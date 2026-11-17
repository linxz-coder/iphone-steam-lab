# Madeira 的 Steam Deck 风格首页

这份补丁基于 Madeira 0.2.0，把首页改为横向圆角封面、选中游戏展开、深灰蓝背景。点击后仍进入原游戏详情，Steam 下载、云存档和启动流程继续使用 Madeira 原来的实现。

同时保留之前实机使用的 VA-floor 修正：iOS 原生进程初始化时不再把已设置的地址下界重置到 64 KB。WoW 分支和其他平台的行为保持不变。这个修正已用实际初始化函数编译测试 48 种组合。

`source.json` 固定上游提交和构建标记。`patches/deck-home.patch` 包含界面、工程成员、版本标记和兼容修正，不包含游戏、个人存档、账号、配对信息和签名材料。

GitHub Actions 在 `codex/deck-ui-build` 分支构建，使用上游同款 `xcode-27` 标准环境，生成未用个人账号签名的完整 IPA。构建产物保留三天。产物生成后仍需检查资源和权限，再用原账号、原应用标识进行保留数据的原位安装。

预览通过不代表完整 app 已构建或已安装；以 Actions 结果和手机回读为准。首次构建需要编译 LLVM、FEX、Wine、DXMT 等依赖，可能需要数小时。

补丁修改的 Madeira 源码沿用 GPL-3.0-or-later 和 Madeira Converter Exception，详见本目录许可证。仓库其他独立脚本的许可不变。
