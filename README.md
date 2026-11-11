# CodeAce

单用户个人刷题工作台。Nuxt 4 + Vue 3 + shadcn-vue，PostgreSQL/pgvector 持久化，独立 Docker 沙箱运行 Python 3、C++17 与 NumPy/PyTorch CPU。

支持分类题库、搜索筛选、题面/数学公式、函数与 ACM 两种输入方式、代码草稿、真实运行判题、提交快照、收藏、Markdown 笔记、错题筛选、学习统计，以及题目后台和鉴权批量导入。

## 本地启动

需要 Node.js 24、pnpm 10、Docker Engine 和 Docker Compose。以下命令在仓库根目录执行：

```bash
pnpm install --frozen-lockfile
pnpm env:init
docker compose up -d postgres
pnpm db:migrate
pnpm admin:init
pnpm source:sync
pnpm db:seed
docker build -f sandbox/runtime.Dockerfile -t codeace-runtime:local .
docker compose up -d --build sandbox
pnpm dev --port 3000
```

访问 <http://localhost:3000>。初始用户名和密码位于本机 `.env` 的 `ADMIN_USERNAME`、`ADMIN_PASSWORD`；`env:init` 生成随机凭证，不会覆盖已有 `.env`。不要提交 `.env`。修改管理员密码后运行 `pnpm admin:init`，已有会话会失效。

数据库默认仅绑定 `127.0.0.1:5436`，沙箱控制接口仅绑定 `127.0.0.1:4311`。PostgreSQL 18 数据挂载父目录 `/var/lib/postgresql`，保存在 Compose 命名卷 `codeace_postgres_data`；`docker compose down` 不删除数据卷。

首次构建运行镜像需下载 NumPy 与 PyTorch CPU。`POSTGRES_IMAGE` 可替换为可访问的 pgvector PostgreSQL 18 镜像；默认参考同机项目使用的镜像仓库。

## 生产构建与 Compose 应用

```bash
pnpm build
node --env-file=.env .output/server/index.mjs
```

或构建整个应用：

```bash
docker compose --profile app up -d --build
```

Compose 应用使用同一数据库卷和执行服务。首次仍需按上文迁移数据库、初始化管理员、导入题库和构建 `codeace-runtime:local`。应用容器不挂载 Docker socket；只有沙箱控制服务持有调度权限。

在 HTTPS 反向代理后使用时，将 `.env` 中 `NUXT_COOKIE_SECURE=true`。本项目不会自动部署到公网。

## 离线题库

发行目录包含 43 道独立算法练习、65 道独立深度学习练习，以及 Python3/C++17 入门示例。题面、参考实现和用例保存在 `database/hot-*` 与 `database/deep-*`，可离线重建，不需要第三方账号。

```bash
pnpm source:sync
pnpm db:seed
```

种子导入保留手工编辑与个人草稿、笔记、收藏、提交历史。已有数据库不会因更新发行目录而删除历史题目；新安装只导入当前发行目录。算法与深度学习练习使用 Python3，通用题可配置 Python3/C++17。

## API 导入

`POST /api/import` 接受 1–100 道题，支持当前登录 cookie，或机器密钥 `Authorization: Bearer <NUXT_IMPORT_KEY>`。请求体上限 3 MB。建议先 `dryRun: true` 检查格式。

```json
{
  "dryRun": true,
  "problems": [
    {
      "source": "personal",
      "sourceId": "sum-two-v1",
      "title": "两整数求和",
      "category": "通用算法",
      "difficulty": "简单",
      "description": "输入两个整数，输出它们的和。",
      "published": true,
      "modes": {
        "acm": {
          "templates": {
            "python3": "a, b = map(int, input().split())\n# 输出答案\n"
          },
          "cases": [
            {"input": "1 2", "expected": "3", "compare": "tokens", "hidden": false},
            {"input": "-5 8", "expected": "3", "compare": "tokens", "hidden": true}
          ]
        }
      }
    }
  ]
}
```

完整数据契约见 `shared/problem.ts`。返回 `created`、`updated`、`skipped`、`failed` 统计和逐题结果；非法条目不会影响其他有效条目，题目键为 `(source, sourceId)`。重复内容跳过，本地手改冲突保留并报告。后台也提供 JSON 粘贴、预检查、导入结果和完整配置编辑。

函数模式还可配置 `prelude`、`harness`、`inputHelp` 和逐用例 `harness`。调用脚本与用户代码均只在沙箱运行，标准答案不传给运行容器。公开用例 `hidden=false` 用于样例运行，正式提交使用全部用例。隐藏用例不是源站未提供数据的复原，所有用例均以实际来源或独立编写为准。

支持 `exact`、`tokens`、`unordered_tokens`、`json`、`unordered_json`、`unordered_nested`、`balanced_bst`、`float_tokens` 比较方式。浮点比较保留数组形状，按 `absTolerance + relTolerance * abs(expected)` 判断；NaN/Infinity 不通过。`unordered_nested` 用于字母异位词分组这类内外层都可无序的答案。

## 执行与安全边界

Nuxt 通过私有鉴权接口调用沙箱服务，最多同时执行 2 个任务，应用待处理上限 8 个。单次任务总墙钟预算 150 秒，客户端断开后取消任务并释放执行槽。每个用例使用单独容器，断网、非 root、只读根文件系统、禁提权、清空 capabilities，限制 CPU、内存、进程数量、临时盘、输出和墙钟时间。C++ 使用 C++17 编译。

判题结果由执行器比较实际输出生成；用户打印 `{"status":"AC"}` 不会改变结果。支持 AC、WA、CE、RE、TLE、MLE、OLE 和 SYSTEM_ERROR。自定义输入没有标准答案时返回 FINISHED，不计入正式通过进度。正式提交保存题目版本、代码与用例快照；服务重启会将中断任务明确标为 SYSTEM_ERROR。

Docker 控制服务属于高权限组件，只部署在自己的可信主机上，控制接口不要向公网开放。沙箱不是面向不受信任公众的多租户判题集群。

## 验证

先启动数据库、沙箱和应用，再执行：

```bash
pnpm typecheck
pnpm test:catalog
pnpm test
pnpm exec playwright install chromium
pnpm test:e2e
pnpm build
```

`pnpm test` 包含真实 HTTP、PostgreSQL 与 Docker 集成测试，不以 mock 替代判题；默认访问 `http://127.0.0.1:3000`。可通过 `TEST_BASE_URL` 切换到构建后的应用。测试读取 `.env` 中的管理员和导入密钥，不在日志输出密码。E2E 覆盖登录、筛选、函数/ACM 执行、正式提交与历史、草稿/笔记恢复、后台导入编辑和手机布局。

Playwright 失败截图与 trace 位于 `test-results/`，HTML 报告位于 `playwright-report/`，均不纳入 Git。推荐在 `pnpm build` 后执行 `pnpm test:stack`：自动创建随机命名的临时数据库，迁移/导入题库、启动构建后的应用并执行全部单元、集成和 E2E；最后停止测试应用、删除本次临时数据库，个人数据不会被修改。默认测试应用端口 3010，可用 TEST_APP_PORT 覆盖。

## 备份

```bash
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > codeace-backup.dump
```

备份包含个人代码与笔记，请自行保存到可信位置。恢复前停止写入，并先验证备份；不要将其他 PostgreSQL 版本的数据目录直接挂载到当前实例。
