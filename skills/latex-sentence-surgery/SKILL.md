---
name: latex-sentence-surgery
description: 对 LaTeX 论文执行“句子级最小改动（删除/替换）+ 可选四步编译”。触发词：移除这句话、删除这句、替换这句、只改这一句、删句并编译。
---

# LaTeX Sentence Surgery

用于论文定稿阶段的高频小改：精确删句/替句，不扩写、不重构，并按需直接编译 PDF。

## 触发方式

- 「移除这句话」
- 「删除这句并编译 pdf」
- 「替换这句为 ...」
- 「只改这一句」

## 执行脚本

```bash
bash /Users/bit/.codex/skills/latex-sentence-surgery/scripts/main.sh "<file>" remove "<target>"
```

```bash
bash /Users/bit/.codex/skills/latex-sentence-surgery/scripts/main.sh "<file>" replace "<target>" "<replacement>"
```

## 工作流程

1. 确认目标文件与目标句。
2. 执行句子级最小改动：
   - `remove`：删除首次匹配句子；
   - `replace`：替换首次匹配句子。
3. 不自动补充解释句或扩展段落，除非用户明确要求。
4. 若用户要求编译，则执行：
   - `xelatex main && biber main && xelatex main && xelatex main`
5. 输出：修改结果（命中次数/是否成功）+ 编译结果。

## 注意事项

1. 仅做最小改动，不重排段落。
2. 默认只处理首次命中的目标句，避免误改多处重复文本。
3. 未命中时必须返回失败并提示用户确认目标句文本。
