---
name: change-review
description: >-
  代码审查助手——只审查当前更改（git diff），不审查已有代码。
  关注四个维度：阻塞项（必须修复）、逻辑错误、日志合理性、API 选择。
  触发词：review、审查代码、检查一下、帮我 review、code review、
  看看有没有问题、检查改动、review 一下当前更改。
  也建议在 logic-dev / ui-dev / code-refactor / quick-fix 完成实现后主动调用。
---

# 代码审查（change-review）

## 设计背景

通用的 code review 往往关注面太广（性能、安全、风格、测试覆盖率...），
导致输出冗长、重点不突出。对于业务逻辑开发，真正要紧的就几件事：

1. **有没有绝对不能合入的问题**（阻塞项）
2. **逻辑对不对**（边界条件、nil 安全、条件判断）
3. **日志是否合理**（关键路径可追溯、但不过度打印）
4. **API 选对了吗**（用了项目封装还是标准库）

本 skill 只审查 `git diff`（未提交的更改），已有代码不在审查范围。
因为——那些代码不是本次改动引入的，审查它们是另一个独立任务。

---

## 审查范围

```
git diff HEAD                    # 已修改但未 stage
git diff --cached                # 已 stage 但未提交
```

审查时合并两者的输出，覆盖本次所有未提交更改。
如果用户指定了文件路径，则只审查指定文件的 diff。

---

## 审查四维度

### 维度 1：🔴 阻塞项（Blocking）

这些问题是**必须修复**的，不修复则代码不可合入：

| 检查项 | 说明 |
|--------|------|
| 使用不存在的 API | 函数名拼写错误、捏造的接口、参数个数不对 |
| 破坏现有调用链 | 改了函数签名但调用方未同步更新 |
| 全局副作用不可控 | 修改了全局变量/单例但没有防御性检查 |
| nil 必然崩溃 | 返回值未 nil-check 就直接 `.` 访问成员 |
| 死循环 / 无限递归 | `while true` 无退出条件，递归无终止条件 |

**检查方式**：每个新增/修改的 API 调用，在 api-registry 中验证其存在性。
api-registry 中没有的，用 Grep 搜索项目确认。

### 维度 2：🟡 逻辑错误（Logic）

这些问题**很可能导致 bug**，需要逐条确认：

| 检查项 | 示例 |
|--------|------|
| 条件判断遗漏 | `if a > 0` 但未考虑 `a == 0`；`if data then` 但 `data` 可能是空表 `{}` |
| 边界条件 | 数组越界、除零、空字符串、负值场景 |
| 时序假设 | 假设 A 一定在 B 之前执行，但没有保证机制 |
| 状态残留 | 切换界面/退出时未清理 timer、listener、cache |
| 比较类型混用 | `value == 0` 但 value 可能是字符串 `"0"` |
| nil 传递链 | 函数 A 返回 nil → 函数 B 不检查 → 函数 C 崩溃 |

### 维度 3：📝 日志（Logging）

日志是最容易被忽视但出问题时最致命的。检查以下：

#### 3a. 关键路径是否有日志

```
- 函数入口：重要函数的入口参数是否记录？
- 分支关键节点：if/else 的关键分支是否有日志区分？
- 外部依赖调用：协议发送、配置表读取、文件 IO 的返回值是否记录？
- 异常/错误路径：错误处理分支是否有日志？
```

判断标准：**如果这个函数出 bug 了，现有的日志能不能定位到是哪一步出了问题？**

#### 3b. 是否有过度日志

```
- for 循环内是否全量打印日志？（如非必要，只建议在循环的 if 分支中打印）
- 高频函数（每帧/每秒调用）是否有不必要的日志？
- 是否连续多行日志可以合并为 1-2 行？
```

判断标准：**日志的粒度应该让排查问题时能定位，而非淹没在噪声中。**
如果在循环中全量打印，3 轮循环后日志文件就几十 MB，真正关键的信息反而找不到了。

具体示例：

