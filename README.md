# iPhone Steam Lab

我想把 iPhone 当成一台随身的 Steam 掌机：登录自己的账号，把游戏下载到手机里，直接在手机上运行。

最开始想玩《港诡实录》和 Hades，后来又装了《睡狗》《名利场 2：冒牌富少》《武士零》和《行尸走肉》。这一路遇到的问题比预想多：Steam 异常登录、JIT 开不起来、VPN 互相顶掉、进了菜单点不动、剧情只有两三帧，还有保存退出后停在旧画面。

这里把用过的配置、修正脚本和测试结果留下来。以后换手机、续签、游戏更新出问题，也有东西可以查。

**目前《冒牌富少》和《武士零》已经有实际游玩及重启测试。《睡狗》《港诡实录》做过旧存档和基础操作测试。《行尸走肉》还有交互和冷启动问题。** 下面会写清楚每款测到了哪里。

这套方案基于 [Madeira](https://github.com/willfaust/Madeira)。实际运行用到 FEX-Emu、Wine、DXMT 等项目。我整理的是本机适配和使用记录，模拟器本体来自上游。游戏在 iPhone 本地运行；Mac 用来安装、续签、备份和看日志，Steam Link 串流不在这套流程里。

## 先看测试条件

| 项目 | 这次使用的环境 |
| --- | --- |
| 手机 | iPhone 17 Pro |
| 系统 | iOS 26.5.1 |
| Madeira | 0.2.0 / build 5；后续使用本仓库脚本生成的 `0.2.0-local-va-floor-test1` |
| 签名工具 | iloader 2.4.1；保留 Memory+ 和调试权限，原位安装 |
| JIT | StikDebug 3.2.2 + Madeira 配套的 `madeira-jit.js`；也试过内置 StikJIT |
| Steam 联网 | UU 加速器，中国香港线路 |
| 操作 | Madeira 屏幕虚拟按键；多数验证通过 Mac 的 iPhone 镜像点击 |
| 实体手柄 | GameSir X5s 没有参加这轮测试 |
| 记录时间 | 2026-11-05 至 2026-11-11 |

帧率来自屏幕叠层的短时观察，睡狗另跑了内置 Benchmark。没有测完整流程，也没有连续玩几个小时来测发热。通过 Mac 镜像点虚拟按键，不能代替手机直接多指操作和实体手柄的测试。

上游 0.2.0 要求 iOS 26 或以上；上游说明里的应用内配对、Madeira JIT 快捷指令还涉及 iOS 27。我的 iOS 26.5.1 是已有配对文件配合 StikDebug 的路线。不要把系统要求和本机实测环境混在一起。见 [0.2.0 发布说明](https://github.com/willfaust/Madeira/releases/tag/v0.2.0)。

## 仓库里有什么

```text
configs/       按游戏整理的配置、触屏按键布局
scripts/       本地补丁生成、布局合并、日志摘要工具
patches/       限定版本的补丁配方，包含输入和输出校验值
docs/          冒牌富少修正细节、USB 操作、存档和回退说明
evidence/      脱敏测试记录和关键校验结果
tests/         补丁拒绝错误输入、布局合并和日志输出测试
```

不提供游戏本体、Steam 登录数据、个人存档、配对文件、微软字体和运行库。Madeira IPA 从上游下载，游戏从自己的 Steam 库安装。这个仓库也没有一个装上就能玩所有 Steam 游戏的 IPA。

## 从安装到第一次运行

### 1. 安装 Madeira，检查权限

从 [Madeira Releases](https://github.com/willfaust/Madeira/releases) 下载安装包，使用 [iloader](https://github.com/nab138/iloader) 等侧载工具签名。我的 0.2.0 修正版可以按后面的命令在本机生成。

- 保留应用扩展。Madeira 的部分 JIT 功能用得到。
- 在 Madeira 的设置里确认 Memory+ 和调试权限正常。装得进去，不代表这些权限一定带上了。
- 按手机提示开启开发者模式、信任签名。账号密码和验证码直接填在 Apple 的验证窗口。
- 已经装过游戏时，先备份，再原位更新。别先卸载 Madeira，应用容器里的游戏和存档也会一起受到影响。
- 续签时继续使用已经验证过的修正版。换回原版 IPA，会丢掉这次的地址分配修正。

我最初用 Sideloadly 签过一次，Memory+ 没有达到需要的状态，后来改用 iloader。这个记录只说明当时那次签名的结果，不能推成所有 Sideloadly 安装都不行。

### 2. 登录 Steam

先用平时能登录 Steam 的网络。我的手机需要 UU 的 Steam 加速，因此登录和下载阶段一直保留 UU。

Madeira 里可以尝试账号登录或二维码登录。二维码要用官方 Steam App 确认。如果正在用 iPhone 镜像，拿起手机后镜像会中断，可以先把二维码留在 Mac 屏幕上，再用手机扫码；二维码过期就重新生成。

我遇到过 Steam 的“异常登录尝试，需要额外安全保障”。那次是自己刚发起的 Madeira 登录，在官方 Steam App 里按实际用途回答：Steam 客户端、其他用途，然后完成确认。这里没有要关闭 Steam Guard 的步骤。不认识的登录请求当然不要批准。

**Steam App 显示“已批准”，还要回 Madeira 看它有没有收到结果。** 我曾在这一步看到 `No internet connection`，原因排查涉及 UU 和 LocalDevVPN 的切换。先恢复能连接 Steam 的网络，再检查登录页；别连续换 VPN、换二维码、反复提交密码。

### 3. 下载游戏

登录后从游戏库下载。先等下载完成，再启用 JIT 测游戏。

UU 和 LocalDevVPN 在我这台手机上会替换对方。下载到一半为了 JIT 切到 LocalDevVPN，容易把下载线路切掉。下载失败先恢复原线路续传，没必要取消任务、删掉已经下好的内容。

断开 USB 不等于删除下载任务，但后台能否继续还受 Madeira、iOS 调度和网络影响。我会看应用里的下载状态，不会只凭“已经拔线”判断任务还在跑。

### 4. 启用 JIT，再恢复 Steam 联网

我实际采用的顺序是：

1. UU 联网，打开 Madeira，先完成该游戏的云存档检查。
2. 连接 LocalDevVPN。
3. 用 StikDebug 和 Madeira 配套的 `madeira-jit.js` 启用 JIT，回到 Madeira 点 Play。
4. 等运行时真正建立 JIT 池。日志中的 `JIT pool ready` 和 `Debugger detached` 是这次使用的判断依据。
5. 再切回 UU，让游戏完成 Steam 联机认证。

**只点过 Enable JIT，或者看到了蓝色闪电，不等于第 4 步完成。** 我试过太早切回 UU，结果 Play 阶段仍然开不起 JIT。

另一处容易误判：UU 页面还留着旧的“加速中”计时，系统 VPN 实际选中的却是 LocalDevVPN。遇到这种情况，到 iOS 设置的 VPN 页面核对，选回 UU，再到 UU 重新开始 Steam 加速。

11 月 11 日内置 JIT 有过端口连接超时，Madeira 跳转 StikDebug 也曾误报“未安装”。最终用 StikDebug 给**已经运行的 Madeira 进程**附加成功，保留了之前完成的云检查。具体 USB 命令在 [进阶操作](docs/usb-and-backups.md)。这个入口问题还没有从应用代码上彻底修好，无电脑启动也没有覆盖所有情况。

### 5. 虚拟按键怎么用

游戏详情里开启 **Touch controls**，再选布局。修改后保存到这款游戏，退出重开检查一次，别只停在编辑预览。

| 游戏 | 本次使用的输入方式 | 确认过的操作 |
| --- | --- | --- |
| 睡狗 | 内置 Xbox controller | 基础移动、转向、菜单、暂停 |
| 港诡实录 | `港诡实录：手柄＋菜单键` | 方向键选菜单、Enter 确认、X 蹲下/站起、Start/Esc 暂停 |
| 武士零 | Xbox 布局，60 FPS | 移动、A 跳跃、X 挥刀击杀、Start 暂停 |
| 行尸走肉合集 | Xbox 布局，30 FPS | 菜单确认、右摇杆视角；剧情交互没有可靠通过 |
| 冒牌富少 | `名利场2：触屏与剧情键`，Keyboard and mouse 模式 | 菜单点击、Space 暂停/继续、Esc 菜单、返回主菜单 |

《冒牌富少》布局里的键：

| 屏幕显示 | 实际按键 | 用途 / 验证范围 |
| --- | --- | --- |
| L | 鼠标左键 | 点击；已测试 |
| Esc | Esc | 暂停菜单、返回；已测试 |
| 空格形状的符号 | Space | 剧情暂停/继续；已测试 |
| Q | Q | 布局中作为跳过键保留；这轮没用它推进剧情 |
| ← / → | 左 / 右方向键 | 布局中保留快退/快进用途；这轮未验证 |
| 7B | F12，虚拟键码 0x7B | 截图键映射；这轮未验证 |

自定义布局在 [configs/touch-presets.json](configs/touch-presets.json)。这是 Madeira 的持久化布局文件格式，不是 Share Setup 格式。合并方法见 [进阶操作](docs/usb-and-backups.md)，不要直接覆盖自己已有的布局。

## 哪些游戏测过，结果怎么样

这些结论对应上面的设备和日期。游戏或 Madeira 更新后，需要重新验证。

| 游戏 / Steam AppID | 测到了哪里 | 帧率记录 | 目前的判断 |
| --- | --- | --- | --- |
| Hades / `1145360` | 已安装，我自己完成过一轮测试；后续排查没有重复测它 | 没有可比较的帧率记录 | 不在这里补写未记录的性能结论 |
| 港诡实录 / `1178490` | 载入旧存档，菜单、确认、蹲起、暂停有响应 | 初次短样本约 40–49 FPS，转向有帧时尖峰 | 基础可操作；复杂场景、连续多指操作未测全 |
| Sleeping Dogs: Definitive Edition / `307690` | 旧云存档可载入，基础移动/转向/暂停；中文菜单、自动保存提示已确认 | 当次中档 Benchmark 平均约 33，最低 21，最高 51 FPS | 能进入游玩；战斗、驾驶、长时间稳定性没测完 |
| 名利场2：冒牌富少 / `4870960` | 中文菜单、旧档继续、剧情视频、字幕、暂停/返回；保存后冷启动再继续 | 修正前剧情 2–4 FPS；修正后短时约 59–60 FPS，部分转场会下降 | 本次短测可玩；不是全章节通关保证 |
| Katana ZERO / `460950` | 中文开场、屋顶教程，移动/跳跃/挥刀击杀/暂停；第二次冷启动成功 | 1408×648，60 FPS 上限，教程约 60 FPS | 本次短测可玩；旧云进度还没有完整恢复证明 |
| The Walking Dead: The Telltale Definitive Series / `1449690` | 中文合集菜单、第一季第一章警车场景、右摇杆视角 | 1408×648，60 上限时约 44–55 FPS；锁 30 后当前场景更稳 | **还不能当作正常可玩**：场景交互不可靠，重复冷启动也卡过 |

睡狗的中文补丁沿用了本机 CrossOver 里已经使用的补丁，先备份再覆盖，随后看了手机里的中文菜单和自动保存提示。补丁本体没有放进仓库；只有安装成功的提示，不能代替游戏里实际显示中文。

Hades 我先测完了，后面主要在折腾其他几款。这一行只保留当时的自测结果，没有记录下来的帧率就不补写了。

实际画面和按日期整理的结果放在 [测试记录](evidence/README.md)。

## 存档会不会同步

先看游戏有没有云文件，再看 Madeira 能否把路径映射到手机。

| 游戏 | 这次存档检查结果 |
| --- | --- |
| 冒牌富少 | 11/11 原进度恢复后，5 个文件全部一致；实际完成上传、关闭、重开检查，也做了保存后继续测试 |
| 睡狗 | 11/9 选用当天上午的最新进度，对照 Mac/手机备份后解决冲突；11/11 只读检查显示 9 个文件一致 |
| 港诡实录 | 旧存档能读取；Steam Cloud 检查没有远端文件，不能据此承诺跨端自动同步 |
| 武士零 | 11/9 有 9 个云文件未映射；11/11 读数是 9 个一致、9 个未映射，仍不能当作原来所有进度已经恢复 |
| 行尸走肉合集 | 11/9 测试前没有云文件；11/11 检查有 15 个文件一致，但没有完成跨设备同一剧情位置的读档验证 |
| Hades | 最初检查没有云端或本机存档；这里没有已验证的旧进度同步结果 |

《武士零》的 `unmapped` 尤其要留意：Mac 版和 Windows 版的路径可能不同。不要看到 Steam Cloud 开关开着，就直接开新游戏再把新档传上去。

我现在的习惯：

1. 开始前看 **游戏详情 → Steam Cloud → In sync**，必要时点 Sync now。
2. 有冲突先备份两边，对照时间和实际进度。成就数量不能用来判断哪份存档更新。
3. 游戏里等自动保存完成。
4. 保持 Steam 联网，点 Madeira 右上角三横线，向下滚到底部，选 **Upload saves and close Madeira**。
5. 等上传完成、应用自己关闭，再去另一台设备继续。

11/11 的日志记录了 `quit-upload done files=1: closing Madeira`，随后重新打开，仍是 5 个文件一致。这个流程已经实际走通。

**只点《冒牌富少》游戏内部的“退出”，Madeira 可能留在最后一帧。** 我连续复现了两次，游戏进程已经正常结束，但画面看着像卡死。用上面的上传并关闭入口，才把整个 Madeira 会话结束掉。下次重开要重新启用 JIT。

云同步的上游说明：[STEAM_CLOUD.md](https://github.com/willfaust/Madeira/blob/main/docs/STEAM_CLOUD.md)。存档路径和备份命令见 [USB、存档与回退](docs/usb-and-backups.md)。

## 《冒牌富少》用了哪些修正

这款花的时间最多。Mac 上 CrossOver 能用的方案给了方向，但照搬到 iPhone 还不够。

- WebView2 换成实际验证过的 **109.0.1518.140 x86**，同时保留对应的 x64 嵌入宿主 DLL。手机里原有的目录名仍带 `149.0.4022.98.x64`，实际文件版本已经不同。
- 游戏宿主有两处兼容处理：给无效/其他进程的窗口做 `RevokeDragDrop` 检查；Tauri 回调 Map 的键统一为字符串。
- WebView2 使用单进程和 `--jitless` 组合，减少当时的进程及地址空间问题。这里降低了 WebView 内部的进程隔离，只作为这款本地游戏的兼容方案保留。
- Madeira 的原生地址分配起点被重置到 64 KiB，日志里有大量失败扫描。修正版保留 iOS 初始化的 `0x100010000` 起点，修改后实测剧情从 2–4 FPS 恢复到约 60 FPS。
- 显示统一为 **1600×900 / Fit / 60 FPS**。之前游戏是 1600×900、输入映射按 1408×648 算，出现了点 A 到 B、按钮没反应的情况。
- 使用这次验证过的触屏输入配置；中文字幕缺字时，补了已有合法字体的 32 位注册项。

完整顺序、校验值和回退方式在 [冒牌富少修正记录](docs/fame-game2.md)。**单独复制一个 cfg，不能保证得到相同结果。**

### 生成 Madeira 修正版

Python 3.10 或以上即可，脚本只用标准库。在仓库根目录运行：

```bash
mkdir -p downloads artifacts
curl -fL --retry 2 \
  'https://github.com/willfaust/Madeira/releases/download/v0.2.0/Madeira-0.2.0.ipa' \
  -o downloads/Madeira-0.2.0.ipa

python3 scripts/patch_madeira.py downloads/Madeira-0.2.0.ipa --check
python3 scripts/patch_madeira.py downloads/Madeira-0.2.0.ipa \
  --output artifacts/Madeira-0.2.0-va-floor-test1.ipa
```

脚本先校验主程序的完整 SHA-256、版本和目标指令，再改一个 4 字节指令；输入不匹配就停止。输出已经存在也会停止，不覆盖旧包。生成的 IPA 还需要侧载工具重新签名，不能直接拿去安装。

这里没有“支持所有 0.2.x”的意思。就算文件名一样，校验不对也不要改脚本里的哈希硬套。新版本有可能已经修好，先看上游变化。

### 按游戏应用配置

- 《冒牌富少》：[fame-game2.cfg](configs/fame-game2.cfg)，只用于上述运行库组合。
- 《武士零》：[katana-zero.cfg](configs/katana-zero.cfg)，保留通过短测和第二次启动的配置。
- 全局输入设置：[global-reference.cfg](configs/global-reference.cfg)，仅作参考。`MADEIRA_HWINPUT=0` 会关闭 Madeira 的硬件键鼠桥接，可能影响蓝牙/USB 键鼠，别给所有设备默认套上。

先备份目标游戏配置，在游戏详情的 Advanced 中按键名设置；如果当前界面不方便编辑，再用 USB 导出对应 cfg，合并后写回。游戏配置文件名是本地生成的，不要照抄我手机里的散列文件名。导入后完整关闭 Madeira，再重新启动验证。

## 遇到问题先查哪里

| 现象 | 这次见过的原因或线索 | 我会先怎么处理 |
| --- | --- | --- |
| Steam 提示异常登录 | 新设备/第三方客户端触发额外验证；不是密码一定错了 | 在官方 Steam App 核实这次请求，完成 Steam Guard，回 Madeira 等结果 |
| 已批准，Madeira 却说没网络 | VPN 被 LocalDevVPN 替换，或登录结果没及时接收 | 恢复原来能登录的 UU 线路，再确认 Madeira 状态 |
| VPN 开着，JIT 仍失败 | 配对、调试服务、JIT 脚本、端口或进程不匹配；连接 VPN 本身不等于 JIT 成功 | 查 Memory+ / 调试权限，使用匹配的 Madeira 脚本，确认实际进程和日志；不要复制别人的固定端口 |
| StikDebug 明明装了却提示未安装 | 本机发生过跳转入口误报，根因尚未确认 | 从 StikDebug 处理；需要保留当前 Madeira 状态时，使用现有 PID 入口。这个问题还没有永久代码修复 |
| 停在 Signing in to Steam | 网络切换后认证等待；也遇到过客户端初始化真正停住 | 先确认 JIT 池和 UU 实际连接。本次成功启动有的用了 1–2 分钟；日志不推进再排查，不无限等 |
| 提示账号还在另一处游戏 | 其他设备或上次未退出的残留会话 | 结束实际游戏会话，等 Steam 释放；不要修改 Steam Guard 或替换认证组件 |
| 日志写 SDL3.dll 加载失败 | 成功启动的日志里也能出现同一报错 | 看后续是否认证、是否出现窗口。两次换成 x64 DLL 没解决问题，最后恢复原文件 |
| 冒牌富少只有 2–4 FPS | 本机遇到地址空间从 64 KiB 开始反复扫描 | 对照版本与日志，使用已验证的 VA-floor 修正，再测真实剧情；不是只降分辨率 |
| 看到菜单但点不动 | 输入坐标和显示分辨率不一致、硬件指针桥接问题，也可能游戏本身卡住 | 对齐到 1600×900，检查输入模式，分别测手机触摸和镜像；不能只测一次菜单 |
| 中文字幕是方块 | 64 位字体注册存在，32 位 WebView 缺少对应注册 | 使用自己有权使用的字体，补 32 位注册，再看实际剧情字幕 |
| 保存退出后像卡死 | 游戏已结束，Madeira 留着旧画面 | 用 Upload saves and close Madeira；重新开应用后重新启用 JIT |
| 云存档开着但进度不对 | 文件未映射、版本不同、冲突未处理 | 备份后看 same / differ / unmapped，核对实际进度，别用新游戏覆盖旧档 |
| 武士零能进，行尸走肉还是不行 | 两款游戏的运行时和输入问题不同 | 配置分别保留。行尸走肉目前仍未确认正常可玩，不继续叠加未经验证的参数 |
| 用了一阵才卡 | 发热、内存、场景变化都可能影响 | 记录相同场景、帧率和温度状态，再比较；没有证据就不把所有卡顿归给发热 |

### 试过但没有留下的方案

- 直接替换 Steam 目录的 SDL3.dll：没有解决启动，已恢复。
- 给《冒牌富少》套《武士零》的 `inproc-sync=0` / `MADEIRA_FASTSYNC=0`：这轮启动更慢，撤回。
- 只关闭 GPU、改软件渲染：有时能看到页面，但不等于视频、输入和性能一起可用。
- WebView2 92、109 x64、多组地址分配重试：都是排查中的实验，不能当作最终方案。
- 提前把 LocalDevVPN 换成 UU：会破坏还没完成的 JIT 初始化。

## 查看日志、备份和验证脚本

原始日志只留在本机。需要分享结果时，先生成有限字段的摘要：

```bash
python3 scripts/log_summary.py private/madeira-log.txt
python3 -m unittest discover -s tests -v
```

摘要只输出 JIT、认证、游戏窗口和云同步计数，不回显原始日志行。它只负责提取证据，不会根据“窗口出现”自动给游戏贴上可玩标签。日志如果混了几轮启动，要先分清是哪一轮。

使用 USB 的备份、布局合并、日志获取和现有 PID JIT 示例在 [docs/usb-and-backups.md](docs/usb-and-backups.md)。脚本默认不操作手机，也不自动覆盖安装目录。

## 接下来还想测的

- GameSir X5s 的连接、按键映射、长按和手感。
- 港诡实录的连续移动和视角；睡狗的战斗、驾驶及较长时间游玩。
- 行尸走肉的场景互动、QTE 和再次冷启动。
- 武士零原有云进度的完整映射。
- 不依赖 Mac 的稳定 JIT 启动流程。

这份记录会按实际测试补。进了菜单就写进了菜单，能继续旧档才写旧档可用；遇到没解决的地方，也留在这里。

## 来源与许可

- [Madeira](https://github.com/willfaust/Madeira) / [0.2.0](https://github.com/willfaust/Madeira/releases/tag/v0.2.0) / [JIT 文档](https://github.com/willfaust/Madeira/blob/main/docs/JIT.md)
- [StikDebug](https://github.com/StikDebug/StikDebug) / [StikJIT 集成说明](https://github.com/StikDebug/StikJIT/blob/main/INTEGRATION.md)
- [iloader](https://github.com/nab138/iloader)
- [Microsoft WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2) / [微软更新目录](https://www.catalog.update.microsoft.com/)

本仓库新增的脚本和文档使用 [MIT License](LICENSE)。Madeira 及其依赖、游戏、字体、运行库各自的许可不因此改变。具体见 [THIRD_PARTY.md](THIRD_PARTY.md)。
