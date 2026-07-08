# jetbrains-lxgw-merged

Automatically merge **JetBrainsMono NFM** with **LXGW WenKai GB Mono** for a single CJK-ready programming font, plus a built-in `U+23F8` pause symbol patch.

## Why

`JetBrainsMono` is an excellent Latin programming font, but on Windows Alacritty falls back to system fonts for CJK characters and some symbols like `⏸` (U+23F8). This project builds a single TTF that contains:

- JetBrainsMono NFM for Latin / Nerd Font icons
- LXGW WenKai GB Mono for CJK glyphs
- A text-style `U+23F8` pause symbol from Sarasa Mono SC

The output font keeps the family name `JetBrainsMono LXGW Merged` so it can directly replace the manually merged version you may already be using.

## Why Only Regular Weight

This project currently builds **only the Regular weight**. Reasons:

1. `LXGW WenKai GB Mono` only provides ExtraLight / Light / Regular + Italics. It does not ship Medium, SemiBold, or Bold.
2. Keeping the build to a single weight makes the script easy to understand and maintain.
3. For terminal use, Regular is usually sufficient; Alacritty can synthesize bold/italic when needed.
4. Extending to multiple weights is straightforward once the core merge logic is stable — contributions welcome.

## Requirements

```bash
pip install -r requirements.txt
```

- Python 3.10+
- `fonttools`
- `requests`

On Windows/WSL you also need `unzip` and `curl` or `requests` for downloading.

## Usage

```bash
python build.py
```

This downloads the source fonts and produces:

```
dist/JetBrainsMono-LXGW-Merged.ttf
```

You can override download URLs:

```bash
python build.py \
  --jb-url "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/JetBrainsMono.zip" \
  --lxgw-url "https://github.com/lxgw/LxgwWenkaiGB/releases/download/v1.522/LXGWWenKaiMonoGB-Regular.ttf"
```

## Project Layout

```
.
├── assets/
│   └── u23f8-glyph.ttf       # Built-in U+23F8 glyph (from Sarasa Mono SC Regular)
├── examples/
│   └── alacritty.toml        # Example Alacritty font config
├── build.py                  # Main entry: download → merge → patch
├── download.py               # Download source fonts
├── merge.py                  # Merge JetBrainsMono + LXGW WenKai GB
├── patch_u23f8.py            # Insert built-in U+23F8 glyph
├── requirements.txt
├── LICENSE                   # MIT for scripts
├── OFL.txt                   # Font attribution
└── README.md
```

## Install the Generated Font

The project itself only generates the TTF. To install on Windows, **do not just copy the file** — the font must be registered in the Windows font collection or DirectWrite will not find it.

### GUI method

Right-click `dist/JetBrainsMono-LXGW-Merged.ttf` → **Install for all users**.

### PowerShell method (system-wide, requires admin)

```powershell
$shell = New-Object -ComObject Shell.Application
$fontFolder = $shell.Namespace(0x14)  # SSF_FONTS
$fontFolder.CopyHere("C:\path\to\JetBrainsMono-LXGW-Merged.ttf", 0x14)
```

### PowerShell method (per-user, no admin required)

```powershell
$shell = New-Object -ComObject Shell.Application
$fontFolder = $shell.Namespace(0x14)
$fontFolder.CopyHere("$env:USERPROFILE\code\jetbrains-lxgw-merged\dist\JetBrainsMono-LXGW-Merged.ttf", 0x14)
```

Then restart Alacritty.

> **Why not `Copy-Item`?** Copying a `.ttf` into `C:\Windows\Fonts` or the per-user font directory does not register it. Alacritty will panic with `Result::unwrap() on an Err value: -2003283965` because DirectWrite cannot resolve the font family name.

## Alacritty Config

```toml
[font]
normal.family = "JetBrainsMono LXGW Merged"
size = 12.0
```

See `examples/alacritty.toml` for a fuller example.

## License

- Python scripts: **MIT License** (see `LICENSE`)
- Generated fonts and included glyph assets: derived from OFL-licensed fonts (see `OFL.txt`)

The generated font must remain under the SIL Open Font License. Do not relicense the font itself under MIT.

## Acknowledgements

- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)
- [LXGW WenKai](https://github.com/lxgw/LxgwWenkai) / [LXGW WenKai GB](https://github.com/lxgw/LxgwWenkaiGB)
- [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic)
