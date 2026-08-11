---
name: ui-dev
description: >-
  UI 界面开发助手——负责 UI 控件的绑定、交互逻辑、数据绑定、动画播放、
  异步防御等 UI 层开发工作。调用 logic 层接口获取数据，完成 UI 自身的功能。
  适用场景：做界面、写 UI、弹窗、面板、列表项、UIBP、按钮点击、
  界面刷新、OnPostInitialize、RegistEvents、LoopScrollGrid 等。
  触发词：做界面、写 UI、做一个弹窗、做一个面板、做一个列表项、UIBP、
  ShowUI、界面开发、加一个按钮、做 XX 界面、实现 XX UI、画一个 XX。
  注意：业务逻辑/数据处理/协议收发请用 logic-dev，重构请用 code-refactor。
---

# UI 界面开发（ui-dev）

## 设计背景

UI 层是玩家能直接感知的层——它调用 logic 层接口获取数据，负责展示和交互，
通常不自己处理业务规则。一个 UI 模块的核心职责是：

```
接收数据 → 绑定控件 → 响应用户交互 → 更新展示
```

本 skill 专注于 UI 面：控件绑定、交互响应、数据刷新、动画、异步防御。
如果你的任务是数据处理、协议收发、业务规则，应该用 logic-dev。

---

## 职责边界

### ✅ 本 skill 负责

- 控件绑定（OnPostInitialize 中的控件注册）
- 事件注册与注销（RegistEvents / UnRegistEvents）
- 用户交互响应（OnClick、OnDrag、OnScroll 等）
- 数据到控件的绑定（SetData、SetItemData、SetTexture 等）
- UI 状态管理（WidgetSwitcher 切换、控件的 visible/collapsed）
- 动画播放（PlayAnimation、StopAnimation）
- 异步防御（界面关闭时取消正在进行的异步操作）
- 通用 UI 控件的对外接口（如通用头像 InitView、通用物品 UI SetData）

### ❌ 本 skill 不负责

- 业务规则的实现（应该调用 logic 层）
- 协议收发（应该通过 handler 或 logic 层）
- 数据存储与管理（应该由 logic/data 层管理）
- UI 布局设计（布局和美术资源由蓝图完成）

---

## 路径配置

| 变量 | 说明 |
|------|------|
| `PROJECT_SRC_DIR` | 项目源码根目录（语言/框架无关） |

---

## 执行流程

### 阶段 0：判定是否需要完整流程

```
改动 ≤ 30 行 && 涉及文件 ≤ 2 个 && 不新增文件 → 降级到 quick-fix
否则 → 走完整流程
```

### 阶段 1：调研（调用 research）

调用 research skill 执行调研。重点关注：
- 目标 UI 模块对应的 logic 层接口有哪些
- 类似 UI 实现的参考（如参考一个已有的弹窗来写新弹窗）
- 需要加载的美术资源是否存在

### 阶段 2：风格分析（调用 module-style）

如果是**在已有 UI 模块上修改**（如给现有弹窗加按钮）：
- 调用 module-style skill 分析该 UI 文件的风格
- 注意 UI 层的特有习惯：控件变量命名、事件绑定方式、刷新策略

如果是**新建 UI 模块**：跳过此步。

### 阶段 3：加载经验库

```
1. Read 个人经验 _index.md
2. Read 项目经验 _index.md
3. 语义匹配 UI 相关分类（naming / abstraction / cross-cutting）
4. Read 相关经验条目
```

### 阶段 4：输出 Plan（按 plan-output 模板）

按 plan-output skill 模板输出方案，UI 方案特别需要说明：
- **控件清单**：涉及哪些控件（从蓝图已有控件出发）
- **数据来源**：调用哪个 logic 接口获取数据
- **交互流程**：用户点击 → 触发了什么

### 阶段 4.5：Stub（接口骨架）—— Plan 之后、实现之前

Plan 确认后，**不要立即写实现代码**。先在目标 UI 文件中写入接口骨架——消除你和用户之间对 UI 交互理解的分歧。

**Stub 包含三样东西**：
1. **函数签名 + LDoc 注解**（`---@param`、`---@return`）
2. **TODO 步骤注释**（描述每个控件操作步骤，不写具体 API 调用）
3. **数据流注释**（函数顶部 1-2 行："数据从哪个 logic 接口来 → 绑定到哪些控件 → 响应用户什么操作"）

