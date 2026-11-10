# Outcome
构建供本人使用的 CodeAce 单用户刷题网站，参考 CodeKy 的题库、题目详情、代码工作台和提交记录交互，形成可持续导入题目、真实执行判题和追踪学习进度的完整闭环。

# Scope
单管理员账户同时用于刷题和后台，无公开注册。中文界面，以题库为首页；提供分类题单、关键词搜索、难度/标签/完成状态筛选、分页、题目详情、题解、代码编辑、函数/ACM 输入、运行/提交、记录与代码回看、草稿、收藏、笔记、错题列表和个人进度统计。后台管理题目、分类、用例、模板、题解、资源限制与发布状态，支持手动编辑与鉴权 JSON API 批量导入。

初始参考目录来自用户提供的 CodeKy 登录 Profile；用户随后明确允许使用其他公开题库和独立练习补齐题目。保留已取得的有效快照，不再访问 CodeKy。目标分类和数量仍是：来源目录中 Hot 100 70 道、Hot100 30 道合并为 100 道，深度学习 68 道，共 168 条目标目录。题库由有效离线快照、可用公开资料和独立编写的同主题练习组成，标明实际来源。实际导入以完整题面和有效判题数据为准，逐题报告完整、不可访问、限流及待补齐，不将目录条目计为可刷题。保留来源 URL/编号，重复同步幂等，不覆盖个人代码、记录和笔记。补充通用 Python3/C++17 示例以验收语言功能。题解仅同步可读取正文，缺失时明确展示暂无题解并允许个人编写。

## 目录结构
### 新建
- app/ — Nuxt 页面、布局、shadcn-vue 组件、题库、编辑器、记录、个人进度及管理界面。
- server/ — 单用户认证、题库与记录 API、导入校验、持久化和判题任务编排。
- shared/ — 题目、模板、用例、执行与导入结果的数据契约。
- database/ — 数据迁移、vector 扩展、种子题库与来源清单。
- sandbox/ — 独立 Docker 执行器、Python/NumPy/PyTorch CPU 与 C++17 镜像及资源限制。
- scripts/ — 初始化、题库同步、限速断点与数据质量审计工具。
- tests/ — 导入、认证、判题集成测试和 pnpm Playwright E2E。
- docker-compose.yml、.env.example — pgvector PostgreSQL、沙箱及应用启动配置。
- package.json、pnpm-lock.yaml、nuxt.config.ts、components.json — pnpm、Nuxt、shadcn-vue 工程配置。
### 修改
- README.md — 本地部署、账户初始化、导入格式、沙箱与测试说明。

## Source coverage
覆盖边界是与个人刷题直接有关的题库列表、题目详情、代码工作台、题解和提交记录；后台、导入和个人学习辅助按用户需求补充。商业社区与其他学习产品不在本次模仿边界。题目数据是待导入的运行数据，不把全部题目的正文作为产品需求；在 Build 阶段按清单完整核对读取与转换结果。

| 来源条目与位置 | 读取状态 | 需要保留的内容 | Spec 位置 | 验收 ID | 覆盖状态 | 理由或替代关系 |
| --- | --- | --- | --- | --- | --- | --- |
| /problems 题单与列表 | complete | 分类题单、搜索、难度、标签、完成状态、分页与进度 | specs/personal-practice/spec.md §题库 | A2 | covered | 个人刷题入口 |
| /problem/1472 题面 | complete | Markdown/公式、输入输出、样例、限制、提示、相似题与前后题导航 | specs/personal-practice/spec.md §详情 | A3 | covered | 题目详情参考 |
| /problem/1472 代码工作台 | complete | 左右分栏、语言和模式切换、代码保存、运行/提交、输入输出面板 | specs/personal-practice/spec.md §执行 | A4 | covered | 核心刷题交互 |
| /problem/1472 提交记录页 | complete | 判题状态、执行用时、内存、提交时间及代码回看；空记录提示 | specs/personal-practice/spec.md §记录 | A5 | covered | 当前源账户无提交记录，不生成或迁移第三方个人记录 |
| /problem/1472 题解页及 solutions 接口 | complete | 题解正文入口与个人编写；接口有 detail_locked 的官方题解和可读用户题解 | specs/personal-practice/spec.md §详情 | A3 | covered | 仅导入可读正文，保留来源，缺失显示暂无题解 |
| /api/problems?list=1 当前账户目录 | complete | Hot 100/Hot100 合计 100 条、深度学习 68 条及分类、编号、难度 | specs/personal-practice/spec.md §来源同步 | A8 | covered | 合并分类别名，UI 125 条含额外基础题的判断被接口目录替代 |
| /api/problems/1472、1320、1467、1471 抽查 | complete | ACM/函数模板、参数、示例、classic/code_input 用例、无序和浮点容差比较 | specs/personal-practice/spec.md §执行与来源同步 | A9 | covered | 导入器需兼容真实来源格式，不能仅导入题面 |
| 其余目标题目正文与用例 | partial | 168 条目标目录的可访问题目数据 | specs/personal-practice/spec.md §来源同步 | A8 | background | 运行数据在 Build 同步验收，非 Shape 需求来源；当前已存 60 道完整含用例快照，22 次 429、2 条 login_required，已暂停请求 |
| 主页竞赛、会员、AI 调试、协作、记忆网络、排名、商业与社区入口 | complete | 不复制这些独立产品流程 | specs/personal-practice/spec.md §边界 | — | non-goal | 用户明确选择个人刷题相关范围；个人错题与笔记另行提供，不引入间隔复习算法 |
| /proj/clothes-design-miniprogram/web/docker-compose.yml | complete | pgvector PostgreSQL 18、环境变量、父目录持久化和健康检查 | — | — | background | 数据库部署实现参考，不需要复制其旧集群迁移逻辑 |

