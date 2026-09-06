# ui 层标准文件结构（Lua 参考实现）

> 这是 UI 文件的标准分区结构与各分区职责。分区顺序、章节角色是**通用标准**；
> 具体生命周期方法名（OnInitialized/OnShow 等）、控件 API 以项目适配表
> （`<project>/.agents/adaptation.md`）和目标模块既成风格为准。
> 已修正原稿演示笔误（`ui.Create` → `ui.E_TYPE.Create`）。

```lua
----------定义常量----------
ui.C_MAX_NUM = 10
ui.E_TYPE = {
    Create = 1,
    Join = 2,
}
ui.TAB_LIST = {
    {type = ui.E_TYPE.Create, loc_id = 10001},
    {type = ui.E_TYPE.Join, loc_id = 10002},
}

----------框架层----------
function ui:ctor(_, uid)
    -- 接收参数
    self.uid = uid

    -- 定义变量
    self.datas = nil
    self.timerA = nil
end

function ui:OnInitialized()
    -- 初始化特定UI组件
    self.LoopScrollBox_0 = self:InitLoopScrollBox(self.UIRoot.LoopScrollBox_0)

    -- 初始化特定不需要异步更新的变量
    local logic = ModuleManager.GetModule(ModuleManager.Config.logic)
    self.datas = logic:GetDatas(self.uid)
end

function ui:OnRegister()
    -- 注册事件系统事件
    self:RegisterEvent(EVENT_TYPE, EVENT_NAME, self.OnEvent, self)

    -- 注册控件系统事件
    self:RegisterEvent(self.UIRoot.Button_Add, "OnClick", self.OnClickButton_Add, self)
    self:RegisterEvent(self.LoopScrollBox_0, "OnRefresh", self.OnRefreshLoopScrollBox_0, self)
end

function ui:OnPostInitialized()
    -- 初始化UI
    self:InitUI()
end

function ui:OnShow()
    -- 更新UI
    self:UpdateUI()
    -- 协议拉取（放 OnShow 而非 OnPostInitialized：界面可重复 Show，
    -- 每次进入都要刷新；重复请求由 logic 层 Ensure 去重兜住）
    self:RequestWhenOpen()
    -- 开启定时器（仅"界面打开期才需要"的定时器归 ui）
    self:StartTimerA()
end

function ui:OnClose()
    -- 按需释放，例如 timer
    if self.timerA then
        self:RemoveTimer(self.timerA)
        self.timerA = nil
    end
    -- 事件注销是否需要手写，看项目适配表；不兜底的项目必须在这里成对注销
end

----------响应控件函数----------
function ui:OnClickButton_Add()
    -- 处理点击事件
    -- 可以是Update，比如UpdateButton_Add
    -- 可以是Request，比如RequestB
    -- 也可以是其他逻辑
end

function ui:OnRefreshLoopScrollBox_0(widget, index)
    -- 处理刷新事件
    -- 一般就是刷新widget
end

----------响应事件函数----------
function ui:OnEvent(event_type, event_name, ...)
    -- 处理事件
    -- 可以是Update，UpdateLoopScrollBox_0
    -- 可以是Request，RequestA（如果协议之间有依赖的话）
    -- 也可以是其他逻辑
    -- 注意：只做分发或简短处理，不要在这里堆业务；禁止事件自激励环
end

----------UI刷新----------
function ui:InitUI()
    -- 基本不会动态刷新的UI组件的初始化
    self.UIRoot.Text_Title:SetText("Title")
end

function ui:UpdateUI()
    -- 全量刷新入口：将各组件刷新包进函数中
    self:UpdateButton_Add()
    self:UpdateLoopScrollBox_0()
end

function ui:UpdateButton_Add()
    -- 获取数据

    -- 防御性编程

    -- 对应组件的刷新逻辑
end

function ui:UpdateLoopScrollBox_0()
    -- 获取数据

    -- 防御性编程

    -- 对应组件的刷新逻辑
    self.LoopScrollBox_0:SetData(self.datas)
end

--- 比较特殊的刷新，按需添加
function ui:RefreshLoopScrollBox_0()
    -- 由于 LoopScrollBox_0 SetData 的成本高，有时只是要触发里面的 widget 刷新，
    -- 而不是要对 datas 进行变更，可以增加这个逻辑
    self.LoopScrollBox_0:Refresh()
end

----------协议请求----------
function ui:RequestWhenOpen()
    -- 打开UI时触发的数据需求（经 logic 的 Ensure 型接口，不直接发协议）
    self:RequestA()
end

function ui:RequestA()
    -- 表达数据需求（调用 logic 门面接口）
end

function ui:RequestB()
end

----------外部调用----------
--- 部分UI会有外部调用的接口，例如通用的物品详情UI，按需添加
function ui:SetData(datas)
    self.datas = datas
    self:UpdateLoopScrollBox_0()
end

----------内部函数----------
function ui:StartTimerA()
    if self.timerA then
        self:RemoveTimer(self.timerA)
        self.timerA = nil
    end

    -- 一般建议将定时器的回调函数写在这里，除非是很复杂的逻辑
    local func = function()
        -- 定时器逻辑
        self:RequestA()
    end

    -- 开启定时器A
    self.timerA = self:AddTimer(func, 1)
end

--- 这里只是做个演示，像这么简单的一般不会包装成函数，
--- 只有存在多处调用或逻辑比较复杂的情况，才额外包装成内部函数
function ui:GetTabs()
    return self.TAB_LIST
end
```

## 分区职责速查

| 分区 | 职责 | 规则要点 |
|------|------|---------|
| 定义常量 | UI 本地常量/枚举 | 与 logic 共用的放独立 macro 文件，不两侧复制 |
| 框架层 | ctor / OnInitialized / OnRegister / OnPostInitialized / OnShow / OnClose | 控件绑定集中初始化；打开期请求在 OnShow；清理在 OnClose |
| 响应控件函数 | OnXxx 控件回调 | 简短；转发到 Update*/Request*/意图 |
| 响应事件函数 | OnEvent 分发 | 只分发不堆逻辑 |
| UI刷新 | InitUI / UpdateUI / Update*_ / Refresh*_ | 三层按成本选；Update* 三步式 |
| 协议请求 | Request* | 只表达需求（走 logic 门面），不直接收发 |
| 外部调用 | SetData 等 | 通用组件对外接口，参数简单直观 |
| 内部函数 | 按需 | 简单单处调用的不包装 |

## 其他语言的适配要点

- **C#（Unity 等）**：`Awake/OnEnable/OnDisable/OnDestroy` 对应
  ctor/OnShow/OnClose 语义；事件用 UnityEvent/C# event，**OnDisable 必须解绑**
  （Unity 无兜底）；协程要在 OnDisable 停止，防止销毁后继续跑（异步防御）。
- **C++（UE 等）**：`BeginPlay/EndPlay` 对应；动态多播委托绑定/解绑成对
  （`AddDynamic`/`RemoveDynamic`）；定时器句柄在 EndPlay 清空；
  回调捕获 this 前确认对象存活。
- **无框架个人项目**：没有生命周期钩子就自建显式的 Init/Open/Close 三段；
  没有事件系统就手写观察者列表，**注册注销成对是红线**，不因项目小而豁免；
  异步防御退化为"回调前判空销毁标记"。
