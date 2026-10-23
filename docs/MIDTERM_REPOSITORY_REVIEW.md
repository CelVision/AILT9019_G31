# G31 Midterm 仓库扫描与个人贡献记录

扫描日期：2026-10-23，香港时间。仓库：<https://github.com/CelVision/AILT9019_G31>。

后续更新：本报告记录的是 `3726563` 基线。新的 `codex/deployment-setup` 分支已补入部署实现并修正文档启动方式，见 [部署指南](DEPLOYMENT.md) 和 [changelog](../CHANGELOG.md)。下面“本次未恢复/未实现”的描述保留为原扫描结论；不代表后续部署分支的文件清单。前端无障碍功能仍未恢复。

项目正式名称为 **ConnectFour Connect**。本次检查当前主分支、全部已获取的远程分支、相关提交差异、前后端代码、部署模板和测试。以下区分代码事实、本次实测、历史记录和建议，不把团队任务板的勾选直接当作验收结果。

## 1 结论

主分支已经包含 Connect Four 核心逻辑、WebSocket 匹配和 GLM/PvE 处理代码，现有 26 个 Python 测试全部通过。它仍是未完成的原型，不能据此声称公网部署完成或全部功能可用。

你的 accessibility / distribution 工作有明确提交证据，但已被撤销：

| 对象 | 提交 | 状态 |
|---|---|---|
| 当前 main | `3726563` | 当前可检查的团队代码 |
| 你的实现 | `ca0b19e` | Git 作者为 Scott Xiang；有无障碍、部署工具和测试代码 |
| 随后的撤销 | `1ca4377` | 完整撤销上述改动；提交说明未给出原因 |
| accessibility 分支最新版本 | `1ca4377` | 与 main 的跟踪文件内容完全相同 |

完整提交链接及功能清单见 [CHANGELOG](../CHANGELOG.md)。本次新增的是文档和测试证据，没有恢复已撤销功能，也没有将其他人的主分支代码归为你的个人贡献。

## 2 你已完成的工作可以怎样写

建议个人贡献栏使用以下英文，准确区分完成开发与当前集成状态：

> Scott Xiang: Implemented an accessibility and distribution prototype in commit ca0b19e, including keyboard/touch controls, screen-reader board information, Docker/Compose configuration, an endpoint checker, and browser tests. The change was later reverted in 1ca4377 and is not active in the current build; integration and public deployment remain outstanding.

若一页表空间较紧，可以用：

> Scott Xiang: Built accessibility controls, deployment tooling and browser tests (ca0b19e). Later reverted (1ca4377); not in the current build. Public deployment remains unverified.

历史 worklog 写了 26 个 Python 测试和 18 个浏览器测试通过。此次只独立重跑了当前 main 的 Python 测试，不能写成此次也重跑了 18 个浏览器测试。没有完整证据前，也不应写“已上线 VPS”“通过 WCAG 认证”或“已合并至 main”。

## 3 当前功能与证据

| 内容 | 证据 | 当前可表述的结论 |
|---|---|---|
| 游戏规则 | `server/app/game_engine.py`、现有引擎测试 | 有实现，相关现有测试通过 |
| 页面和静态资源 | `server/app/main.py`、`tests/test_app_smoke.py` | 后端同源提供页面，HTTP 测试通过 |
| WebSocket 与匹配 | `server/app/main.py` | 有同龄匹配、15 秒后 PvE 路由代码；本次未运行完整浏览器对局 |
| AI 回合 | `server/app/ai/glm_client.py`、`tests/test_ai_turn.py` | GLM 与错误/超时回退的现有 mock 测试通过；未重新调用真实 API |
| 降级策略 | `handle_ai_turn` | 使用中心优先的合法走子；没有调用现存 Minimax 模块 |
| 部署 | `deploy/nginx.conf`、`deploy/connectfour.service` | HTTPS/WSS 和单 worker 模板存在，未证明部署完成 |
| 无障碍 | 当前 client 与 `ca0b19e` 差异 | 完整改进仅存在于已撤销的历史提交 |

复测：macOS，Python 3.12.14；隔离环境安装 `server/requirements.txt` 后从仓库根目录运行 `python -m pytest tests/ -q`。结果：**26 passed, 3 warnings in 1.71s**。三项均为弃用警告，不是测试失败。详见 [原始输出](evidence/2026-10-23-pytest.txt) 和 [依赖版本](evidence/2026-10-23-python-packages.txt)。

这些测试主要覆盖引擎、HTTP 资源、mock GLM 和 AI 回合状态。WebSocket smoke 只是检查路由注册，AI 回合测试将 socket 设为 None；不能把它们当作完整双人浏览器演示的证明。

## 4 最影响 midterm 的问题