# Non-goals
公开注册、多用户隔离、竞赛、会员/支付、排行榜、社交评论、实时协作、AI 提示与调试、自动间隔复习、GPU/CUDA/JAX/TensorFlow 执行、第三方个人历史迁移、生产公网部署及 Git 推送不包含在本次范围。pgvector 扩展会启用，不额外构建语义检索产品。题库内容导入不绕过源站权限；不把来源隐藏或缺失内容伪造为已同步。

# Acceptance examples
- A1：使用 pnpm 安装启动 Nuxt + shadcn-vue；Docker Compose 启动 pgvector PostgreSQL，vector 扩展可查询，数据库重启后题目及个人数据保留。
- A2：题库支持 Hot100/深度学习/通用分类、搜索、难度/标签/完成状态筛选、分页；点击题目进入对应详情并保持返回筛选上下文。
- A3：详情正确渲染题面、代码、公式、样例、输入输出、提示和限制；可切换题解、提交记录，导航前后题和相似题；缺失题解明确提示且可个人编辑。
- A4：编辑器可切换语言与已配置模式，运行样例或自定义输入、正式提交判题；Hot100/深度学习只允许 Python3，通用题可 Python3/C++17；前后端均拒绝不支持的组合，草稿按题目/模式/语言独立保存。
- A5：提交列表和单题记录显示时间、语言、模式、结果、用时、内存和用例通过数，可回看提交代码、错误原因及允许展示的失败输入；运行样例不计入正式解题进度。
- A6：收藏、个人笔记、未通过题错题列表、通过进度及按日练习统计真实持久化；错误尝试不会抹去历史已通过状态，成功后错题状态可正确更新。
- A7：单管理员账户可登录退出，无公开注册；后台和数据接口受保护；后台可管理分类、题目、模板、用例、题解、限制及发布状态，未发布题不出现在普通题库。
- A8：对 100 道 Hot100 与 68 道深度学习目标目录同步当前可访问完整内容，保留来源和别名去重；提供逐题导入清单、可刷数量、锁定/限流/待补齐报告及可重试断点；幂等重导入不破坏个人数据，不能以目录数声称可刷题数。
- A9：真实来源 classic、code_input、function_template_map、input_by_lang 可转换成运行契约；NumPy/PyTorch CPU 函数题、链表/二叉树/设计类题及原地修改题有对应执行与序列化处理，无序比较和浮点容差保持题意；不能适配的条目进入待补齐而非发布；通用 ACM C++17 和 Python3 示例真实可执行。
- A10：鉴权导入 API 支持批量 JSON、dry-run、来源幂等键、逐题错误和成功统计；错误格式和未授权请求被拒绝；导入含隐藏用例、模板和题解后可在后台编辑并实际刷题。
- A11：用户代码仅在独立 Docker 沙箱中执行，断网、非 root、只读根文件系统、临时工作目录、CPU/内存/进程/输出/墙钟限制及退出清理有效；判题能区分 AC、WA、CE、RE、TLE、MLE 和服务不可用，源程序输出不能冒充判题状态。
- A12：pnpm Playwright E2E 覆盖登录、筛选进入题目、运行与提交、记录恢复、收藏笔记、后台编辑与 API 导入；后端集成测试覆盖判题比较、语言约束、输入校验、认证和沙箱限制；浏览器人工检查主要页面和窄屏，交付真实运行命令、结果和剩余限制。

# Constraints and invariants
pnpm 管理依赖；Nuxt + shadcn-vue；pgvector PostgreSQL 18 通过 Docker Compose 启动；Python3、C++17。Hot100 和深度学习仅 Python3，Python 环境预装 NumPy 与 PyTorch CPU。两种输入风格由每题模板/用例声明，未配置的模式不可选择；平台支持两种，不把没有 ACM 输入规格的题目伪装为 ACM 可用。导入来源的可执行用例脚本同样只能在沙箱执行。认证凭证不进入仓库、日志或导入产物。

# Decisions
- 用户已确认：模仿题列表、题目详情、刷题记录等刷题相关页面；题库可爬取账户开放的 Hot100 和深度学习内容；单用户个人使用。
- 账户由环境变量/初始化命令设置，密码哈希入库、HttpOnly 会话；单账户拥有全部个人和管理权限。
- 采用自建轻量 Docker 执行服务而非依赖远程公共判题 API，便于适配源站函数 harness 和 PyTorch CPU；Web 服务不持有用户代码执行权限，Docker 控制面只由执行器使用。
- 本 change 保持单个 Native change：题目契约、导入转换、编辑器与判题执行紧密相连，首版串行集成比拆分子 change 更易保证真实来源兼容。
- 用户报告 CodeKy 账号因采集被临时限制 24 小时，并明确授权改用互联网其他题库；因此停止该站全部请求，在线采集脚本默认拒绝执行。题名清单已完整保存，缺失题目改用独立编写的同主题练习，并标注真实来源。此为用户明确授权的数据来源选择，保留 100 道 Hot100 与 68 道深度学习的目标及原有功能验收。

# Verification expectations
以真实 PostgreSQL 与 Docker 执行为准，不以 mock 通过替代判题。保留逐题数据审计和代表性函数、ACM、NumPy/PyTorch、链表/树/设计类适配验证；遇源站权限或限流只报告真实导入覆盖，继续完成不依赖来源访问的实现。若因外部条件无法取得全部题目，在验收结论中明确目标目录、可刷数量、待补齐条目与原因，等待用户接受实际结果。
