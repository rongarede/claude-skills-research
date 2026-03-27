#!/usr/bin/env python3
"""
Semantic Scholar API 异步客户端
支持并发搜索、批量查询、速率控制、磁盘缓存、配置文件
"""

import asyncio
import hashlib
import json
import os
import ssl
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

BASE_URL = "https://api.semanticscholar.org/graph/v1"
AI4SCHOLAR_URL = "https://ai4scholar.net/graph/v1"
CONFIG_DIR = Path.home() / ".config" / "semantic-scholar"
CACHE_DIR = CONFIG_DIR / "cache"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_TTL = 3600  # 缓存有效期（秒）

# 默认返回字段
DEFAULT_FIELDS = "title,authors,year,citationCount,externalIds,venue"
DETAIL_FIELDS = (
    "title,authors,year,citationCount,externalIds,venue,"
    "abstract,referenceCount,isOpenAccess,openAccessPdf"
)


# ── 配置管理 ──

def load_config() -> Dict:
    """从配置文件加载设置"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_config(cfg: Dict):
    """保存设置到配置文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def resolve_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    """Key 解析链：显式传入 → 环境变量 → 配置文件"""
    if explicit_key:
        return explicit_key
    env_key = os.environ.get("S2_API_KEY")
    if env_key:
        return env_key
    return load_config().get("api_key")


# ── 磁盘缓存 ──

class DiskCache:
    """简单的 JSON 磁盘缓存，按查询 hash 存储"""

    def __init__(self, ttl: int = CACHE_TTL, enabled: bool = True):
        self.ttl = ttl
        self.enabled = enabled
        if enabled:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _key(self, namespace: str, params: Dict) -> str:
        """生成缓存文件名（SHA256 前 16 位）"""
        raw = json.dumps({"ns": namespace, **params}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, namespace: str, params: Dict) -> Optional[Any]:
        """读取缓存，返回 None 表示未命中或已过期"""
        if not self.enabled:
            return None
        path = CACHE_DIR / f"{self._key(namespace, params)}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if time.time() - data.get("_ts", 0) > self.ttl:
                path.unlink(missing_ok=True)
                return None
            return data.get("payload")
        except (json.JSONDecodeError, OSError):
            return None

    def put(self, namespace: str, params: Dict, payload: Any):
        """将结果写入磁盘缓存"""
        if not self.enabled:
            return
        path = CACHE_DIR / f"{self._key(namespace, params)}.json"
        try:
            path.write_text(json.dumps(
                {"_ts": time.time(), "payload": payload},
                ensure_ascii=False,
            ), encoding="utf-8")
        except OSError:
            pass

    def clear(self):
        """清除所有缓存"""
        if CACHE_DIR.exists():
            for f in CACHE_DIR.glob("*.json"):
                f.unlink(missing_ok=True)


# ── 速率限制 ──

@dataclass
class RateLimiter:
    """令牌桶速率限制器（协程安全）"""
    rate: float = 1.0
    _tokens: float = 1.0
    _last_refill: float = field(default_factory=time.monotonic)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def acquire(self):
        """获取一个令牌，必要时等待至令牌可用"""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self.rate, self._tokens + elapsed * self.rate)
            self._last_refill = now
            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self.rate
                await asyncio.sleep(wait)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0


# ── 客户端 ──

