---
name: xiaohongshu-persona-writer
description: 当用户提到"ip帖改编"、"ip帖创作"、"生成素人文"、"写小红书"、"小红书素人帖"、"素人账号内容"、"留学求职素人文"、"生成素人帖"、"换皮仿写"、"初始化项目"、"开始迭代"时触发。基于人设和参考文章进行换皮仿写，生成留学求职赛道小红书素人文，支持版本迭代和持续优化。
---

# 小红书素人文智能体迭代工程

通过人机协作，以文件夹作为"外部记忆"，持续迭代优化一个能写出高质量**留学求职赛道小红书素人文**的智能体 System Prompt。

---

## 📁 文件夹结构

| 路径 | 用途 |
|------|------|
| `0_personas/` | 人设库，存放不同账号的人设定义 |
| `1_prompts/v{n}.md` | 第 n 版 System Prompt |
| `2_outputs/v{n}_output_xx.md` | 第 n 版 prompt 生成的产出 |
| `3_feedback/v{n}_feedback.md` | 人类对第 n 版产出的反馈 |
| `4_examples/` | 范例库（好范例和差范例） |
| `golden_rules.md` | 从所有反馈中提炼的永久性规则 |

---

## 🎯 核心 Skills

### Skill 1：初始化项目

**触发词**：`初始化项目`

详见 [workflow/skill1-init.md](workflow/skill1-init.md)

---

### Skill 2：生成产出

**触发词**：`生成产出` / `写一篇素人文`

详见 [workflow/skill2-generate.md](workflow/skill2-generate.md)

**核心流程**：
1. 读取最新版 prompt
2. 选择人设
3. 提供参考文章
4. 换皮仿写
5. 保存产出和反馈模板

---

### Skill 3：开始迭代

**触发词**：`开始迭代` / `根据反馈迭代`

详见 [workflow/skill3-iterate.md](workflow/skill3-iterate.md)

**两阶段流程**：
1. **评估阶段**：判断是否可以迭代
2. **执行阶段**：学习规则 → 重构 prompt → 生成新版产出

---

### Skill 4：查看状态

**触发词**：`当前状态` / `汇报进度`

详见 [workflow/skill4-status.md](workflow/skill4-status.md)

---

### Skill 5：添加人设

**触发词**：`添加人设` / `新建人设`

详见 [workflow/skill5-add-persona.md](workflow/skill5-add-persona.md)

---

### Skill 6：查看人设

**触发词**：`查看人设` / `人设列表`

详见 [workflow/skill6-view-personas.md](workflow/skill6-view-personas.md)

---

### Skill 7：添加范例

**触发词**：`添加好范例` / `添加差范例`

详见 [workflow/skill7-add-example.md](workflow/skill7-add-example.md)

---

## 📚 模板库

- **人设模板** → [templates/persona-template.md](templates/persona-template.md)
- **反馈模板** → [templates/feedback-template.md](templates/feedback-template.md)
- **产出模板** → [templates/output-template.md](templates/output-template.md)

---

## 📐 工作流规则

详见 [rules/workflow-rules.md](rules/workflow-rules.md)

**核心约束**：
- 严格遵守定义的 Skill 和动作
- 所有文件操作在当前工作目录下进行
- 禁止删除任何历史版本文件
- "开始迭代" 必须先评估、获得确认后才能执行

---

## 🔄 工作流循环

```
初始化项目 → 生成产出 → 填写反馈 → 开始迭代 → 填写反馈 → ...
```

详见 [rules/workflow-rules.md](rules/workflow-rules.md)
