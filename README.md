# foyofun-code-* 编码技能集

个人技能集：主体是 foyofun-code-* 编码工作流，文末附其他技能。
`foyofun` = 开发者，`code` = 用途分类。
设计目标：**通用思想，语言无关**（任意语言/引擎均适用），
项目相关细节全部收敛到每个项目的适配表里。

## 技能清单与调用关系

```
                      ┌─────────────────────────────────────────┐
                      │            执行者（入口）                 │
                      │                                         │
 用户诉求 ──────────▶ │  logic    ui    integrate   refactor    │ ──▶ review（收尾自检）
                      │                                      ✅  │      ▲（也可独立调用）
                      └───────┬──────────────────┬─────────────────┘
                              │ 按阶段调用        │ 集成消费
                              ▼                  ▼
                      ┌─────────────────────────────────────────┐
                      │                支撑件                    │
                      │                                         │
                      │  research  style  experience  api       │
                      │  （调研）  （风格） （经验库）  （API查询）│
                      │                                         │
                      │  plan（方案模板）  stub（骨架+标记规范）   │
                      └─────────────────────────────────────────┘
```

| 技能 | 角色 | 一句话职责 |
|------|------|-----------|
| foyofun-code-research | 支撑 | 调研已有功能与数据源，项目首次使用时初始化 .agents 基础设施 |
| foyofun-code-style | 支撑 | 已有模块的风格提取，让新代码入乡随俗 |
| foyofun-code-experience | 支撑 | 正反例经验库（个人/项目两层），记录用户编码偏好 |
| foyofun-code-api | 支撑 | 项目 API 查询与积累，禁止绕过项目封装 |
| foyofun-code-plan | 支撑 | 方案模板：数据源/时序/新增逻辑/不确定点（禁止猜测） |
| foyofun-code-stub | 支撑 | 骨架生成（自足性标准）+ `[SEAM]`/`[MOCK]`/`[TODO]` 标记规范 |
| foyofun-code-logic | 执行 | logic 层开发，假数据闭环自测 |
| foyofun-code-ui | 执行 | ui 层开发，内部交互闭环自测 |
| foyofun-code-integrate | 执行 | ui/logic 集成装配，只增不改 |
| foyofun-code-refactor | 执行 | 行为不变的结构优化 |
| foyofun-code-review | 执行 | diff 审查四维度，可独立调用 |

## 核心思想（贯穿全套）

1. **反投机**——不预埋接口、不过早缓存、不提前抽象、不做储备性调研
2. **闭环先行**——ui/logic 各自独立闭环开发，假数据自测；集成期只增不改
3. **契约显式化**——跨层对接 = 快照形状 + 意图清单 + 事件清单 + 时序归属
4. **不猜测**——不确定点列出来等用户回答，方案里的每个事实都来自调研
5. **人机共读**——经验库、API 积累、适配表全是 .md，用户随时直接编辑
6. **注册注销成对、异步必须防御**——无论框架是否兜底

## 三种标记（stub 定义，全体系通用）

| 标记 | 含义 | 消除时机 |
|------|------|---------|
| `-- TODO:` | 实现步骤 | 实现完成 |
| `-- [SEAM]` | 跨层契约桩 | integrate 填充/绑定后 |
| `-- [MOCK]` | 闭环假数据点 | integrate 换真源后 |

## 新项目接入（约 5 分钟）

1. 在项目里随便发起一次编码任务（或直接说"调研一下 XX"），
   research 会自动创建 `<project>/.agents/` 并生成下面三样骨架
2. 填写**项目适配表**（模板见下），这是唯一必须人工做的步骤
3. 可选：把已知的项目 API 收录进 `api/`，把已知偏好记入 `experiences/`
   （也可以不预填，用着让 skill 逐步积累）

## 项目适配表模板（`<project>/.agents/adaptation.md`）

```markdown
# 项目适配表
> 所有 foyofun-code-* skill 执行前都会参考本表。框架差异都写在这里，skill 正文保持通用。

## 基本信息
- 语言/引擎：
- 源码根目录：

## UI 框架
- 生命周期方法（对应 ctor/初始化/注册/OnShow/OnClose 的真实方法名）：
- 控件获取与绑定方式：
- 事件注册/注销 API：
- **注销是否框架兜底**（不兜底 = 必须手写成对注销）：
- 定时器 API：

## logic 层
- 模块管理器（获取其他模块的方式）：
- 协议发送/接收惯例（命名风格、handler 形态）：
- 事件系统 API（PostEvent/RegisterEvent 的真实形态）：

## 日志
- 日志函数与格式：

## 已知项目封装分类（供 foyofun-code-api 定向查询）
- 如：TimeUtil（时间）、StringUtil（字符串）、...

## 其他
- 配置表读取方式：
- 特殊约束：
```

## 模型分层使用建议

- **Pro 级模型**：出 Plan（plan）和骨架（stub）——这两个阶段做决策、需要调研整合能力
- **Flash 级模型**：照骨架填实现——stub 的自足性标准保证弱模型无需调研即可翻译注释为代码
- 切换方式：骨架确认后换模型，指其"按 foyofun-code-logic/ui 的骨架逐条 TODO 实现"

## 数据文件总览

| 位置 | 内容 |
|------|------|
| `~/.agents/skills/foyofun-code-*/` | 技能本体（跨工具共享：ZCode / Claude Code） |
| `~/.agents/experiences/` | 个人经验（跨项目通用审美） |
| `<project>/.agents/adaptation.md` | 项目适配表 |
| `<project>/.agents/experiences/` | 项目经验 |
| `<project>/.agents/api/` | 项目 API 积累 |

## 其他技能

| 技能 | 一句话职责 |
|------|-----------|
| foyofun-qq-st-character-card | 角色卡创作引导：为 qq-st-bridge 桥接系统（NoneBot QQ 机器人 + SillyTavern 无头后端）对话式创建可直接部署的 chara_card_v3 角色卡（JSON + 人读 .md + 兴趣关键词 + 头像提醒）；铁律是示例对话必须为纯文字聊天记录体，零动作、零心理描写 |