**格式示例**：
```lua
-- 数据流: logic_team:GetMemberList() → LoopScrollGrid → 每项响应 OnClick
---@param memberList table 成员列表
---@return void
function TeamMember_UIBP:RefreshMemberList(memberList)
    -- TODO: 清空 LoopScrollGrid 已有数据
    -- TODO: 遍历 memberList，逐项 SetItemData
    -- TODO: 设置空列表占位提示的可见性
end

-- 数据流: 用户点击邀请按钮 → logic_team:SendInvite(uid) → 按钮置灰 + 倒计时
---@param uid number 被邀请玩家UID
---@return void
function TeamMember_UIBP:OnClickInvite(uid)
    -- TODO: 检查冷却时间是否结束
    -- TODO: 调用 logic_team:SendInvite(uid)
    -- TODO: 按钮设为不可点击
    -- TODO: 启动 3 秒倒计时后恢复按钮状态
end
```

**Stub 约束**：
- 只有 ≥2 个地方调用的 UI 逻辑才新建函数。一次性使用的逻辑用 `-- TODO: xxx` 内联在按钮回调中
- 不要写具体控件 API 调用（`self.Button:SetEnable(false)` 太早——可能你用 `SetButtonEnable` 而非 `SetEnable`）
- 不要为了"让 Stub 清晰"而把简单 UI 刷新拆成多个函数

**写入文件**：
Stub 直接写入目标 UI 文件。用户可以选择：
- ✅ 确认 Stub → 进入阶段 5 实现
- ✏️ 指出交互流程有误 → 回到阶段 4 修正 Plan
- 🛑 在此停下 → 用户自己按控件清单和 TODO 注释手动实现

### 阶段 5：实现

用户确认 Stub 后，按 TODO 注释逐条填充控件操作代码。
- 在 `OnPostInitialize` 中集中完成控件变量赋值
- 控件变量名通常与蓝图中的控件名一致

**事件注册规范**：
- 在 `RegistEvents`（或等价方法）中集中注册所有事件
- 在 `UnRegistEvents`（或等价方法）中取消注册
- 界面关闭/销毁时必须清理事件，防止空回调

**异步防御**：
- 任何异步操作（网络请求、定时器、动画回调）在执行前检查 `self.bp` 是否有效
- 关闭界面时取消所有进行中的异步操作

**UI 实现约束**：
- UI 层不应该实现业务规则。如果发现自己正在写 `if player.level >= 10 and vip...`，停下来——这应该在 logic 层
- UI 层可以有自己的轻量状态（如当前选中的 tab、滚动位置），但不应该有业务状态
- 对外提供通用控件的调用接口时（如 `InitView`），接口参数应简单直观

**日志**：
- UI 层面的日志重点在关键交互点（打开界面、点击按钮、切换 Tab）
- 避免在每帧刷新/滚动回调中打全量日志

### 阶段 6：自检（调用 change-review）

审查本次 diff，UI 层额外关注：
- 有没有忘记 `UnRegistEvents` 或等价的清理逻辑
- 异步操作前有没有检查 `self.bp`
- 有没有在 UI 层实现了业务逻辑

### 阶段 7：提示调研发现

同 logic-dev 阶段 7——发现了新的 API 提示写入注册表。

---

## 用户写骨架、AI 填实现（可选模式）

```lua
---@param data table { iconPath, name, level, desc }
function Setting_Item_UIBP:SetData(data)
    -- 1. 设置图标
    -- 2. 设置名称文本
    -- 3. 根据等级切换对应样式
    -- 4. 设置描述（如果为空则隐藏描述控件）
end
```

AI 按骨架填充，不新增函数。这特别适合 UI 开发——你定义好每个控件的刷新逻辑，
AI 只负责把操作控件的代码写出来。

---

## 关键原则

1. **UI 不实现业务规则**——业务逻辑永远在 logic 层
2. **异步操作必须防御**——界面关闭后回调不应该执行
3. **事件注册必须清理**——RegistEvents 和 UnRegistEvents 成对出现
4. **控件绑定集中在 OnPostInitialize**——不要散落在各处
5. **日志关注交互点**——用户做了什么操作，而不是每一帧刷新

---

## 与其他 Skill 的关系

| Skill | 调用阶段 | 用途 |
|-------|---------|------|
| research | 阶段 1 | 找 logic 接口、找参考 UI、验证资源 |
| module-style | 阶段 2 | 匹配已有 UI 的风格 |
| api-registry | 阶段 5 | 验证 UI 框架接口（UIBase 方法等） |
| experience-repo | 阶段 3 + 5 | UI 相关的命名/抽象偏好 |
| plan-output | 阶段 4 | 统一方案输出 |
| change-review | 阶段 6 | 审查 UI 特有的问题（清理、防御） |
| quick-fix | 阶段 0 | 小 UI 改动降级 |
