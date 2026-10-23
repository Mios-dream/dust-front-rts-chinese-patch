# Dust Front RTS 中文翻译补丁

本补丁针对 Unity `2020.3.3f1` Windows 版本制作，修改内容包括：

- 主菜单、设置、教程、任务、单位、建筑、能力、学说和装备描述
- `resources.assets` 中的 705 条本地化文本
- TextMeshPro 的中文 fallback 字体

## 安装

先关闭游戏，在 PowerShell 中执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1 -GamePath "你的 Steam\steamapps\common\Dust Front RTS"
```

安装脚本会校验 Steam 资源版本，并在替换前创建带时间戳的备份。卸载时执行：

```powershell
.\uninstall.ps1 -GamePath "你的 Steam\steamapps\common\Dust Front RTS"
```

如果 Steam 自动更新了游戏，脚本默认会拒绝应用旧补丁。请先重新制作对应版本的补丁，不要直接使用 `-Force`。

字体使用 Noto Sans CJK SC 的子集，许可证见 `OFL.txt`。
