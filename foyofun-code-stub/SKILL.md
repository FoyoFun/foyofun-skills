---
name: foyofun-code-stub
description: >-
  代码骨架生成——Plan 确认后、实现之前，把新增文件、新增接口、新增函数的骨架直接写入
  项目文件：函数签名 + 文档注释 + TODO 步骤注释 + 数据流注释。骨架必须自足——把调研、
  风格、API、经验的全部结论内嵌进去，让用户本人或一个能力较弱、不做调研的 AI 模型
  （如 Flash 级模型）能仅凭骨架完成实现。由 foyofun-code-logic / ui 在 Plan 确认后调用。
---

# 代码骨架（foyofun-code-stub）

## 设计背景

骨架是 Plan 与实现之间的**歧义消除层**。它把"AI 对方案的理解"变成可检查的中间产物，
在写代码之前消灭理解偏差。

骨架有**两个消费者**，质量标准由它们决定：
1. **用户本人**——照着骨架手写实现，或改完骨架再交给 AI；
2. **弱模型**（Flash 级）——用户通常用 Pro 级模型出 Plan 和骨架，切 Flash 级模型填实现。
   弱模型**不做调研、不做决策、不会查询 API**，它的任务只是"把注释翻译成代码"。

## 自足性标准（核心）

骨架必须让一个"不做任何调研和决策"的实现者完成任务。生成前自查：

- [ ] 每个函数的**签名精确**（参数名、类型注释、返回值）
- [ ] 涉及的项目 API **签名已验证并写明**（foyofun-code-api 的结论直接写进注释，
      不留"调用某接口"这种占位描述）
- [ ] **数据形状具体**（快照/intent 的字段表，不是"一个 table"）
- [ ] **风格要点内嵌**（命名/注释/日志惯例，来自 foyofun-code-style，写进骨架顶部）
- [ ] **适用经验条目内嵌**（foyofun-code-experience 的相关推荐做法）
- [ ] 每个 TODO 说清**做什么**；需要设计决策的地方已经替弱模型决定好**怎么做**

## 三种标记（全体系的通用约定）

| 标记 | 含义 | 生命周期 |
|------|------|---------|
| `-- TODO:` | 实现步骤 | 实现完成后删除 |
| `-- [SEAM]` | 跨层契约桩（快照 getter、intent 分发点等，注明归属方） | 集成期由 foyofun-code-integrate 消费后删除 |
| `-- [MOCK]` | 闭环用的假数据源/假应答 | 集成期替换为真调用后删除 |

注释语法按语言调整（Lua `--`，C#/C++/Java `//`，Python `#`），标记名不变。
`[SEAM]` 和 `[MOCK]` 是跨对话的对接点索引——调研和集成都靠搜索它们工作，
所以**必须原样保留拼写**。

## 骨架内容四件套

1. **结构分区**：按目标执行 skill 的标准结构生成分区注释横幅与生命周期函数
   （结构模板见 foyofun-code-logic / foyofun-code-ui 的 references/）
2. **函数签名 + 文档注释**（LDoc/XML doc/模块惯例格式）
3. **TODO 步骤注释**：每个函数内列出步骤，只描述做什么
4. **数据流注释**：函数顶部 1-2 行——数据从哪来 → 经过什么处理 → 到哪去

示例：

```lua
-- [SEAM] GetTeamSnapshot(): 团队快照，logic 侧实现，集成期接入
-- 数据流: on_datas_rsp → 原始数据缓存 → 懒加工 → 本接口
---@param uid number 玩家UID
---@return table { members: {uid,name,level}[], canInvite: boolean }
function TeamData:GetTeamSnapshot(uid)
    -- TODO: 脏标记检查（need_refresh[uid] 为 true 时先调 ProcessDatas）
    -- TODO: 组装快照：members 从 datas[uid] 映射，canInvite = #members < C_MAX_NUM
    -- TODO: 防御：无数据时返回空表 { members = {}, canInvite = false }
end
```

## 生成流程

1. Plan 已被用户确认（未确认不生成）。
2. 读目标执行 skill 的结构模板（logic/ui 的 references/structure-lua.md），
   新建文件按标准结构生成完整分区；已有文件只生成新增部分，风格对齐既有代码。
3. 骨架**直接写入目标文件**（不是临时文件），跨层对接点打 `[SEAM]`，
   闭环所需的假数据打 `[MOCK]`。
4. 输出骨架清单（文件 × 函数 × 标记），用户三选一：
   - ✅ 确认 → 进入实现（本人写 / 弱模型写 / 原模型继续写均可）
   - ✏️ 指出理解有误 → 修正后重新生成（不辩解，先理解用户为什么觉得不对）
   - 🛑 停在这里 → 用户自己照骨架实现

## 约束

- **不写任何实现代码**——哪怕一行防御代码也太早，那是实现阶段的事
- 新建函数门槛与 Plan 第 3 节一致：≥2 调用方或独立关注点；单调用方逻辑用 TODO 内联
- 不为"让骨架更清晰"而多拆函数——宁可一处多两行 TODO
- 已有文件中生成骨架时，插入位置遵循该文件既有分区结构

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| foyofun-code-plan | 上一步；骨架是 Plan 第 3/4 节的代码化 |
| foyofun-code-style | 风格摘要内嵌进骨架 |
| foyofun-code-api | 已验证 API 签名内嵌进骨架 |
| foyofun-code-experience | 适用经验条目内嵌进骨架 |
| foyofun-code-logic / ui | 调用方；持有各自的标准结构模板 |
| foyofun-code-integrate | `[SEAM]`/`[MOCK]` 标记的消费方 |
