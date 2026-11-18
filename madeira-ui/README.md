# Madeira 的 Steam Deck 风格首页

这份补丁基于 Madeira 0.2.0，把首页改为横向圆角封面、选中游戏展开、深灰蓝背景。点击后仍进入原游戏详情，Steam 下载、云存档和启动流程继续使用 Madeira 原来的实现。

同时保留之前实机使用的 VA-floor 修正：iOS 原生进程初始化时不再把已设置的地址下界重置到 64 KB。WoW 分支和其他平台的行为保持不变。这个修正已用实际初始化函数编译测试 48 种组合。

`source.json` 固定上游提交和构建标记。`patches/deck-home.patch` 包含界面、工程成员、版本标记和兼容修正，不包含游戏、个人存档、账号、配对信息和签名材料。

GitHub Actions 在 `codex/deck-ui-build` 分支构建，使用上游同款 `xcode-27` 标准环境，生成未用个人账号签名的完整 IPA。构建产物保留三天。产物生成后仍需检查资源和权限，再用原账号、原应用标识进行保留数据的原位安装。

预览通过不代表完整 app 已构建或已安装；以 Actions 结果和手机回读为准。首次构建需要编译 LLVM、FEX、Wine、DXMT 等依赖，可能需要数小时。

补丁修改的 Madeira 源码沿用 GPL-3.0-or-later 和 Madeira Converter Exception，详见本目录许可证。仓库其他独立脚本的许可不变。

## 2026-11-18 的 Hades 启动修正

build 7 在 iOS 26.5.1 上启动 Wine 时会调用系统缺少的 `pipe2`。build 8 改用兼容的管道接口后，Steam 已能启动 Hades.exe，但 32 位和 64 位 DirectX 版都会在创建窗口前退出。对照之前能玩的版本，构建脚本漏了上游的 `patches/wine-opengl-winios.patch`。

build 9 在编译 Wine 前应用这份补丁，同时重建手机端和 Windows 端组件。安装包检查覆盖了 `pipe2`、32 位和 ARM64EC OpenGL 的加载地址、运行库清单。完整包 SHA-256 为 `2216358baed5b1ab5721cf1026874566329e2be4a1d45b5eac9cd00a3e292966`。[build 9 构建记录](https://github.com/linxz-coder/iphone-steam-lab/actions/runs/44217309763)

截至这次构建，build 9 已通过安装包检查，实机游玩结果待验证。下方是 build 7 的历史记录。

## 2026-11-17 的 build 7 实机记录

2026-11-17，0.2.0 / build 7 已用原应用身份安装到 iPhone 17 Pro / iOS 26.5.1。[完整构建记录](https://github.com/linxz-coder/iphone-steam-lab/actions/runs/44019905283)。

横向封面切换和原游戏详情入口能用。实机还发现旧 Desktop 自动焦点会把新首页滚走，现已修正，连续两次重新打开均停在顶部。安装前后核对了六款游戏目录、107 个存档及配置文件和 7 个启动文件摘要，数据均保留。JIT 通过原 StikDebug 脚本启用，Memory+ 正常。

这轮没有重新跑游戏、测帧率或测温度。Madeira 内的 Enable JIT 仍可能误报 StikDebug 未安装，继续使用已配置的 StikDebug 流程；首页补丁没有修改认证和 JIT 实现。睡狗在启动后的自动云同步中下载了两个更新文件，旧文件已备份，九个文件与云端一致，没有上传存档。

定制 IPA 的 SHA-256：`0c7b160577cf78dd73cadcdb9bffc877eed144cc5f672f8c25dc9ab79d5e0d09`。后续续签保持原账号和应用标识，使用这份定制包或更高版本的同源构建，避免官方旧包覆盖定制首页。