| 优先级 | 问题与代码依据 | 建议验收方式 |
|---|---|---|
| 高 | README 建议 `python -m http.server 3000`，但 `socket_client.js` 用当前页面端口连接 `/ws/game`，静态服务器没有该后端 | 统一打开 `http://127.0.0.1:8000/`，另一个成员从干净环境跑通 |
| 高 | `app.js` 在一秒后只发送一次 `queue_join`，未等待连接成功 | 模拟超过一秒的连接建立，确认仍能入队或显示可恢复错误 |
| 高 | `game_board.js` 的 `handleClick` 依赖之前的 hover；没有键盘落子控件 | 实际触屏点按和全键盘完成一局；优先评估已撤销提交中的对应实现 |
| 高 | Nginx 仍用 `connectfour.example.com`；仓库没有经验证的公开服务地址 | 提供真实域名后检查证书、页面、资源、WSS 及完整对局 |
| 中 | `main.py` 的 `current_room_id` 在落子时才设置，断线清理依赖它 | 玩家匹配后不落子就断开，确认房间被清理且对手获通知 |
| 中 | `app.js` 发 `rematch_request`，服务端没有对应分支 | 暂时隐藏未实现按钮，或实现并验证完整流程 |
| 中 | `app.js` 和 `main.py` 仍标 Gemini，运行配置是 GLM | 界面、README、状态表使用一致且真实的模型/本地回退标识 |
| 中 | 服务端出生年份异常输入处理不足，年龄计算固定为 2026；倒计时没有服务端裁定 | 团队补充年龄边界/异常消息测试，明确计时功能的真实范围 |
| 文档 | README/TASKS 多处链接指向个人 Windows 的 `file:///d:/...` | 改为仓库相对链接，由另一个账号打开验证 |
| 文档 | TASKS `DELIV-2` 写 3–5 分钟视频 | 按课程 midterm 专项要求制作不超过 60 秒的 MP4 |

`matchmaking.py` 和 `room_manager.py` 不存在，但部分逻辑已内联在 `main.py` 中；不能仅根据文件缺失判断整个匹配功能未实现。相反，README 树中的 Suite A / Suite B 文件确实不存在，不能声称整套验收完成。

## 5 你负责部分的下一步建议

先确认当时撤销的实际原因，再决定如何重新集成。不要把一次已撤销的大改动直接当成“已完成上线”。建议把后续工作拆成可以单独验收的小块：

1. **10 月 24 日，Scott，复现和部署文档**：统一同源启动步骤、修复文档链接、列出 VPS 目录/权限/证书要求；验收为另一成员按文档打开页面与后端接口。
2. **10 月 25 日，Scott 与前端负责人，最小无障碍集成**：优先触屏落子、键盘列按钮、清楚的焦点和错误提示；验收为实际键盘和触屏操作及对应回归测试。前端负责人姓名仍待团队确认。
3. **10 月 25 日，Scott 与后端负责人，演示环境**：若 VPS/域名已准备好，验证 HTTPS/WSS；否则明确写本地演示并记录公网部署阻碍。验收至少是一条真实输入到结果的完整对局路径。后端负责人待确认。

以上是 midterm 前的建议，并非已完成记录。状态表的“未来两周”另可安排：10 月 30 日稳定性及断线处理、11 月 3 日无障碍人工验证与 HTTPS/WSS 验收、11 月 6 日由另一成员完成干净环境复现。每项需团队确认负责人。

部署过程中，同一实例只开一个 Uvicorn worker。当前匹配池和房间只在进程内存中，开多 worker 或多副本会把用户分到不同的池。systemd 要求的日志目录及权限也需要实际准备；模板文件本身不会创建它们。

## 6 Midterm 当前可以准备到哪里

- 已有真实仓库链接，可以填写 `repository_link.txt`。
- 可以引用此次测试记录，但要写清自动化覆盖范围和局限。
- 你的贡献可以依据实现/撤销两个提交说明，其他成员贡献应由本人确认，不能通过提交数量推定“没有贡献”。
- 尚缺实机录屏、其他成员的已完成工作、最终范围与负责人确认。当前资料不足以生成真实完整的最终提交 ZIP。
- 正式 midterm 要求是一个不超过 100 MB 的 ZIP：不超过 60 秒的 MP4、`repository_link.txt`、一页状态表；10 月 26 日提交，具体截止时刻以 Moodle 为准。仓库内部项目计划不能取代课程专项要求。

课程要求依据工作区中的 `Midterm/AILT9019_Midterm_Check_Requirements.pdf` 与 `Midterm/AILT9019_Midterm_Rubric.pdf`。这两份课程文件不在当前 Git 仓库中；最终以 Moodle 发布版本为准。