class S2Client:  # pylint: disable=too-many-instance-attributes
    """Semantic Scholar 异步 API 客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        trust_env: bool = True,
        cache: bool = True,
        max_concurrent: int = 5,
    ):
        self.api_key = resolve_api_key(api_key)
        self.trust_env = trust_env
        self.cache = DiskCache(enabled=cache)
        # 并发信号量：防止瞬间打满速率
        self._sem = asyncio.Semaphore(max_concurrent)
        # 判断是否使用 ai4scholar 代理
        self.base_url = BASE_URL
        self._auth_mode = "x-api-key"
        if self.api_key and self.api_key.startswith("sk-user-"):
            self.base_url = AI4SCHOLAR_URL
            self._auth_mode = "bearer"
        # 有 key 10 req/s，无 key 1 req/s
        rate = 9.0 if self.api_key else 0.9
        self.limiter = RateLimiter(rate=rate)
        self._session: Optional[aiohttp.ClientSession] = None
        # 启动信息
        if not self.api_key:
            apply_url = ("https://www.semanticscholar.org"
                         "/product/api#api-key-form")
            print(
                "[S2] 未检测到 API Key，速率限制为 1 req/s\n"
                "    配置方式：\n"
                "    1) export S2_API_KEY=\"your-key\"\n"
                "    2) 写入 ~/.config/"
                "semantic-scholar/config.json\n"
                f"    申请: {apply_url}",
                file=sys.stderr,
            )
        else:
            mode = ("ai4scholar.net"
                    if self._auth_mode == "bearer"
                    else "官方 API")
            print(f"[S2] 已加载 Key ({mode}，10 req/s)",
                  file=sys.stderr)

    def _headers(self) -> Dict[str, str]:
        """构建请求头（含认证信息）"""
        h = {"Accept": "application/json"}
        if self.api_key:
            if self._auth_mode == "bearer":
                h["Authorization"] = f"Bearer {self.api_key}"
            else:
                h["x-api-key"] = self.api_key
        return h

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 aiohttp 会话（懒初始化）"""
        if self._session is None or self._session.closed:
            ssl_ctx = ssl.create_default_context()
            # macOS Python 常见 CA 证书问题，始终放宽 SSL 验证
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_ctx)
            self._session = aiohttp.ClientSession(
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=30),
                connector=connector,
                trust_env=self.trust_env,
            )
        return self._session

    async def close(self):
        """关闭 HTTP 会话，释放连接资源"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(  # pylint: disable=too-many-arguments
        self, method: str, url: str, *,
        params: Optional[Dict] = None,
        json_body: Optional[Any] = None,
        retries: int = 3,
    ) -> Any:
        """带信号量 + 速率控制 + 重试的请求"""
        async with self._sem:
            session = await self._get_session()
            for attempt in range(retries):
                await self.limiter.acquire()
                try:
                    if method == "GET":
                        resp = await session.get(url, params=params)
                    else:
                        resp = await session.post(
                            url, params=params,
                            json=json_body,
                        )

                    if resp.status == 200:
                        return await resp.json()
                    if resp.status == 429:
                        wait = 2 ** (attempt + 1)
                        print(f"[S2] 429 限流，等待 {wait}s 后重试", file=sys.stderr)
                        await asyncio.sleep(wait)
                        continue
                    text = await resp.text()
                    print(
                        f"[S2] HTTP {resp.status}: "
                        f"{text[:200]}",
                        file=sys.stderr,
                    )
                    if attempt < retries - 1:
                        await asyncio.sleep(1)
                    continue
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    print(f"[S2] 请求异常: {e}", file=sys.stderr)
                    if attempt < retries - 1:
                        await asyncio.sleep(1)
                    continue
            return None

    # ── 搜索 ──

    async def search(  # pylint: disable=too-many-arguments
        self, query: str, *,
        fields: str = DEFAULT_FIELDS,
        limit: int = 10,
        offset: int = 0,
        year: Optional[str] = None,
        venue: Optional[str] = None,
        open_access: Optional[bool] = None,
        min_citation_count: Optional[int] = None,
    ) -> Dict:
        """搜索论文（单次，最多 100 条）"""
        params: Dict[str, Any] = {
            "query": query, "fields": fields,
            "limit": min(limit, 100), "offset": offset,
        }
        for key, val in [("year", year), ("venue", venue)]:
            if val:
                params[key] = val
        if open_access is not None:
            params["openAccessPdf"] = "" if open_access else None
        if min_citation_count is not None:
            params["minCitationCount"] = str(min_citation_count)

        cached = self.cache.get("search", params)
        if cached is not None:
            print(f"[S2] 缓存命中: {query}", file=sys.stderr)
            return cached

        url = f"{self.base_url}/paper/search"
        result = await self._request(
            "GET", url, params=params,
        )
        result = result or {"total": 0, "data": []}
        self.cache.put("search", params, result)
        return result

    async def search_concurrent(
        self, queries: List[str],
        fields: str = DEFAULT_FIELDS,
        limit: int = 10,
        **kwargs,
    ) -> Dict[str, Dict]:
        """并发搜索多个关键词（信号量控制并发度）"""
        tasks = [
            self.search(q, fields=fields, limit=limit, **kwargs)
            for q in queries
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        output = {}
        for q, r in zip(queries, results):
            if isinstance(r, Exception):
                print(f"[S2] 查询 '{q}' 失败: {r}", file=sys.stderr)
                output[q] = {"total": 0, "data": [], "error": str(r)}
            else:
                output[q] = r
        return output

    # ── 批量查询 ──

    async def batch_papers(
        self, paper_ids: List[str],
        fields: str = DEFAULT_FIELDS,
    ) -> List[Optional[Dict]]:
        """批量查询论文详情（自动分批，每批 500）"""
        all_results = []
        for i in range(0, len(paper_ids), 500):
            batch = paper_ids[i:i + 500]
            result = await self._request(
                "POST", f"{self.base_url}/paper/batch",
                params={"fields": fields},
                json_body={"ids": batch},
            )
            if result:
                all_results.extend(result)
            else:
                all_results.extend([None] * len(batch))
        return all_results

    # ── 单篇详情 ──

    async def paper_detail(
        self, paper_id: str,
        fields: str = DETAIL_FIELDS,
    ) -> Optional[Dict]:
        """获取单篇论文详情"""
        return await self._request(
            "GET", f"{self.base_url}/paper/{paper_id}",
            params={"fields": fields},
        )

    # ── 批量搜索（大规模） ──

    async def bulk_search(  # pylint: disable=too-many-arguments
        self, query: str, *,
        fields: str = DEFAULT_FIELDS,
        limit: int = 100,
        year: Optional[str] = None,
        min_citation_count: Optional[int] = None,
    ) -> List[Dict]:
        """批量搜索（token 分页，适合大规模检索）"""
        params: Dict[str, Any] = {"query": query, "fields": fields}
        if year:
            params["year"] = year
        if min_citation_count is not None:
            params["minCitationCount"] = str(min_citation_count)

        all_data: List[Dict] = []
        token = None
        bulk_url = f"{self.base_url}/paper/search/bulk"
        while len(all_data) < limit:
            p = {**params, **({"token": token} if token else {})}
            result = await self._request("GET", bulk_url, params=p)
            if not result or not result.get("data"):
                break
            all_data.extend(result["data"])
            token = result.get("token")
            if not token:
                break
        return all_data[:limit]
