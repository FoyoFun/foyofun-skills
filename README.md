# Claude Skills

个人 Claude Code 技能集合。每个技能是一个可复用的指令模板，通过 `/skill-name` 在对话中触发。

## 技能清单

### oc-creation-assistant
引导用户一步步创作原创角色（OC）。从零开始或基于碎片想法，通过问答帮助用户构建角色设定、性格、背景故事，让角色更丰满立体。
```
/oc-creation-assistant
```

### sillytavern-character-card
引导用户将角色设定转化为 SillyTavern 格式的角色卡（Character Card），生成可直接导入 ST 的 JSON/PNG 文件。
```
/sillytavern-character-card
```

### sillytavern-prompt-generator
引导用户创建完整的 SillyTavern 预设（Prompt/Preset）。涵盖角色扮演、跑团、纯闲聊等多种场景，可调整 AI 的回复风格、长度、温度等参数。
```
/sillytavern-prompt-generator
```

### story-outline-assistant
引导用户在缺乏灵感时完成故事大纲创作。帮助梳理碎片想法、发展情节、发现故事的核心意义。
```
/story-outline-assistant
```

## 忽略的目录

以下目录保留在本地但**不受版本控制**：

| 目录 | 说明 |
|------|------|
| `skill-creator/` | 第三方 skill，非本人创作 |
| `oc-creation-assistant-workspace/` | OC 创作助手的评测/工作数据 |

## 使用方式

在 Claude Code 对话中直接输入 `/<skill-name>` 调用。

## 许可

MIT © 2026 foyofun
