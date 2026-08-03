---
name: experience-repo
description: >-
  编码经验库——用正反例对比的方式记录用户对代码可读性、可维护性的偏好。
  支持读取（AI 写代码时参考）和保存（用户描述偏好时记录）。
  当 AI 在 logic-dev / ui-dev / code-refactor / quick-fix 的实现阶段，
  应主动加载经验库检查是否有适用的经验规则。
  触发词（保存）：记住、记一下、以后遇到这种、我的习惯是、不要这样写、
  这样写更好、这个经验记录一下、记下来。
  触发词（读取）：由其他 skill 内部调用，不直接面向用户触发。
---

# 经验库（experience-repo）

## 设计背景

AI 在代码架构上的判断（耦合/内聚/可读性/可维护性/拓展性/切面/效率的平衡），
和人的经验差距很大。抽象规则无法准确传达这种"微妙的平衡感"，
但**具体的正反例对比**可以有效缩小这个差距。

例如：用户可能认为"UI 组件索引即使被多次使用也不应提取为变量"，
因为这增加了维护者的记忆负担——而 AI 受训练数据影响，倾向提取变量减少重复。
这种偏好很难用抽象规则描述，但用一个正反例就能清晰传达。

本 skill 分为两层存储：
- **个人经验**：跟随插件，跨项目复用（通用的编码审美）
- **项目经验**：绑定项目，不污染其他项目（项目特有的惯用模式）

---

## 路径配置

| 变量 | 说明 |
|------|------|
| `CLAUDE_PLUGIN_ROOT` | ai-coding 插件根目录 |
| `PROJECT_LUA_DIR` | Lua 代码根目录 |
| `PERSONAL_EXP_DIR` | `${CLAUDE_PLUGIN_ROOT}/experiences/personal/` |
| `PROJECT_EXP_DIR` | `${PROJECT_LUA_DIR}/.record/experiences/project/` |

> **安全设计**：项目经验存在 `.record/` 下，不上传 GitHub。个人经验在插件目录下，
> 用户自行决定是否上传。skill 文件本身不含任何经验数据，可安全上传。

---

## 数据目录结构

```
个人经验（${CLAUDE_PLUGIN_ROOT}/experiences/personal/）：
├── _index.md              # 分类索引
├── naming.md              # 变量/函数命名偏好
├── traversal.md           # 遍历：何时合并/分离
├── abstraction.md         # 抽象层次：何时提取变量/函数
├── cross-cutting.md       # 切面组织
├── logging.md             # 日志习惯
├── interface-design.md    # 接口设计原则
└── ...

项目经验（${PROJECT_LUA_DIR}/.record/experiences/project/）：
├── _index.md
├── module-patterns.md     # 项目特有的模块组织方式
├── protocol-handling.md   # 协议处理约定
├── config-usage.md        # 配置表使用习惯
└── ...
```

---

## 经验条目格式（正反例对比）

每一条经验包含三个部分：**场景**、**✅ 推荐做法**、**❌ 不推荐做法**、**原因**。

### 示例 1：UI 组件索引不提取为变量

```markdown
## 经验：UI 组件索引不提取为变量

**场景**：在 UI 函数中多次访问同一个子控件。

### ✅ 推荐
```lua
function Lobby_Social_UIBP:RefreshAll()
    self.FriendList:SetData(friends)
    self.FriendList:ScrollToTop()
    self.FriendList:SetVisible(true)
end
```

### ❌ 不推荐
```lua
function Lobby_Social_UIBP:RefreshAll()
    local list = self.FriendList
    list:SetData(friends)
    list:ScrollToTop()
    list:SetVisible(true)
end
```

**原因**：`self.FriendList` 本身已具备语义（是好友列表控件），提取为局部变量 `list`
只省了两次 `self.Friend` 的键入，却让维护者多记一个局部变量名——它指向什么、
和 `self.FriendList` 是不是同一个东西？除非性能数据显示成员访问是瓶颈，
否则保留 `self.` 前缀使代码"自文档化"。

**适用项目**：通用（个人经验）
**记录时间**：2026-08-03
```

### 示例 2：逻辑独立的两次遍历不合并

```markdown
## 经验：逻辑独立的两次遍历不合并

**场景**：同一数据源需要做两种不同的处理。

### ✅ 推荐
```lua
-- 先统计各模式数量
for _, data in ipairs(modeList) do
    self:CountMode(data.mode_id)
end

-- 再找出最高价值的模式
for _, data in ipairs(modeList) do
    self:CheckBestMode(data.mode_id, data.value)
end
```

### ❌ 不推荐
```lua
for _, data in ipairs(modeList) do
    self:CountMode(data.mode_id)
    self:CheckBestMode(data.mode_id, data.value)
