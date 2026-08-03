# Foyofun Skills

可复用的 AI Skill 集合——涵盖创意写作与游戏客户端开发两大领域。每个 skill 是一个独立目录，将 `SKILL.md` 作为系统提示词提供给 AI 即可使用。

---

## 🎮 编码开发 Skills（UE4+Lua 游戏客户端）

专为大型 UE4+Lua 游戏项目设计的编码 Skill 体系，按四层架构组织：

### 架构总览

```
用户请求
    │
    ├─ 调研 ──→ research（Layer 0：调研缓存，避免重复搜索）
    │
    ├─ 检索 ──→ api-registry / experience-repo / module-style（Layer 1：只读检索）
    │
    ├─ 输出 ──→ plan-output / change-review（Layer 2：方案输出 & 代码审查）
    │
    └─ 执行 ──→ logic-dev / ui-dev / code-refactor / quick-fix（Layer 3：面向用户）
```

### Layer 0：调研基础

| Skill | 说明 | 触发词 |
|-------|------|--------|
| `research` | 项目代码调研，缓存+Git 失效检查，f/g/h/i 的强制前置步骤 | 调研、研究一下、看看现有代码、先看看、摸底 |

### Layer 1：检索 & 知识库

| Skill | 说明 | 触发词 |
|-------|------|--------|
| `api-registry` | API 注册表——保存和检索项目封装接口，避免 AI 使用标准库而非项目封装 | 查接口、有没有封装、怎么调用、收录接口 |
| `experience-repo` | 经验库——正反例对比记录编码偏好，支持读写双向 | 记住、记一下、以后这样写、不要这样写 |
| `module-style` | 模块风格分析——在已有模块上开发时先分析其编码习惯 | 内部调用，分析这个模块的风格 |

### Layer 2：输出 & 质检

| Skill | 说明 | 触发词 |
|-------|------|--------|
| `plan-output` | 方案输出模板——为 logic-dev/ui-dev/code-refactor 提供统一的 Plan 格式 | 内部引用 |
| `change-review` | 代码审查——只审 git diff，关注阻塞项/逻辑错误/日志/API 选择 | review、审查代码、检查一下、code review |

### Layer 3：执行（面向用户）

| Skill | 说明 | 触发词 |
|-------|------|--------|
| `logic-dev` | 业务逻辑层开发——数据流、数据处理、协议、接口设计、时序控制 | 开发 logic、实现功能、写一个模块、数据管理 |
| `ui-dev` | UI 界面开发——控件绑定、交互逻辑、数据刷新、异步防御 | 做界面、写 UI、UIBP、弹窗、按钮、列表项 |
| `code-refactor` | 代码重构——改结构不改行为，多方案选择+经验驱动 | 重构、整理代码、优化结构、拆分、职责不清 |
| `quick-fix` | 快速修复——≤30 行小改动，TODO 清理、小 bug 修复、日志补充 | 修复、改一下、TODO 做一下、这里有个小问题 |

### 设计原则

- **职责单一**：每个 Skill 只做一件事，logic-dev 不写 UI，ui-dev 不处理业务规则
- **数据与 Skill 分离**：Skill 文件是通用指令（可上传 GitHub），API 注册表/经验库/调研缓存等数据存储在项目的 `.record/` 目录下
- **正反例替代抽象描述**：经验库用 `✅ 推荐` / `❌ 不推荐` 的代码示例而非抽象规则
- **默认在现有接口中修改**：如非必要勿增实体，新增接口需要满足明确条件
- **调研缓存**：TTL + Git 变更双重失效检查，避免重复搜索浪费 token
- **索引路由**：`_flat_index → _toc → 分段 Read` 的三层检索策略，大幅节省 token

### 使用方式

将对应 skill 目录放入 AI 工具的 skills 路径下即可。Skill 文件使用 `${PROJECT_LUA_DIR}`、`${CLAUDE_PLUGIN_ROOT}` 等环境变量引用路径，不依赖特定项目目录结构。

---

## ✍️ 创意写作 Skills

| Skill | 说明 |
|-------|------|
| `oc-creation-assistant` | 引导用户一步步创作原创角色（OC）。从零开始或基于碎片想法，通过问答构建角色设定、性格、背景故事 |
| `sillytavern-character-card` | 将角色设定转化为 SillyTavern 格式的角色卡（Character Card），生成可导入 ST 的 JSON/PNG 文件 |
| `sillytavern-prompt-generator` | 创建完整的 SillyTavern 预设（Prompt/Preset），调整 AI 回复风格、长度、温度等参数 |
| `story-outline-assistant` | 引导用户在缺乏灵感时完成故事大纲创作，梳理碎片想法、发展情节、发现故事核心意义 |

---

## 许可

MIT © 2026 foyofun
