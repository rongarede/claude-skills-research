#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sci-hub-download: 通过 DOI 从多路线下载论文 PDF

三路线优先级：
  路线1 → 开放获取直链（OA，免费最快）
  路线2 → Sci-Hub 镜像（覆盖 2022 年前论文）
  路线3 → 出版商直连（部分 IEEE/Springer 支持）

用法:
  python3 download.py "10.1109/TNNLS.2023.3310935"
  python3 download.py "10.1109/TNNLS.2023.3310935" -o ~/Papers/
  python3 download.py -f dois.txt -o ~/Papers/
  python3 download.py "10.1109/xxx" --mirror sci-hub.st
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("缺少依赖，请运行: pip install requests beautifulsoup4")
    sys.exit(1)

# Sci-Hub 镜像列表（按推荐顺序）
MIRRORS = [
    "https://sci-hub.mksa.top",
    "https://sci-hub.se",
    "https://sci-hub.st",
    "https://sci-hub.ren",
    "https://sci-hub.ru",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 请求超时（秒）
TIMEOUT = 30

# Unpaywall API 邮箱（需使用真实格式邮箱，test@example.com 会被拒绝）
UNPAYWALL_EMAIL = "user@university.edu"


# ─────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────

def sanitize_filename(doi: str) -> str:
    """将 DOI 转为安全文件名"""
    return re.sub(r'[^\w\-.]', '_', doi) + ".pdf"


def is_valid_pdf(data: bytes) -> bool:
    """用魔数校验是否真正是 PDF"""
    return data[:5] == b"%PDF-"


def save_pdf(data: bytes, doi: str, output_dir: Path) -> Path:
    """将 PDF 数据写入磁盘并返回路径"""
    filename = sanitize_filename(doi)
    filepath = output_dir / filename
    filepath.write_bytes(data)
    size_mb = len(data) / (1024 * 1024)
    print(f"    → 已保存 ({size_mb:.1f} MB): {filepath}")
    return filepath


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


# ─────────────────────────────────────────
# 路线1：开放获取直链
# ─────────────────────────────────────────

def _fetch_unpaywall(doi: str, session: requests.Session, timeout: int) -> Optional[str]:
    """查询 Unpaywall API，返回 OA PDF URL（无则返回 None）"""
    api_url = f"https://api.unpaywall.org/v2/{doi}?email={UNPAYWALL_EMAIL}"
    try:
        resp = session.get(api_url, timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()
        best = data.get("best_oa_location") or {}
        return best.get("url_for_pdf")
    except Exception:
        return None


def try_open_access(doi: str, output_dir: Path, session: requests.Session, timeout: int) -> Optional[Path]:
    """
    路线1：开放获取直链。
    按出版商 DOI 前缀快速构造 PDF URL；兜底查询 Unpaywall API。
    成功返回 Path，失败返回 None。
    """
    print("  [路线1] 开放获取直链 ...", end=" ", flush=True)
    candidates = []

    doi_lower = doi.lower()

    # MDPI (10.3390/...)
    if doi_lower.startswith("10.3390/"):
        # www.mdpi.com 有 WAF 拦截，优先用 Crossref 查 ISSN 路径，再构造 mdpi-res.com CDN URL
        try:
            cr_resp = session.get(f"https://api.crossref.org/works/{doi}", timeout=10)
            if cr_resp.status_code == 200:
                cr_msg = cr_resp.json().get("message", {})
                cr_links = cr_msg.get("link", [])
                for link in cr_links:
                    link_url = link.get("URL", "")
                    if "/pdf" in link_url:
                        # 从 www.mdpi.com URL 提取文章路径，构造 CDN URL
                        # 例：https://www.mdpi.com/1424-8220/23/1/1/pdf
                        # → 提取 journal ISSN 路径: 1424-8220/23/1/1
                        import re as _re
                        m = _re.search(r'mdpi\.com/(\d{4}-\d{4})/(\d+)/(\d+)/(\d+)/pdf', link_url)
                        if m:
                            issn, vol, issue, art = m.groups()
                            # 查找 journal 短名（从 Crossref container-title 推断）
                            journal_title = (cr_msg.get("container-title") or [""])[0].lower()
                            # MDPI CDN 格式: mdpi-res.com/d_attachment/{journal}/{journal}-{vol}-{art:05d}/article_deploy/{journal}-{vol}-{art:05d}.pdf
                            # 补零到 5 位
                            art_padded = art.zfill(5)
                            cdn_url = f"https://mdpi-res.com/d_attachment/{journal_title}/{journal_title}-{vol}-{art_padded}/article_deploy/{journal_title}-{vol}-{art_padded}.pdf"
                            candidates.append(cdn_url)
                        # 也保留原始 URL 作为备选
                        candidates.append(link_url)
        except Exception:
            pass

    # IEEE Access (10.1109/ACCESS...)
    if doi_lower.startswith("10.1109/access"):
        # 提取 article number（最后一段数字）
        parts = doi.split(".")
        art_num = parts[-1] if parts[-1].isdigit() else None
        if art_num:
            candidates.append(
                f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={art_num}&ref="
            )

    # PLoS ONE / PLoS journals (10.1371/...)
    if doi_lower.startswith("10.1371/"):
        candidates.append(f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable")

    # Frontiers (10.3389/...)
    if doi_lower.startswith("10.3389/"):
        # Frontiers PDF URL: /journals/{journal}/articles/{doi}/pdf
        # 也尝试旧格式 /articles/{doi}/pdf
        candidates.append(f"https://www.frontiersin.org/journals/neuroscience/articles/{doi}/pdf")
        candidates.append(f"https://www.frontiersin.org/articles/{doi}/pdf")

    # 尝试所有构造的候选 URL
    for url in candidates:
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200 and is_valid_pdf(resp.content):
                print(f"命中 ({url[:60]}...)")
                return save_pdf(resp.content, doi, output_dir)
        except Exception:
            pass

    # 兜底：Unpaywall API
    pdf_url = _fetch_unpaywall(doi, session, timeout)
    if pdf_url:
        try:
            resp = session.get(pdf_url, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200 and is_valid_pdf(resp.content):
                print(f"Unpaywall 命中")
                return save_pdf(resp.content, doi, output_dir)
        except Exception:
            pass

    print("未找到 OA 直链")
    return None


# ─────────────────────────────────────────
# 路线2：Sci-Hub 镜像（保留原有逻辑）
# ─────────────────────────────────────────

def extract_pdf_url(html: str, base_url: str) -> Optional[str]:
    """从 Sci-Hub 页面提取 PDF URL"""
    soup = BeautifulSoup(html, "html.parser")

    # 方式1: embed 标签
    tag = soup.find("embed", id="pdf") or soup.find("embed", {"type": "application/pdf"})
    if tag and tag.get("src"):
        return _normalize_url(tag["src"], base_url)

    # 方式2: iframe 标签
    tag = soup.find("iframe", id="pdf") or soup.find("iframe")
    if tag and tag.get("src"):
        src = tag["src"]
        if src.endswith(".pdf") or "pdf" in src:
            return _normalize_url(src, base_url)

    # 方式3: buttons div 中的链接
    buttons = soup.find("div", id="buttons")
    if buttons:
        a_tag = buttons.find("a", href=True)
        if a_tag:
            return _normalize_url(a_tag["href"], base_url)
        # onclick 中的 URL
        btn = buttons.find("button", onclick=True)
        if btn:
            match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", btn["onclick"])
            if match:
                return _normalize_url(match.group(1), base_url)

    # 方式4: 任何包含 .pdf 的 embed/iframe src
    for tag_name in ["embed", "iframe"]:
        for t in soup.find_all(tag_name, src=True):
            if ".pdf" in t["src"]:
                return _normalize_url(t["src"], base_url)

    return None


def _normalize_url(url: str, base_url: str) -> str:
    """处理协议相对 URL 和相对路径"""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return urljoin(base_url, url)
    if not url.startswith("http"):
        return urljoin(base_url, url)
    return url


def try_scihub(doi: str, output_dir: Path, session: requests.Session,
               mirror: Optional[str], timeout: int) -> Optional[Path]:
    """
    路线2：Sci-Hub 镜像轮询。
    成功返回 Path，失败返回 None。
    """
    mirrors = [mirror] if mirror else MIRRORS
    print("  [路线2] Sci-Hub 镜像 ...")

    for m in mirrors:
        url = f"{m}/{doi}"
        print(f"    尝试 {m} ...", end=" ", flush=True)
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code}")
                continue

            # 直接返回了 PDF
            content_type = resp.headers.get("Content-Type", "")
            if "application/pdf" in content_type:
                pdf_data = resp.content
            else:
                pdf_url = extract_pdf_url(resp.text, m)
                if not pdf_url:
                    print("未找到 PDF 链接")
                    continue

                print(f"PDF → {pdf_url[:60]}...")
                pdf_resp = session.get(pdf_url, timeout=timeout)
                if pdf_resp.status_code != 200:
                    print(f"PDF 下载失败: HTTP {pdf_resp.status_code}")
                    continue
                pdf_data = pdf_resp.content

            if not is_valid_pdf(pdf_data):
                print("返回内容非 PDF")
                continue

            print(f"    → 命中 {m}")
            return save_pdf(pdf_data, doi, output_dir)

        except requests.exceptions.Timeout:
            print("超时")
        except requests.exceptions.ConnectionError:
            print("连接失败")
        except Exception as e:
            print(f"错误: {e}")

    print("  [路线2] 所有 Sci-Hub 镜像均失败")
    return None


# ─────────────────────────────────────────
# 路线3：出版商直连
# ─────────────────────────────────────────

def try_publisher_direct(doi: str, output_dir: Path, session: requests.Session, timeout: int) -> Optional[Path]:
    """
    路线3：出版商直连尝试。
    支持 IEEE Xplore 和 Springer Open Access。
    成功返回 Path，失败返回 None。
    """
    print("  [路线3] 出版商直连 ...", end=" ", flush=True)
    doi_lower = doi.lower()
    candidates = []

    # IEEE Xplore：从 DOI 末尾数字段解析 article number
    if doi_lower.startswith("10.1109/"):
        parts = doi.split(".")
        art_num = parts[-1] if parts[-1].isdigit() else None
        if art_num:
            candidates.append(
                f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={art_num}&ref="
            )

    # Springer Open Access PDF
    if doi_lower.startswith("10.1007/") or doi_lower.startswith("10.1186/"):
        candidates.append(f"https://link.springer.com/content/pdf/{doi}.pdf")

    # Elsevier / ScienceDirect（部分 OA 文章）
    if doi_lower.startswith("10.1016/"):
        # 尝试 ScienceDirect PDF 直链
        article_id = doi.replace("10.1016/", "").replace("/", "-")
        candidates.append(f"https://www.sciencedirect.com/science/article/pii/{article_id}/pdfft?isDTMRedir=true&download=true")

    for url in candidates:
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200 and is_valid_pdf(resp.content):
                print(f"命中 ({url[:60]}...)")
                return save_pdf(resp.content, doi, output_dir)
        except Exception:
            pass

    print("无直连可用")
    return None


# ─────────────────────────────────────────
# 主下载入口
# ─────────────────────────────────────────

def download_paper(doi: str, output_dir: Path, mirror: Optional[str] = None, timeout: int = TIMEOUT) -> bool:
    """
    三路线组合下载单篇论文，返回是否成功。

    路线1 → OA 直链（最快）
    路线2 → Sci-Hub 镜像（覆盖面广）
    路线3 → 出版商直连（兜底）
    """
    session = make_session()

    # 路线1: 开放获取直链
    result = try_open_access(doi, output_dir, session, timeout)
    if result:
        print(f"  [OK] 路线1(OA) 成功: {doi}")
        return True

    # 路线2: Sci-Hub（保留原有逻辑，mirror 参数仍有效）
    result = try_scihub(doi, output_dir, session, mirror, timeout)
    if result:
        print(f"  [OK] 路线2(Sci-Hub) 成功: {doi}")
        return True

    # 路线3: 出版商直连
    result = try_publisher_direct(doi, output_dir, session, timeout)
    if result:
        print(f"  [OK] 路线3(出版商) 成功: {doi}")
        return True

    print(f"  [FAIL] 三路线均失败: {doi}")
    print(f"  提示：可尝试手动访问 https://sci-hub.se/{doi} 或联系图书馆获取")
    return False


# ─────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="通过 DOI 从多路线下载论文 PDF（OA 直链 → Sci-Hub → 出版商）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "10.1109/TNNLS.2023.3310935"
  %(prog)s "10.1109/TNNLS.2023.3310935" -o ~/Papers/
  %(prog)s -f dois.txt -o ~/Papers/
  %(prog)s "10.1109/xxx" --mirror sci-hub.st
        """,
    )
    parser.add_argument("doi", nargs="?", help="论文 DOI")
    parser.add_argument("-f", "--file", help="DOI 列表文件（每行一个 DOI）")
    parser.add_argument("-o", "--output", default=".", help="输出目录（默认当前目录）")
    parser.add_argument("--mirror", help="指定 Sci-Hub 镜像域名（路线2专用）")
    parser.add_argument("--timeout", type=int, default=30, help="请求超时秒数（默认 30）")
    args = parser.parse_args()

    if not args.doi and not args.file:
        parser.error("请提供 DOI 或使用 -f 指定 DOI 列表文件")

    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 收集 DOI 列表
    dois = []
    if args.doi:
        dois.append(args.doi.strip())
    if args.file:
        file_path = Path(args.file).expanduser()
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            sys.exit(1)
        dois.extend(
            line.strip()
            for line in file_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )

    if not dois:
        print("没有要下载的 DOI")
        sys.exit(1)

    print(f"共 {len(dois)} 篇论文，输出目录: {output_dir}\n")

    success = 0
    failed = []
    for i, doi in enumerate(dois, 1):
        print(f"[{i}/{len(dois)}] {doi}")
        if download_paper(doi, output_dir, args.mirror, args.timeout):
            success += 1
        else:
            failed.append(doi)
        # 批量下载时间隔，避免被封
        if len(dois) > 1 and i < len(dois):
            time.sleep(2)

    print(f"\n完成: {success}/{len(dois)} 成功")
    if failed:
        print("失败列表:")
        for d in failed:
            print(f"  - {d}")
        sys.exit(1)


if __name__ == "__main__":
    main()
