# 科学骑行训练教练

面向不同性别、水平、FTP、车型与骑行项目的 Agent Skill，帮助制定训练、饮食、补给和恢复方案。有可靠功率数据时按功率与体感判断；无功率计时使用时间、RPE、说话能力和心率趋势，不从速度或模拟功率反推 FTP。

技能融合北理皮加查（董建奇）公开方法的可取思路与运动科学证据，是独立整理的作品，不代表博主本人、官方授权或效果保证。来源摘要、核验深度和适用边界分别见 [方法来源](references/creator-method.md) 与 [证据索引](references/evidence.md)。

## 安装

本仓库根目录就是技能目录。将下列 **6 个文件** 按原目录结构放进 Codex 的技能目录：

```text
~/.codex/skills/evidence-based-cycling-coach/
├── SKILL.md
├── agents/openai.yaml
└── references/
    ├── training.md
    ├── nutrition-recovery.md
    ├── creator-method.md
    └── evidence.md
```

Windows 的 `~` 表示当前用户的主文件夹；设置了 `CODEX_HOME` 时，改用该目录下的 `skills/evidence-based-cycling-coach`。README、docs、scripts、tests 和 CI 配置用于维护仓库，无需一起安装。安装后新开一个会话，让客户端重新发现技能。

## 使用

在支持 Skill 的客户端调用 `$evidence-based-cycling-coach`，说明本次需要解决的问题即可。例如：

- “两小时轻松骑行，骑中怎么补给？”
- “已有最近几周的训练记录，请安排下周三次骑行。”
- “这堂 XCO 技术课结束后前臂很疲劳，下一堂课怎么调整？”

**默认先回答，不先收完整个人档案。** 已知资料直接复用；只有缺口确实会改变本次建议、且不能用范围或公式解决时，才补问最关键的一项，必要时最多两项。体重、FTP、设备型号、是否外卖等不是所有问题的必填项。入口规则以 [SKILL.md](SKILL.md) 为准。

## 文件职责

| 文件 | 职责 |
|---|---|
| [SKILL.md](SKILL.md) | 任务路由、最少提问、关键边界与交付检查 |
| [训练参考](references/training.md) | 测量、单课、负荷、专项与人群适配 |
| [营养与恢复](references/nutrition-recovery.md) | 供能、补水、蛋白、补剂与睡眠 |
| [方法来源](references/creator-method.md) | 博主原方案摘要、改编与来源限制 |
| [证据索引](references/evidence.md) | 32 个来源 ID、链接、核验深度与外推限制 |
| [维护说明](docs/maintenance.md) | 修改流程、本地验证、CI 与人工验收 |

不预存个人骑行或健康档案；不保证固定 FTP 增长。特殊人群、危险症状与具体剂量按技能中的情境规则处理。
