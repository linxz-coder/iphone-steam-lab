# 《名利场 2：冒牌富少》修正记录

最后验证日期：2026-11-11。对应 Steam AppID `4870960`，当时记录的 Steam build 为 `26236662`。补丁最终以文件 SHA-256 为准，不能只看游戏版本号。

## 我留下的组合

| 部分 | 实际文件 / 设置 |
| --- | --- |
| Madeira | 0.2.0 / build 5，VA-floor 修正版 |
| 游戏程序 | x64 FameGame2.exe，窗口清理检查 + 回调 Map 键修正 |
| WebView 浏览器进程 | 109.0.1518.140，x86 |
| 嵌入宿主 | 109.0.1518.140，x64 EmbeddedBrowserWebView.dll |
| 浏览器参数 | 单进程、进程内 GPU、JavaScript jitless，完整内容见 cfg |
| 画面 | 1600×900 / Fit / 60 FPS |
| 输入 | Keyboard and mouse，专用屏幕按键，实际全局 HWINPUT=0 |
| 字体 | 已有合法来源的微软雅黑/宋体，加上 32 位注册 |

目录名不代表实际版本。我的手机仍使用这个原有位置：

```text
Fame Game2/
  FameGame2.exe
  WebView2/
    Microsoft.WebView2.FixedVersionRuntime.149.0.4022.98.x64/
      msedgewebview2.exe                  ← 实际是 109 x86
      ...109 x86 的完整运行库文件...
      EBWebView/
        x86/...
        x64/EmbeddedBrowserWebView.dll    ← 实际是 109 x64
```

11/11 从手机重新读文件验证了两者的 PE 版本，均为 109.0.1518.140。没把“试过 92 版”的过程当作最终配置。

## 先备份

完全退出游戏和 Madeira 后，至少保留：

- 游戏目录里的原始 `FameGame2.exe` 和 `WebView2` 目录。
- `C:/users/mobile/AppData/Local/FameGame2/save/`，这里有实际进度 `save.db`。
- 该游戏的 cfg、触屏布局；如需调整字体，再备份 Wine 的 `system.reg`。
- 当前能用的 Madeira 安装包和配置。

`EBWebView` 是浏览器配置数据，不等于 `save/save.db`。不要把整棵 FameGame2 数据目录当缓存删掉。

## 1. Madeira 的地址分配修正

当时日志显示，原生进程启动后把 `address_space_start` 从 iOS 初始化的 `0x100010000` 又重置到 `0x10000`。后续分配反复扫描低地址，曾出现六万多次失败尝试。实际剧情只有 2–4 FPS，还伴随很长的停顿。

修正仅把那个重置存储指令换成 NOP，保留已经初始化好的起点。WoW32 分支不改。原始排查做过三个初始地址的指令模拟；本次发布又用原版 IPA 重新生成，检查主程序哈希和 ZIP 完整性。

| 校验项 | 值 |
| --- | --- |
| 原始主程序 SHA-256 | `33962cb2919c6ef0cdc6ef036e90eabdd79be3902f3284d1c603c894fa97205f` |
| 修正后主程序 SHA-256 | `4360a867fe5126d9ebfc1917e38ae1d339e1ee484a9fe2460faf897f481fa84e` |
| 文件偏移 | `0xA50E3C` |
| 原指令 / 新指令 | `09fd06f9` / `1f2003d5` |

生成方法见主 README。重新签名后原位安装，检查 Memory+、调试权限和游戏库。不要卸载旧应用来换包。

这次结果：11/9 两轮实际剧情约 59–60 FPS；11/11 再次验证播放和保存后继续。只说明这个设备、这个版本、这个游戏的结果。

## 2. WebView2 109 的准备

从微软更新目录获取 109.0.1518.140 的 x86 和 x64 包，保留微软签名及原始包用于校验。旧版本只用于这个游戏的兼容测试，不用于普通网页浏览。

本次使用过的官方分发地址：

