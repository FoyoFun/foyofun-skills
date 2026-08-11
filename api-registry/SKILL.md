---
name: api-registry
description: >-
  项目 API 注册表——保存和检索项目封装的通用接口与框架特有接口。
  核心价值是用项目知识对抗 AI 的训练数据惯性：避免 AI 使用 os.time() 而不是
  TimeUtil.GetServerTimeInSec()、用 string.split 而不是 StringUtil.Split 等。
  既方便 AI 查找项目封装，也方便用户手动查看和维护。
  触发词：查接口、项目有什么 API、有没有封装、怎么调用、XX 的接口在哪、
  API 注册、收录接口、查一下 XX 的用法、这个用标准库还是项目封装。
  当 AI 在写代码前需要确认某个功能是否有项目封装接口时，也应主动查阅本注册表。
---

# API 注册表（api-registry）

## 设计背景

AI 天然倾向使用训练数据中的标准库 API（`os.time()`、`string.split`、`table.sort`），
但大型项目中通常有更合适的封装（`TimeUtil.GetServerTimeInSec()`、`StringUtil.Split`、
`TableUtil.SortByKey`）。这些封装处理了时区、nil 安全、热更兼容等问题，
直接用标准库会导致隐藏 bug。

本 skill 维护一个**人机共读**的 API 注册表，格式既适合 AI 快速扫描（函数签名 + 一句话说明），
也适合用户手动维护（清晰的分类 + 表格）。

---

## 路径配置

| 变量 | 说明 |
|------|------|
| `PROJECT_SRC_DIR` | 项目源码根目录（语言/框架无关，由环境提供或项目适配配置提供） |
| `REGISTRY_DIR` | `${PROJECT_SRC_DIR}/.record/api-registry/` |

> **注意**：数据存储在项目目录 `.record/api-registry/` 下，不在 plugin/skill 目录下。
> 这样 skill 本身可以上传 GitHub（无敏感信息），而 API 注册表数据绑定项目、不出仓库。

---

## 数据目录结构

```
${PROJECT_SRC_DIR}/.record/api-registry/
├── _index.md              # 分类路由表（手动维护）
├── _flat_index.md          # 脚本自动生成，一行一个 API
├── time.md                 # 时间相关
├── string.md               # 字符串相关
├── table.md                # 表/数组相关
├── ui-base.md              # UI 基类（UIBase生命周期等）
├── ui-widget.md            # UI 控件操作
├── module-base.md          # Module 基类
├── network.md              # 网络/协议相关
├── config.md               # 配置表读取
├── event.md                # 事件系统
├── log.md                  # 日志接口
├── timer.md                # 定时器相关
├── math.md                 # 数学计算
├── file.md                 # 文件操作
├── ...                     # 更多分类按需新增
```

---

## 叶子文档格式（人机共读）

每个分类文件（如 `time.md`）格式如下：

```markdown
## TimeUtil

### `TimeUtil.GetServerTimeInSec() → number`
获取服务器时间（秒）。**替代 `os.time()`**——后者在客户端返回本地时间，可能导致与服务器时间不一致。
常用于：倒计时、活动时间判断、数据时效性校验。

### `TimeUtil.GetServerTimeInMs() → number`
获取服务器时间（毫秒）。

### `TimeUtil.FormatTime(timestamp, format) → string`
格式化时间戳为字符串。format 可选："%Y-%m-%d %H:%M:%S"（默认）、"%Y/%m/%d" 等。

---

## DateUtil

### `DateUtil.IsSameDay(ts1, ts2) → boolean`
判断两个时间戳是否同一天。**替代 `os.date("%d", ts1) == os.date("%d", ts2)`**。
```

**格式规则**：
- 每个源文件/模块（如 TimeUtil）用 `##` 标题
- 每个 API 用 `###` 标题，格式为 `` `完整签名 → 返回类型` ``
- 下面 1-2 行说明，包含：功能、**替代了哪个标准库 API**（如果有）、常用场景
- 如果 API 有常见误用方式，加 `⚠️` 警告

### 人可维护性设计

- 文件名就是分类名（`time.md` = 时间相关），直觉就能找到
- 函数签名直接可复制到代码中调用
- "替代了 XXX" 是给 AI 看的——告诉它在什么情况下**不要**用训练数据中的 API
- 每个分类文件独立，不会因为改一个文件影响其他分类

---

## 检索流程（省 token 模式）

和通用知识库检索采用相同的索引路由策略：

```
1. Read _flat_index.md（一行一个 API，全部叶子条目）
   → 语义匹配关键词 → 定位到目标分类文件（如 time.md）
2. Read 目标分类文件（通常 50-200 行）→ 按需 Read 相关段落
```

