---
name: logic-dev
description: >-
  业务逻辑层开发助手——关注数据流、数据处理、逻辑功能、数据管理，
  不关注 UI 实现。职责：接收数据 → 存储数据 → 加工数据 → 提供功能接口 → 处理时序。
  适用于开发 logic 模块、handler、数据管理、协议处理、业务逻辑重构。
  触发词：开发 logic、实现功能、写一个模块、做XX逻辑、新增一个 handler、
  处理协议、数据管理、实现 XX 功能、写业务逻辑、开发一个系统。
  注意：做界面/UI/弹窗/按钮请用 ui-dev，重构代码结构请用 code-refactor，
  小修小补请用 quick-fix。
---

# 业务逻辑层开发（logic-dev）

## 设计背景

业务逻辑层是游戏的骨架——它决定数据从哪来、怎么变、存哪里、怎么提供给上层。
一个好的 logic 模块应该让 UI 层可以"傻瓜式调用"：拿到数据就展示，不需要自己理解业务规则。

本 skill 专注于数据面，不处理 UI 交互。如果你的任务涉及界面布局、控件绑定、
动画播放，应该用 ui-dev。

---

## 职责边界

### ✅ 本 skill 负责

- 协议收发与解析（handler）
- 数据存储与缓存（data/manager）
- 业务规则计算（logic）
- 数据加工与转换（加工原始数据为 UI 可用格式）
- 时序控制（异步请求的顺序、回调时机）
- 提供对外的函数接口（给 UI 或其他模块调用）
- 事件派发（通知 UI 数据变更）

### ❌ 本 skill 不负责

- UI 控件绑定与操作
- 界面布局与动画
- 蓝图交互
- 美术资源加载
- 用户输入处理（点击、滑动等）——除非是纯数据层的输入

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

调用 research skill 执行调研。这是强制步骤——不拿调研结论就不进入 Plan。

调研完成后，检查调研结论的合格线清单是否全部打勾。

### 阶段 2：风格分析（调用 module-style）

如果是**在已有模块上修改**（非新建模块）：
- 调用 module-style skill 分析目标模块风格
- 将风格摘要记入上下文

如果是**新建模块**：跳过此步。按 api-registry 和 experience-repo 的指引来。

### 阶段 3：加载经验库

```
1. Read 个人经验 _index.md（${HOME}/.claude/experiences/personal/_index.md，用 `echo $HOME` 解析）
2. Read 项目经验 _index.md（${PROJECT_SRC_DIR}/.record/experiences/project/_index.md）
3. 根据当前任务语义匹配相关分类
4. Read 相关分类文件中的经验条目
```

### 阶段 4：输出 Plan（按 plan-output 模板）

按 plan-output skill 定义的模板输出方案。

如果用户提供了函数骨架（LDoc + 步骤注释），直接在方案中说明"按用户骨架填充实现"，跳到阶段 5。

### 阶段 4.5：Stub（接口骨架）—— Plan 之后、实现之前

Plan 确认后，**不要立即写实现代码**。先在目标文件中写入接口骨架——消除你和用户之间对 Plan 理解的歧义。

**Stub 包含三样东西**：
1. **函数签名 + LDoc 注解**（`---@param`、`---@return`、`---@type`）
2. **TODO 步骤注释**（用 `-- TODO:` 描述每个步骤要做什么，不写具体实现）
3. **数据流注释**（函数顶部 1-2 行，描述"数据从哪来 → 经过什么处理 → 到哪去"）

**格式示例**：
```lua
-- 数据流: RPC GetInfoReq → Handler.on_GetInfoRsp → self.dataCache → 本接口
---@param uid number 玩家UID
---@return table|nil { level, exp, vipLevel }
function PlayerData:GetPlayerSummary(uid)
    -- TODO: 从 self.dataCache[uid] 获取基础数据
    -- TODO: 如果缓存未命中，返回 nil（调用方需处理）
    -- TODO: 补充 lastLoginTime 字段（当前缓存中缺少）
end

-- 数据流: 定时器 → 检查缓存时效 → 按需发 RPC → 更新缓存
---@return void
function PlayerData:RefreshIfExpired(uid)
    -- TODO: 判断 self.dataCache[uid].updateTime 距现在是否 > TTL
    -- TODO: 过期则发 GetInfoReq，在回调中更新缓存
    -- TODO: 未过期则跳过
end
```

**Stub 约束**：
- 只有 ≥2 个调用方使用的逻辑才新建函数签名。单调用方的逻辑用 `-- TODO: xxx` 内联在已有函数中
- 不要写任何实现代码——哪怕一行 `if not data then return nil end` 也太早
- 不要为了"让 Stub 更清晰"而新增不必要的接口——宁可在一处多写两行 TODO，也不要拆成三个函数