- [109 x86 安装包](https://catalog.s.download.windowsupdate.com/c/msdownload/update/software/updt/2023/09/microsoftedgestandaloneinstallerx86_179f59bc54d73843d9288a9fd5609de0e507b911.exe)
- [109 x64 安装包](https://catalog.s.download.windowsupdate.com/c/msdownload/update/software/updt/2023/09/microsoftedgestandaloneinstallerx64_1c890b4b8dd6b7c93da98ebdc08ecdc5e30e50cb.exe)

用 7-Zip 展开外层安装包，继续展开里面的安装程序和 `MSEDGE.7z`，找到 `Chrome-bin/109.0.1518.140/`。实际操作只解包，不需要在 Mac 上执行 EXE。

游戏自己的 x64 宿主仍需要 x64 的 EmbeddedBrowserWebView.dll，而浏览器进程使用 x86。准备完整 x86 目录后，把对应 x64 DLL 放到 `EBWebView/x64/EmbeddedBrowserWebView.dll`。不能只复制一个 msedgewebview2.exe，遗漏旁边的 DLL、资源和 locales。

备份原目录后，把准备好的运行库放到游戏原先寻址的位置。我的旧目录名没有改变，所以启动日志里看见 149 并不代表还在跑 149。

11/11 手机文件校验值：

| 文件 | SHA-256 |
| --- | --- |
| msedgewebview2.exe，109 x86 | `d8a2f04cb823332de7efbad84cf2f3788fe0000b29d613f18b366526314dec69` |
| EBWebView/x64/EmbeddedBrowserWebView.dll，109 x64 | `80c310f2972471b8f8a73b9369a78a47fd8dec6ad7d35c0920fd975ef5af73e8` |

仓库不打包这些微软文件。下载地址失效或文件不匹配时，先核对来源和版本，不用其他 DLL 猜着替换。

## 3. 游戏宿主兼容补丁

这个补丁只针对记录中的原始文件，包含两部分：

1. 在三个 `RevokeDragDrop` 调用点前检查窗口是否存在、是否属于当前进程。有效窗口仍走原调用；无效或其他进程窗口返回对应错误值。补丁增加一个很小的 `.fgfix` 节，并同步异常展开表。
2. Tauri 的回调 Map 在 set/get/delete 时统一使用字符串键，避免旧 WebView 下键类型不一致。

不修改 Steam 登录、授权、游戏购买检查或存档逻辑。输入必须是自己安装的正版游戏文件，依旧从 Steam 游戏库正常启动。

```bash
# 把原始 FameGame2.exe 复制到 private/，不要直接以游戏安装目录作为输出。
mkdir -p private artifacts
python3 scripts/apply_game_patch.py private/FameGame2.exe --check
python3 scripts/apply_game_patch.py private/FameGame2.exe \
  --output artifacts/FameGame2.exe
```

| 文件 | SHA-256 |
| --- | --- |
| 原始输入，137933072 字节 | `359b81928f1cfa2cacc2a2d4f544f6691d286137ddbb030156dbb5c5c7ce7559` |
| 生成输出，137933824 字节 | `2d9eea559e0d6d8d836c50ad6eedd48b15eef8971151d1480e8f46e6db96880c` |

生成结果与 11/11 手机上实际运行的文件哈希一致。备份原件后再把输出复制回游戏目录。Steam 更新或校验游戏文件可能会恢复原始程序，届时先核对新版本，不能绕过脚本的哈希检查。

补丁配方只保存变更范围，不包含游戏本体。它保存了当时能运行的组合；没有做逐项移除的对照测试来证明两部分缺一不可。

## 4. 配置、分辨率和字体

把 [fame-game2.cfg](../configs/fame-game2.cfg) 中的设置合并到该游戏的配置，显示改为 1600×900、Fit、60 FPS。

单进程降低了 WebView 的进程隔离，一个组件崩溃可能带走整个游戏。我只把它留给这款游戏，不作为全局浏览器参数。`--jitless` 是 JavaScript 引擎的设置，不能代替 iOS 侧 Madeira 所需的 JIT。

中文菜单正常、字幕却是方块时，检查 `C:/windows/Fonts/` 中是否有自己有权使用的字体，以及以下两个注册位置：

```text
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Fonts
HKLM\Software\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Fonts
```

当时已有 `msyh.ttc`、`simsun.ttc`，补齐 32 位位置的 8 个对应条目后，剧情中文字幕才显示正确。只拷字体文件不一定够。用 [scripts/register_fonts32.py](../scripts/register_fonts32.py) 可以对导出的 Wine `system.reg` 生成新文件；它只复制已有的这两类字体注册，不下载字体，不修改手机。

触屏坐标修正后，菜单点击、Space 暂停/继续、Esc 返回都通过了验证。`MADEIRA_HWINPUT=0` 是这台手机经 Mac 镜像操作时保留的全局设置，硬件键鼠用户需要另测。

## 5. 保存、退出、再继续

11/11 做了三次独立启动：第一次进入第四章回顾，再到第五章厨房剧情并产生测试检查点；第二次冷启动能继续到该检查点；之后恢复原进度并开启云同步，第三次正确回到原来的第四章回顾。

临时测试第五章时隔离了云上传，测试结束恢复原存档。最终对比确认，剧情节点、分支变量值和激活节点没有变化，只有变量修改时间刷新。这里不公开私人存档。

我重复遇到游戏内部退出后 Madeira 留着旧画面。处理方式已经改为：

> 等游戏保存完成 → 保持 UU 联网 → Madeira 三横线菜单 → 向下滚到底 → Upload saves and close Madeira → 等自动退出。

安全退出上传 1 个更新文件，随后检查为 5 个一致。重新打开 Madeira 后仍是 5 个一致。下一轮运行仍要重新获得 JIT。

## 回退

完全关闭 Madeira，恢复备份的游戏程序、WebView2 目录和游戏 cfg；如改过字体，再恢复对应的注册表备份。存档只在核对实际进度后恢复，别把旧备份直接当成“修复包”覆盖新进度。

如果只是想撤销 Madeira 的 VA-floor 修正，用原版 IPA 重新签名后原位安装。先备份容器数据、保持同一签名身份和应用标识，再检查游戏库及存档。

不要把已经撤回的 `patch_va.py` / `patch_va4.py` 地址猜测方案和现在的 VA-floor 修改混用。仓库只保留这次实际部署并验证过的补丁配方。