| 步骤 | Token 消耗 |
|------|-----------|
| 读 _flat_index.md | ~500-2000 tokens |
| 读目标分类文件 | ~300-1500 tokens |
| **合计** | **~800-3500 tokens** |

对比逐文件遍历（需要 Read 10+ 个分类文件），省 60-80%。

---

## 写入流程

### 用户主动触发

用户说"记录这个接口"、"收录到 API 注册表"、"这个 API 记一下"等。

### research 调研后提示

research skill 调研结束后，如果发现了未收录的 API，会提示用户是否写入。
用户确认后，调用本 skill 的写入流程。

### 写入步骤

1. **判定分类**：根据 API 的功能判断属于哪个分类（time / string / ui-base / ...）
   - 如果现有分类都不匹配，创建新分类文件
2. **检查重复**：Read 目标分类文件，确认该 API 尚未收录
3. **追加条目**：在对应 `##` 模块下追加 `###` 条目
4. **更新 _index.md**：如果新增了分类文件，在索引表中追加一行
5. **重建 _flat_index.md**：
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/build-api-flat-index.py" --root "${REGISTRY_DIR}"
   ```
   如果该脚本尚未创建（首次使用），则手动在 `_flat_index.md` 尾部追加一行：
   ```
   | {分类} | {模块名} | {API签名} | {一句话说明} | {文件名}.md#{锚点} |
   ```

### 写入示例

```
用户: "记录一下，LogicUtil.IsInLobby() 可以判断玩家是否在大厅"

AI:
1. 判定分类 → lobby（新建）
2. 创建 time.md... 不，创建 lobby.md
3. 追加条目
4. 更新 _index.md
5. 重建 _flat_index.md
6. 告知用户："✅ 已收录 `LogicUtil.IsInLobby()` 到 API 注册表 (lobby.md)"
```

---

## _index.md 格式

```markdown
# API 注册表索引

| 分类 | 文件名 | 描述 |
|------|--------|------|
| 时间 | `time.md` | TimeUtil、DateUtil 等时间相关封装 |
| 字符串 | `string.md` | StringUtil 等字符串处理封装 |
| UI 基类 | `ui-base.md` | UIBase 生命周期、标准方法 |
| UI 控件 | `ui-widget.md` | 通用控件操作接口 |
| Module 基类 | `module-base.md` | ModuleBase 生命周期与数据管理 |
| 网络 | `network.md` | NetManager、协议收发封装 |
| 配置表 | `config.md` | CDataTable 等配置表读取接口 |
| 事件 | `event.md` | EventSystem、EventDefine |
| 日志 | `log.md` | log、log_format、log_tree 等 |
| 定时器 | `timer.md` | AddTimerLoop、AddTimer 等 |
| ... | ... | ... |
```

---

## _flat_index.md 格式（自动生成）

一行一个 API，供 AI 快速扫描和语义匹配：

```markdown
# API 注册表扁平索引

| 分类 | 模块 | API 签名 | 说明 | 路径 |
|------|------|---------|------|------|
| 时间 | TimeUtil | `GetServerTimeInSec() → number` | 获取服务器时间(秒), 替代 os.time() | time.md#timeservertimeinsec--number |
| 时间 | TimeUtil | `GetServerTimeInMs() → number` | 获取服务器时间(毫秒) | time.md#timeservertimeinms--number |
| 时间 | DateUtil | `IsSameDay(ts1, ts2) → boolean` | 判断同一天, 替代 os.date() | time.md#dateutilissamedayts1-ts2--boolean |
| 字符串 | StringUtil | `Split(str, sep) → table` | 分割字符串, 替代 string.split | string.md#stringutilsplitstr-sep--table |
| ... | ... | ... | ... | ... |
```

---

## 关键原则

1. **人机共读**——格式要方便人手动改，同时也方便 AI 扫描
2. **"替代了 XXX" 是核心信息**——告诉 AI 什么时候不该用训练数据中的 API
3. **数据绑定项目，不绑定 skill**——注册表内容在 `.record/` 下
4. **渐进增长**——每次 research 调研都是完善注册表的机会
5. **函数签名直接可复制**——减少查阅后还要打开源文件看参数

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| research | 调研时查注册表，发现新 API 后提示写入 |
| experience-repo | 经验库记录"何时用哪个 API"的模式偏好 |
| logic-dev / ui-dev / code-refactor / quick-fix | 实现阶段持续查阅，确保每个调用都用项目封装 |
| change-review | Review 时验证是否误用了标准库 API |