**写入文件**：
Stub 直接写入目标代码文件（非临时文件）。这样用户可以选择：
- ✅ 确认 Stub → 进入阶段 5 实现
- ✏️ 指出理解有误 → 回到阶段 4 修正 Plan，再重新输出 Stub
- 🛑 在此停下 → 用户自己按 Stub 中的接口和 TODO 注释手动实现

**歧义处理**：
如果用户说"不对，XX 不应该在这里"，不要辩解。先理解用户为什么觉得不对——
是 Plan 本身有问题（回到阶段 4 修正），还是 Stub 的表达方式有误导（调整 Stub 即可）。

### 阶段 5：实现

用户确认 Stub 后，按 TODO 注释逐条填充实现。

**每写一个 API 调用前**：
1. 先在 api-registry 的 `_flat_index.md` 中检查是否有项目封装
2. 如果有 → 使用项目封装
3. 如果没有 → 用 Grep 搜索 `{函数名}` 确认该接口确实存在于项目中
4. 如果搜索也不到 → 停下来，标注 `-- TODO: 需确认 {函数签名} 是否存在`

**实现规范**（持续参考）：
- experience-repo 中的经验规则
- module-style 的风格摘要
- project-coding-standards（如已配置）

**接口新增约束**（奥卡姆剃刀原则）：
- 默认在现有接口中修改，不新建接口
- 只有在以下情况才新建接口：
  a. 新功能被 ≥2 个调用方使用
  b. 现有接口已达 ~80 行且新逻辑 ≥30 行
  c. 新逻辑与现有接口关注点完全不同
- 如果只是加 ≤10 行逻辑，直接改现有接口

**切面原则**（详见 experience-repo → cross-cutting.md）：
接口按职责分为三类：
- **原子接口**：职责单一，最小不可拆分（如 `Clean()`、`IsInLobby()`）
- **门面接口**：供外部调用，内部做好兜底，让调用方省心（门面可以嵌套原子）
- **编排接口**：内部流程，平级调用，让维护者看清完整生命周期

写每个函数前先问：它是给外部调用的门面，还是内部编排的一环？
- 门面 → 内部可嵌套原子，调用方无需关心细节
- 编排 → 同级调用不嵌套，维护者一眼看清生命周期

### 阶段 6：自检（调用 change-review）

实现完成后，调用 change-review skill 审查本次 diff。

重点关注：
- 是否有阻塞项
- 关键路径是否都有日志
- 循环内是否有不必要的全量打印
- 是否全部使用了项目封装接口

### 阶段 7：提示调研发现

如果实现过程中发现了新的 API（research 调研时未覆盖的），提示用户：

```
💡 本次实现中使用了 {N} 个未收录的 API，建议写入 API 注册表。
```

---

## 用户写骨架、AI 填实现（可选模式）

如果用户提供了这样的骨架：

```lua
---@param playerUid number 玩家UID
---@return table { level, exp, vipLevel }
function PlayerDataManager:GetPlayerSummaryInfo(playerUid)
    -- 1. 从玩家数据缓存中获取基础信息
    -- 2. 如果缓存未命中，从服务器拉取
    -- 3. 组装返回结构
    -- 4. 更新最后访问时间
end
```

则：
1. **不新增任何函数**（骨架已经定义了接口边界）
2. 按骨架中的 LDoc 和步骤注释逐条实现
3. 实现完成后，走阶段 6 自检

这是最理想的协作模式——你控制架构，AI 填充细节。

---

## 关键原则

1. **数据流 > 文件列表**——从数据视角看问题，比从文件视角更清晰
2. **如非必要，勿增接口**——在现有接口中补充逻辑是默认选项
3. **每个 API 调用都要验证存在性**——查 registry → Grep → TODO
4. **切面意识**——一个函数只做一件事，调用方负责编排
5. **日志是给未来的自己看的**——关键节点不省、循环内不滥

---

## 与其他 Skill 的关系

| Skill | 调用阶段 | 用途 |
|-------|---------|------|
| research | 阶段 1 | 强制前置调研 |
| module-style | 阶段 2 | 分析目标模块风格 |
| api-registry | 阶段 5 | 验证 API 存在性，选择项目封装 |
| experience-repo | 阶段 3 + 5 | 加载经验规则，指导实现 |
| plan-output | 阶段 4 | 统一方案输出格式 |
| change-review | 阶段 6 | 实现后自检 |
| quick-fix | 阶段 0 | 小改动降级入口 |