```lua
-- ❌ 循环内全量打印——100 个玩家就是 100 条日志
for _, player in ipairs(playerList) do
    log(bqlog.format("[...] processing player uid=%s level=%s", player.uid, player.level))
    self:ProcessPlayer(player)
end

-- ✅ 循环内只在关键/异常分支打印
for _, player in ipairs(playerList) do
    if player.level >= MAX_LEVEL then
        log(bqlog.format("[...] high level player uid=%s level=%s", player.uid, player.level))
    end
    self:ProcessPlayer(player)
end

-- ✅ 或者不在循环内打，循环前后汇总
log(bqlog.format("[...] start processing %s players", #playerList))
for _, player in ipairs(playerList) do
    self:ProcessPlayer(player)
end
log(bqlog.format("[...] finish processing %s players, success=%s", #playerList, count))
```

### 维度 4：🔧 API 选择（API Choice）

检查本次改动中是否使用了**应该被项目封装替代**的标准库/原始 API：

| ❌ 不推荐 | ✅ 项目封装 | 为什么 |
|-----------|-----------|--------|
| `os.time()` | `TimeUtil.GetServerTimeInSec()` | 客户端时间 ≠ 服务器时间 |
| `string.split(s, sep)` | `StringUtil.Split(s, sep)` | 需要检查 Lua 版本兼容 |
| `table.sort(t)` | `TableUtil.SortByKey(t, key)` | 稳定的排序 + nil 安全 |
| 直接 `self:AddTimer(1, true)` | 通过 TimerUtil 统一管理 | 便于统一清理 |

**检查方式**：对比 api-registry 的 `_flat_index.md`，看本次 diff 中是否有可以用注册表中 API 替代的标准库调用。

---

## 审查输出格式

```markdown
## 🔍 Code Review：{简述审查范围（改了哪些文件）}

### 🔴 阻塞项（{N} 个）
{如果没有，写"✅ 无阻塞项"}
| # | 文件:行号 | 问题 | 修复建议 |
|---|----------|------|---------|
| 1 | xxx.lua:42 | {具体问题} | {怎么改} |

### 🟡 逻辑问题（{N} 个）
{如果没有，写"✅ 未发现逻辑问题"}
| # | 文件:行号 | 问题 | 修复建议 |
|---|----------|------|---------|
| 1 | xxx.lua:58 | {具体场景下的异常行为} | {怎么改} |

### 📝 日志检查
| 检查项 | 状态 |
|--------|------|
| 关键路径日志 | ✅ 完整 / ⚠️ 缺少 {某处} 的日志 |
| 循环内过度日志 | ✅ 合理 / ⚠️ 第 {N} 行循环内全量打印 |
| 日志内容质量 | ✅ 清晰 / 💡 {建议} |

### 🔧 API 选择
{如果没有不当的选择，写"✅ 已正确使用项目封装接口"}
| 文件:行号 | ❌ 当前使用 | ✅ 应改为 |
|----------|-----------|---------|
| xxx.lua:15 | `os.time()` | `TimeUtil.GetServerTimeInSec()` |

### 📊 审查总结
- 审查文件：{N} 个
- 阻塞项：{N} 个（必须修复）
- 逻辑问题：{N} 个（建议修复）
- 日志问题：{N} 个
- API 选择问题：{N} 个
- 整体评估：✅ 可以合入 / ⚠️ 建议修复后再合入 / 🔴 有阻塞项不可合入
```

---

## 轻量模式（quick-fix 使用）

quick-fix 改动小（≤30 行 / ≤2 文件），使用轻量审查：

```
## 🔍 快速审查
{逐行指出问题，不区分维度，只写有问题的部分}
```

---

## 关键原则

1. **只审 diff，不审已有代码**——旧代码的债是另一个任务
2. **阻塞项必须明确**——不要用"建议""可能""考虑"，阻塞项就是阻塞项
3. **日志检查不要浮于表面**——具体指出"第 X 行缺少日志"、"第 Y 行循环内全量打印"
4. **API 选择要和注册表交叉验证**——这是 api-registry 的核心使用场景
5. **审查 ≠ 批评**——对于风格偏好问题（如变量命名），除非违反了 experience-repo 中的明确规则，否则不做评论

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| api-registry | 审查 API 选择时交叉验证注册表 |
| experience-repo | 审查风格时参考经验库 |
| logic-dev / ui-dev / code-refactor / quick-fix | 实现后调用本 skill 自检 |
