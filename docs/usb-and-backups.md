# USB、存档与回退

下面是 Mac 端操作。需要 Xcode 提供的 `xcrun devicectl`、手机信任这台 Mac，以及已签名安装的 Madeira。先用 `xcrun devicectl help` 确认工具可用。

这些命令里的设备和应用标识要换成自己的，不要从别人的日志里照抄。连接信息、完整进程列表和原始日志只留在本机。

## 找到设备和 Madeira

```bash
xcrun devicectl list devices
```

选择自己的设备，把值填在变量里：

```bash
PHONE_ID='填写自己的设备标识'
xcrun devicectl device info apps --device "$PHONE_ID"

# 从上面的输出确认；签名后的标识可能带团队后缀。
MADEIRA_BUNDLE='填写实际的Madeira包标识'
mkdir -p private backups
```

## 先导出，再改

以冒牌富少存档为例，先完全关闭 Madeira，再导出：

```bash
xcrun devicectl device copy from \
  --device "$PHONE_ID" \
  --domain-type appDataContainer --domain-identifier "$MADEIRA_BUNDLE" \
  --source 'Documents/wine/drive_c/users/mobile/AppData/Local/FameGame2/save/save.db' \
  --destination backups/fame-save-before.db

xcrun devicectl device copy from \
  --device "$PHONE_ID" \
  --domain-type appDataContainer --domain-identifier "$MADEIRA_BUNDLE" \
  --source 'Documents/madeira.cfg' --destination backups/madeira-before.cfg
```

每轮使用新的备份文件名。换配置前备份，换签名包前还要备份全部存档、游戏列表和自定义按键；不需要为了备份把几十 GB 游戏都重复复制一次。

本机见过的存档位置：

| 游戏 | 相对 `Documents/wine/drive_c/` 的位置 |
| --- | --- |
| 冒牌富少 | `users/mobile/AppData/Local/FameGame2/save/` |
| 港诡实录 | `users/mobile/AppData/Local/PuzzleGame/Saved/` |
| 武士零 | `users/mobile/AppData/Local/Katana_ZERO/` |
| Hades | `users/mobile/Documents/Saved Games/` 下对应游戏目录 |
| 睡狗 Definitive Edition | Steam 游戏安装目录的 `data/`，文件名如 `HK GameSlot 1`、`HK Autosave Slot`、`HK Options` |

先列自己的目录确认存在，再导出；不同平台或版本可能有差异。《行尸走肉》不同版本、季度目录不同，这里不填一个未经核对的通用路径。

## 自定义触屏布局

导出 `Documents/madeira-control-presets.json` 到 `private/current-presets.json`。运行：

```bash
python3 scripts/merge_touch_presets.py private/current-presets.json \
  --output private/merged-presets.json
```

工具保留已有布局，添加仓库里的港诡和冒牌富少布局。名称或 ID 相同但内容不同会停止，让你自己决定保留哪份。不要为了通过检查直接删掉旧布局。

如果是第一次创建自定义布局，先在 Madeira 内保存一份布局，让应用生成文件，再导出合并。

确认新文件后，在 Madeira 完全关闭时写回：

```bash
xcrun devicectl device copy to \
  --device "$PHONE_ID" \
  --domain-type appDataContainer --domain-identifier "$MADEIRA_BUNDLE" \
  --source private/merged-presets.json \
  --destination 'Documents/madeira-control-presets.json'
```

重新打开，在每款游戏的 Controller layout 中选对应布局，开启 Touch controls 并保存。导入文件只表示布局存在，还需要实际点按验证。

## 32 位字体注册

先导出 `Documents/wine/system.reg` 到 `private/system-before.reg`。已有合法来源的字体及 64 位注册后：

```bash
python3 scripts/register_fonts32.py private/system-before.reg \
  --output private/system-fonts32.reg
```

它只补齐已存在的 `msyh.ttc` 和 `simsun.ttc` 条目，遇到同名冲突停止。先查看差异，再在应用关闭时写回。其他全局设置不会由这个脚本改动。

## 获取诊断摘要

```bash
xcrun devicectl device copy from \
  --device "$PHONE_ID" \
  --domain-type appDataContainer --domain-identifier "$MADEIRA_BUNDLE" \
  --source 'Documents/madeira-log.txt' --destination private/madeira-log.txt

python3 scripts/log_summary.py private/madeira-log.txt
```

原始日志可能含会话信息。分享摘要前也应看一遍，只保留与问题有关的字段。

日志复制如果失败，先确认 USB 连接及读取权限。游戏运行时还遇到过日志硬链接导致导出失败；这时优先用 Madeira 的日志导出入口，或等应用正常退出再读取。不要递归删除整个日志目录来碰运气。

## 给现有 Madeira 进程启用 JIT

这是 11/11 实际用过的 Mac 辅助路线，解决了应用内跳转误报，又保留了该进程刚完成的云存档检查。它不是自动安装脚本。

1. 从你使用的 Madeira IPA 取出配套 `madeira-jit.js`，在 StikDebug 导入并关联 Madeira。脚本和 Madeira 版本需要匹配。
2. UU 下先打开 Madeira，等游戏云状态一致。
3. 切到 LocalDevVPN。
4. 获取当前 Madeira 的 PID，别拿上一次的 PID 继续用：

```bash
xcrun devicectl device info processes --device "$PHONE_ID"

MADEIRA_PID='填本次Madeira进程PID'
STIK_BUNDLE='填写实际的StikDebug包标识'
xcrun devicectl device process launch \
  --device "$PHONE_ID" \
  --payload-url "stikdebug://enable-jit?bundle-id=$MADEIRA_BUNDLE&pid=$MADEIRA_PID&script-name=madeira-jit.js" \
  "$STIK_BUNDLE"
```

5. 在 StikDebug 确认运行已导入的配套脚本，回 Madeira 点 Play。
6. 等 JIT 池就绪并完成调试器脱离，再恢复 UU，等待 Steam 认证和画面。

StikDebug 应用列表直接点 Madeira 可能会重新启动应用，这与给现有 PID 附加有区别。重启会丢掉当前应用进程刚做过的云检查状态，别以为两种方式完全一样。

上游入口说明：[StikJIT Integration](https://github.com/StikDebug/StikJIT/blob/main/INTEGRATION.md)。实际参数还应以你安装的 StikDebug 版本为准。

## 出了问题怎么回退

配置改动只恢复对应 cfg。游戏程序、运行库改动分别恢复各自原件。签名更新保留同一应用身份及容器数据。云存档冲突则先比较两份内容，别和程序回退混成一次覆盖。

仓库里的 `private/`、`backups/`、`downloads/`、`artifacts/` 都被 Git 忽略。它们只是本机工作目录，不应上传。