end
```

**原因**：两次遍历分别服务于不同的业务目的（统计 vs 筛选），分开写让每个循环
的职责一目了然。合并虽然省了一次遍历，但把两个无关的逻辑强行耦合在同一个
循环体中。维护者修改"统计"逻辑时还要担心是否影响了"筛选"——而拆开则互不干扰。
只有当量级真的大到出现体验问题（如 10000+ 元素的列表）时才考虑合并。

**适用项目**：通用（个人经验）
**记录时间**：2026-08-03
```

### 示例 3：如非必要，勿增接口（项目经验示例）

```markdown
## 经验：如非必要，勿增接口

**场景**：需要在现有模块中补充新功能逻辑。

### ✅ 推荐
```lua
-- 在现有 GetPlayerSummary 接口中补充新字段
function PlayerData:GetPlayerSummary(uid)
    local base = self:GetBaseData(uid)
    base.newField = self:CalcNewField(uid)  -- 新增 3 行
    return base
end
```

### ❌ 不推荐
```lua
-- 新建专门的接口
function PlayerData:GetPlayerSummaryWithNewField(uid)
    ...
end
```

**原因**：增加新接口会引入新的调用契约，调用方需要知道什么时候用
`GetPlayerSummary`、什么时候用 `GetPlayerSummaryWithNewField`。
而直接在现有接口中补充，调用方无感知升级。只有在新逻辑超过 ~30 行、
或与现有接口关注点完全不同、或被 ≥2 个调用方独立使用时，
才考虑新建接口。

**适用项目**：{具体项目名}
**记录时间**：2026-08-03
```

---

## 读取流程（AI 写代码时）

### 被 f/g/h/i 调用

logic-dev / ui-dev / code-refactor / quick-fix 在实现阶段应：

1. **实现前**：Read 个人经验 `_index.md` + 项目经验 `_index.md`（~500 tokens 合计）
2. **语义匹配**：根据当前任务，定位相关的经验分类（如写 UI 代码 → 查 `naming.md`、`abstraction.md`）
3. **Read 相关分类文件**：检查是否有适用的经验规则
4. **代码中遵守**：有匹配的经验 → 按推荐做法写；无匹配 → 自由发挥

如果当前任务明显不涉及某分类（如纯数据计算不涉及 UI 控件），跳过该分类文件。

---

## 写入/保存流程（用户描述偏好时）

### 触发条件

用户说类似以下的话时，触发保存：

- "记住，以后这种情况不要提取变量"
- "记一下，我更倾向把这两个遍历分开"
- "我的习惯是日志里不要出现中文"
- "以后遇到类似的，都放在一个函数里改，不要新建函数"
- "这个经验记录一下"

### 保存步骤

1. **理解用户意图**：从上下文确认：
   - 场景是什么？（什么时候适用这条经验）
   - 推荐做法是什么？（用户觉得好的代码）
   - 不推荐做法是什么？（用户觉得不好的代码）
   - 原因是什么？（为什么这样做更好）
2. **选择存储位置**：
   - 通用偏好（跨项目适用）→ 个人经验 `${CLAUDE_PLUGIN_ROOT}/experiences/personal/`
   - 项目特有约定（只在这个项目适用）→ 项目经验 `${PROJECT_LUA_DIR}/.record/experiences/project/`
   - 不确定时默认放个人经验，同时告知用户
3. **判定分类**：naming / traversal / abstraction / cross-cutting / logging / interface-design / ...
4. **检查重复**：Read 目标分类文件，确认没有完全相同的经验。如果有相似但不完全相同的 → 追加为新的经验条目
5. **按正反例格式写入**：追加到目标分类文件尾部
6. **更新索引**：如果是新分类，在 `_index.md` 中追加一行
7. **告知用户**：

```
✅ 已记录经验到 {个人/项目}经验库 → {分类文件名}

📝 记录内容：{一句话概括}
📍 存储位置：{文件路径}

如有不妥，可直接编辑该文件修改。用"查看经验库"可随时回顾。
```

### 用户手动修改

用户看到记录后如果觉得不准确，会自己去对应的文件编辑。这就是为什么格式必须
**人可读、人可改**——正反例对比格式清晰，用户一眼就能看懂并修改。

---

## 查看经验库

用户说"查看经验库"、"我有哪些经验记录"、"显示经验"时：

1. Read 个人经验 `_index.md` + 项目经验 `_index.md`
2. 以表格形式呈现所有分类及条目数
3. 用户指定分类 → Read 对应文件，呈现所有经验条目

---

## 关键原则

1. **正反例比抽象描述有效 10 倍**——用代码说话
2. **人机共读共改**——格式清晰，用户自己也能改
3. **个人和项目分离**——通用审美 vs 项目约定
4. **增量积累**——每次用户纠正 AI 都是一次记录机会
5. **经验 ≠ 铁律**——有匹配的经验时参考，但不死板套用；场景不同时可灵活处理

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| api-registry | 经验库记录"何时用哪个 API"的模式，API 注册表记录"有哪些 API" |
| logic-dev / ui-dev / code-refactor / quick-fix | 实现阶段主动加载经验库 |
| change-review | Review 时用经验库检查是否有违反偏好的写法 |
