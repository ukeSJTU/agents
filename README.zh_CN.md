# agents

> 面向编程智能体的个人可复用 skill 与 plugin。

[English](README.md)

本仓库是 Uke 的智能体资产分发源。将资产安装到兼容的编程智能体后，即可在自己的项目中使用，无需手动复制文件。

## 当前资产

### Skills

| Skill                                      | 适用场景                             | 关键行为                                                        |
| ------------------------------------------ | ------------------------------------ | --------------------------------------------------------------- |
| [`pdf-read`](skills/pdf-read/SKILL.md)     | 阅读、审阅、搜索、总结和比较已有 PDF | 基于 PDF 原生内容提供带页码的依据；绝不修改 PDF，也不使用 OCR。 |
| [`paper-read`](skills/paper-read/SKILL.md) | 深入、可回溯地研读学术论文 PDF       | 必须明确阅读深度，产出含叙事化论文主线的三遍研读记录。          |

### Plugins

目前尚未发布个人 plugin。后续发布的 plugin 会在这里列出，并附上安装说明。

## 安装 skill

推荐使用 [skills CLI](https://github.com/vercel-labs/skills) 安装。它支持 Codex、Claude Code 以及其他兼容的编程智能体。

将 `<skill-name>` 替换为 `pdf-read` 或 `paper-read`，即可为 Codex 全局安装：

```bash
npx skills add ukeSJTU/agents --skill <skill-name> --agent codex --global
```

或为 Claude Code 全局安装：

```bash
npx skills add ukeSJTU/agents --skill <skill-name> --agent claude-code --global
```

省略 `--global`，即可仅在当前项目中安装。安装前若想查看本仓库提供的内容，请运行：

```bash
npx skills add ukeSJTU/agents --list
```

> [!NOTE]
> `pdf-read` 运行时需要在 `PATH` 中提供 [`uv`](https://docs.astral.sh/uv/getting-started/installation/)。它的内置脚本通过 `uv run` 创建隔离环境，不会把 PDF 相关库安装到全局 Python 环境。
>
> `paper-read` 没有额外运行时依赖；需要页级 PDF 依据时，建议同时安装 `pdf-read`。

## 使用 `pdf-read`

安装完成后，直接用自然语言向智能体提出与 PDF 有关的请求。例如：

> 审阅附件中的 PDF，总结其主要论点，并标注对应页码。

该 skill 面向具有可用原生文本层的电子 PDF，可处理文本、表格、图片、图表、公式和需要关注布局的页面；当提取不可靠时，它会说明限制，而非自行猜测。它被刻意设计为只读：不会编辑、合并、批注、填写、签署、加密、绕过解密、优化 PDF，也不会使用 OCR。

## 使用 `paper-read`

请求三遍研读时，必须明确选择 `理解`、`精读` 或 `审读`。例如：

> 为附件中的论文生成研读记录。阅读深度：精读。

生成的记录会先给出连续叙事的“论文主线｜一遍读懂”，再提供可回溯的三遍分析和证据索引。

## 仓库结构

```text
skills/          个人、可分发的智能体 skill
plugins/         个人、可分发的智能体 plugin（目前尚未发布）
skills.sh.json   skills.sh 的目录配置
.agents/         本仓库的开发支持文件
.claude/         本仓库的开发支持文件
```

`.agents/` 和 `.claude/` 用于维护本仓库，并不是上面所述分发资产的来源。
