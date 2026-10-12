# 仓库维护规则

- 本文件是仓库规则的唯一正文；`AGENTS.md` 必须是指向 `CLAUDE.md` 的相对符号链接。
- 六个安装文件是 `SKILL.md`、`agents/openai.yaml` 与 `references/` 下四个 Markdown 文件。
- 使用说明放 README；验证与人工验收放 `docs/maintenance.md`，不要把会话历史追加到规则中。
- 入口的最少提问规则不可退化成完整档案问卷；变更行为时按维护说明验收实际答复。
- 保持通用人群与项目适配，不写入个人骑行／健康档案、原始聊天、绝对本地路径或凭据。
- 区分博主方法、证据结论与教练实施选择；文献 ID 只在 `references/evidence.md` 定义。
- 任何新增研究主张须核实出处与外推限制；静态 CI 通过不代表科学效果已验证。
- 提交前运行 `python scripts/validate_repository.py` 和 `python -m unittest discover -s tests -v`。
- 不凭旧记录声称本次 CI 通过；核对 PR 最新提交的实际检查状态。

维护流程与行为验收见 [docs/maintenance.md](docs/maintenance.md)。
