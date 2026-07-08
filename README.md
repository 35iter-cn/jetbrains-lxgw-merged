# jetbrains-lxgw-merged

自动合并 **JetBrainsMono NFM** 与 **LXGW 文楷 GB 等宽体** 的编程字体，并内置 `⏸`（U+23F8）暂停符号补丁。

## 这个字体解决什么问题

### ✅ 修复 Claude Code plan mode 符号与文字重叠

如果你在用 **Alacritty + Claude Code**，进入 plan mode 时底部会显示：

```
⏸ plan mode on
```

当字体缺少 `⏸`（U+23F8）时，Windows 上的 Alacritty 会 fallback 到 **Segoe UI Emoji**，把它渲染成带边框的 emoji。这个 emoji 宽度超过一个单元格，导致 `⏸` 和右侧文字**左右重叠**。

本仓库生成的 `JetBrainsMono LXGW Merged` 内置了文本样式的 `U+23F8`，让暂停符号保持等宽，**不再重叠**。

### ✅ 中西文混排更统一

`JetBrainsMono` 西文优秀，但中文会 fallback 到系统字体。本字体把 LXGW 文楷 GB 的中文合并进来，西文保持 JetBrainsMono，终端里中英文风格一致。

## 为什么只做 Regular 字重

## 为什么只做 Regular 字重

本仓库目前**只生成 Regular 一个字重**，原因如下：

1. `LXGW 文楷 GB 等宽体` 只提供 ExtraLight / Light / Regular（及对应 Italic），没有 Medium、SemiBold、Bold。
2. 先保证 Regular 合并逻辑稳定，脚本易于理解和维护。
3. 终端里 Regular 通常够用，Alacritty 会在需要时自动合成粗体/斜体。
4. 后续扩展多字重很简单，只需把 `for weight in [...]` 打开即可。

## 依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Python 3.10+
- `fonttools`
- `requests`

Windows/WSL 下还需要 `unzip` 用来解压 Nerd Fonts 的 zip 包。

## 使用方法

```bash
python build.py
```

构建完成后输出：

```
dist/JetBrainsMono-LXGW-Merged.ttf
```

也可以手动指定下载地址：

```bash
python build.py \
  --jb-url "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/JetBrainsMono.zip" \
  --lxgw-url "https://github.com/lxgw/LxgwWenkaiGB/releases/download/v1.522/LXGWWenKaiMonoGB-Regular.ttf"
```

## 项目结构

```
.
├── assets/
│   └── u23f8-glyph.ttf       # 内置 U+23F8 字形（来自 Sarasa Mono SC Regular）
├── examples/
│   └── alacritty.toml        # Alacritty 配置示例
├── build.py                  # 主入口：下载 → 合并 → 打补丁
├── download.py               # 下载字体源文件
├── merge.py                  # 合并 JetBrainsMono + LXGW 文楷 GB
├── patch_u23f8.py            # 插入内置 U+23F8 字形
├── requirements.txt
├── LICENSE                   # 脚本使用 MIT 协议
├── OFL.txt                   # 字体归属与授权声明
├── README.md                 # 本文件（中文）
└── README.en.md              # English README
```

## 安装生成的字体

本仓库只负责生成 TTF，安装需要你自己完成。**不要直接复制文件**，否则 Windows 不会注册字体，Alacritty 会崩溃并报错 `-2003283965`。

### 图形界面安装

右键 `dist/JetBrainsMono-LXGW-Merged.ttf` → **为所有用户安装**。

### PowerShell 安装（系统级，需要管理员）

```powershell
$shell = New-Object -ComObject Shell.Application
$fontFolder = $shell.Namespace(0x14)
$fontFolder.CopyHere("C:\path\to\JetBrainsMono-LXGW-Merged.ttf", 0x14)
```

### PowerShell 安装（仅当前用户，无需管理员）

```powershell
$shell = New-Object -ComObject Shell.Application
$fontFolder = $shell.Namespace(0x14)
$fontFolder.CopyHere("$env:USERPROFILE\code\jetbrains-lxgw-merged\dist\JetBrainsMono-LXGW-Merged.ttf", 0x14)
```

安装完成后**完全重启 Alacritty**。

## Alacritty 配置

```toml
[font]
normal.family = "JetBrainsMono LXGW Merged"
size = 12.0
```

更完整的示例见 `examples/alacritty.toml`。

## 直接下载 Release 字体

如果不想自己构建，可以直接从 GitHub Release 下载已生成好的 `JetBrainsMono-LXGW-Merged.ttf`：

> https://github.com/35iter-cn/jetbrains-lxgw-merged/releases

## 许可证

- Python 脚本：**MIT 许可证**（见 `LICENSE`）
- 生成的字体及内置字形资源：衍生自 SIL Open Font License 字体（见 `OFL.txt`）

生成后的字体必须继续遵守 SIL Open Font License，请勿将字体本身改为 MIT 或其他协议。

## 致谢

- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)
- [LXGW 文楷](https://github.com/lxgw/LxgwWenkai) / [LXGW 文楷 GB](https://github.com/lxgw/LxgwWenkaiGB)
- [Sarasa Gothic / 更纱黑体](https://github.com/be5invis/Sarasa-Gothic)

## English Documentation

See [README.en.md](README.en.md).
