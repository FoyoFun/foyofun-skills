# logic 层标准文件结构（Lua 参考实现）

> 这是 logic 文件的标准分区结构与各分区职责。分区顺序、章节角色是**通用标准**；
> 具体命名（方法名、事件 API、定时器 API）以项目适配表
> （`<project>/.agents/adaptation.md`）和目标模块既成风格为准。
> 已修正原稿演示笔误（`self.dats` → `self.datas`，`logic.Create` → `logic.E_TYPE.Create`）。

```lua
----------定义常量----------
logic.C_MAX_NUM = 10
logic.E_TYPE = {
    Create = 1,
    Join = 2,
}
logic.TAB_LIST = {
    {type = logic.E_TYPE.Create, loc_id = 10001},
    {type = logic.E_TYPE.Join, loc_id = 10002},
}

----------框架层----------
function logic:ctor()

end

function logic:DefineAndReset()
    -- 后台原始数据
    self.original_datas = nil

    -- 加工缓存数据：有些数据加工会有耗时，所以会缓存起来，避免重复加工
    -- 但这类数据要注意控制刷新逻辑，一般在出现性能瓶颈之前，是绝对不建议缓存的
    -- 控制刷新的方式有很多种，以下演示一种（脏标记），实际根据需要而定
    self.datas = nil

    -- 定义变量
    self.timerA = nil
    self.need_refresh_datas = {}
end

function logic:OnRegister()
    -- 注册事件系统事件，有时也会对其他 logic 有依赖，按需注册
    self:RegisterEvent(EVENT_TYPE, EVENT_NAME_A, self.OnEvent, self)
end

----------外部调用接口----------
-- 按需添加外部调用的接口，这类接口一定要做好防御性编程，避免阻塞业务
function logic:GetDatas(uid)
    if self.datas and self.datas[uid] and not self.need_refresh_datas[uid] then
        return self.datas[uid]
    end

    -- 防御性编程
    if not self.original_datas or not self.original_datas[uid] then
        return {}
    end

    -- 数据加工
    self:ProcessDatas(uid)

    -- 返回数据
    return self.datas[uid]
end

----------协议收发----------
function logic:send_datas_req()
    -- 调用 handler 发送协议请求
end

--- 一般建议，如果是有类似 uid 这类 key 的协议，缓存时按照 uid 映射缓存，避免数据争抢
function logic:on_datas_rsp(uid, datas)
    self.original_datas[uid] = datas
    self.need_refresh_datas[uid] = true
    EVENT_SYSTEM:PostEvent(EVENT_TYPE, EVENT_NAME_B)
end

----------响应事件函数----------
function logic:OnEvent(event_type, event_name, ...)
    -- 处理事件
end

----------内部函数----------
--- 有的时候 logic 也需要定时器，例如定时弹窗之类的
--- （需求与界面是否打开无关 → 归 logic；只存在于界面打开期间 → 归 ui）
function logic:StartTimerA()
    if self.timerA then
        self:RemoveTimer(self.timerA)
        self.timerA = nil
    end

    -- 一般建议将定时器的回调函数写在这里，除非是很复杂的逻辑
    local func = function()
        -- 定时器逻辑
        self:ShowPop()
    end

    -- 开启定时器A
    self.timerA = self:AddTimer(func, 1)
end

--- 数据加工也是按需添加，一般如果简单的加工，且不多处调用，就不需要额外的函数了，
--- 避免跳转过深导致阅读困难
--- 一般内部函数建议是面向过程的，也就是不传参的，也不返回的
--- 这里当作每次加工都开销巨大，且数据复杂，所以传递一个 uid 来按需加工
--- 虽然建议不传参也不返回，但实际开发中需根据实际情况而定
function logic:ProcessDatas(uid)
    if not self.datas then
        self.datas = {}
    end

    -- 数据加工
    -- self.datas[uid] = ...

    -- 恢复
    self.need_refresh_datas[uid] = false
end

--- 这里只是做个演示，像这么简单的一般不会包装成函数，
--- 只有存在多处调用或逻辑比较复杂的情况，才额外包装成内部函数
function logic:ShowPop()
    -- 显示弹窗（系统级 UI：只 Show，不触碰其内部逻辑）
end
```

## 分区职责速查

| 分区 | 职责 | 规则要点 |
|------|------|---------|
| 定义常量 | 常量/枚举/静态配置 | 与 ui 共用的常量放独立 macro 文件，不两侧复制 |
| 框架层 | ctor / DefineAndReset / OnRegister | 状态声明与重置合一；注册事件在此 |
| 外部调用接口 | 给 ui/其他模块的门面 | 防御性编程，不让调用方阻塞 |
| 协议收发 | send_xxx_req / on_xxx_rsp | 命名惯例按模块既成风格（本例 snake_case）；数据先落地后派发 |
| 响应事件函数 | OnEvent | 只做分发或简短处理，长逻辑下沉内部函数 |
| 内部函数 | 面向过程的实现细节 | 简单且单处调用的不包装；默认不传参不返回，按需放宽 |

## 其他语言的适配要点

结构标准（分区 + 职责）不变，语法与机制按语言/框架调整，以项目适配表为准：

- **C#**：类字段区 = 定义变量；事件可用 C# event / Action 回调代替事件系统，
  `IDisposable.Dispose` 承担 OnClose 式清理；协议收发通常是 async/await 或回调，
  "send 直连 on"闭环改为直接调用响应处理方法喂假数据。
- **C++**：手动管理生命周期（RAII 析构对应清理）；事件用观察者注册表或信号槽；
  特别注意定时器与回调的悬挂检查（this 捕获失效是 C++ 特有的崩溃源）。
- **无框架个人项目**：没有 ModuleManager 就用静态类/单例/服务注册表；
  没有 DefineAndReset 就写显式的 Reset()；没有兜底注销就**必须**手写成对的
  注册/注销——红线不因项目小而豁免。
