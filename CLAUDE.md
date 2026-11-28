# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 这是什么

技能目录，不是应用程序。没有构建、lint、测试，也没有仓库级 `package.json`。每个技能是一个目录，里面必须有 `SKILL.md`。人读 `README.md`，浏览器用根目录的 `index.html`。这三处必须是同一批名字。

## 目录

六个分类目录。编号就是 `index.html` 里 `CATS` 的下标，加技能时 DATA 第三列用这个数：

| 下标 | 目录 |
|---|---|
| 0 | `01-写作与内容` |
| 1 | `02-商业思维` |
| 2 | `03-提示词与AI` |
| 3 | `04-效率工具` |
| 4 | `05-视觉与设计` |
| 5 | `06-发布与平台` |

`AI分身迁移包/` 不是技能，不要算进总数，也不要给它补 `SKILL.md`。它的 README 会指示 agent 覆盖用户的 `~/.claude/CLAUDE.md` 和 `telos/`。除非用户明确说要安装这套分身，不要执行里面的复制。

技能目录内部的 `CLAUDE.md`（例如 `06-发布与平台/小红书留学求职ip号帖子改编/`）只约束那个技能，不是本仓库的规则。

`.claude/` 在 `.gitignore` 里，本地 worktree 放这里。不要提交。

## 一个技能是什么

```
<分类>/<目录名>/
  SKILL.md       必需。文件第一行必须是 ---
  references/    按需才读的文档，不要整段塞进 SKILL.md
  scripts/       只属于这个技能，不是仓库级工具
  assets/ templates/ rules/ workflow/   按该技能自己的需要
```

Frontmatter 至少要有 `name` 和 `description`。启用与否只看 `description`，要写清什么时候用，不要只写一句口号。

目录名和 `name` 经常不是同一个字符串。中文目录配英文 `name` 是常态，例如目录 `投流帖改写` 的 name 是 `ad-post-rewrite`，`NanoBanana-PPT-Skills` 的 name 是 `ppt-generator-pro`。

- README 链接、`index.html` 的 DATA 第一列、GitHub 路径：用**目录名**
- 斜杠命令和技能触发：用 frontmatter 的 **`name`**
- 不要为了统一去改其中一边。改目录会断 README 和 index 的链接；改 `name` 会换掉已经装过的用户的命令名

`02-商业思维/interpersonal-reflection-coach/SKILL.md` 是 GBK，不是 UTF-8。改这个文件不能按 UTF-8 写回，否则中文坏掉。其余 `SKILL.md` 按 UTF-8。

上游整包拷进来的技能（`docx`、`pdf`、`pptx`、`baoyu-*`、`office-hours`、`NanoBanana-PPT-Skills` 等）保持原结构。不要重排成上面的模板。`baoyu-danger-*` 走的是非官方接口，不要扩大它们的抓取范围。

## 改目录时三处一起动

没有生成脚本。`README.md` 和 `index.html` 是手改的。添加或改名一个技能，三处一起动：

1. `<分类>/<目录名>/SKILL.md`（以及它自己的 references/scripts）
2. `README.md`：对应分类加一条 `- [目录名](./分类/目录名) — 一句说明`，改该分类标题里的个数，改开头的总数
3. `index.html` 的 `DATA` 加一行：`["目录名", "一句说明", 分类下标]`。第一列必须是目录名，页面用它拼 GitHub 链接

`.gitignore` 写了 `index.html` 和 `LICENSE`，但这两个文件已经被跟踪。改 `index.html` 仍然要提交。不要因为它出现在 gitignore 里就跳过，也不要 `git rm --cached`。`.gitignore` 自身和 `.claude/` 不入库。

`index.html` 里的 `REPO` 和页头链接指向 `https://github.com/wangruiyu070802/all-skills`。本克隆的 `origin` 是 `TylerRay782/all-skills`。不要擅自改这个常量。

## 安装路径

给人用时以 README 为准：把技能目录拷到 `~/.claude/skills/`。

仓库里有两套路径，不要互相改：

- README 和多数技能正文写 `~/.claude/skills/`
- `index.html` 页脚和 `skill-creator` 写 `~/.newmax/skills/`，那是另一套客户端的扫描目录

在本仓库新增技能时，不要执行 skill-creator 里「必须创建在 `~/.newmax/skills/`」那条。技能源文件放在对应的 `0N-分类/` 下。技能正文里硬编码的 `~/.claude/skills/<name>/` 是安装之后的路径，不要在目录仓库里为了能跑去改，除非用户正在那个已安装副本里工作。

## 核对

没有 build / lint / test。改完目录，数量应等于 README 开头的总数，也等于 `index.html` 里 `DATA` 的行数，分类下标对得上该目录所在的 `0N-` 文件夹。

```powershell
(git ls-files "*SKILL.md").Count
```

技能自带的 `scripts/*.py`、`scripts/*.mjs` 只在该技能被调用时运行。不要在仓库根加依赖清单或统一测试。
