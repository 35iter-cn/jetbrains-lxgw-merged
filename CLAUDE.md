# Claude Code 工作指引

本文件给 Claude Code（以及未来的自己）看：如何在这个仓库里构建字体并发布 release。

## 本地构建 `JetBrainsMono-LXGW-Merged.ttf`

### 1. 准备环境

```bash
cd /root/code/jetbrains-lxgw-merged
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

依赖只有 `fonttools` 和 `requests`。WSL/Windows 还需要 `unzip`。

### 2. 执行构建

```bash
python build.py
```

构建流程：
1. `download.py` 下载 JetBrainsMono NFM Regular 和 LXGW 文楷 GB 等宽体 Regular
2. `merge.py` 把中文字符合并到西文字体
3. `patch_u23f8.py` 把 `U+23F8`（⏸）字形从 `assets/u23f8-glyph.ttf`  patch 进去

输出文件：

```
dist/JetBrainsMono-LXGW-Merged.ttf
```

### 3. 验证字体包含 U+23F8

```bash
python - <<'PY'
from fontTools.ttLib import TTFont
f = TTFont('dist/JetBrainsMono-LXGW-Merged.ttf')
cmap = f['cmap'].getBestCmap()
print('U+23F8 present:', 0x23F8 in cmap)
PY
```

## 发布 GitHub Release

### 前提

- 已安装并登录 GitHub CLI：`gh auth status`
- 当前版本号用 `v{major}.{minor}.{patch}`，例如 `v1.0.0`
- `dist/JetBrainsMono-LXGW-Merged.ttf` 已生成

### 推荐命令

```bash
VERSION="v1.0.0"
NOTES_FILE="/tmp/release-notes.md"

cat > "$NOTES_FILE" <<'EOF'
## 变更内容

- 更新 JetBrainsMono NFM 到 x.x.x
- 更新 LXGW 文楷 GB 等宽体到 x.x.x
- 修复/改进 …

## 安装

1. 下载 `JetBrainsMono-LXGW-Merged.ttf`
2. 右键 → 为所有用户安装（Windows）或双击安装（macOS）
3. 在 Alacritty 配置里设置 `normal.family = "JetBrainsMono LXGW Merged"`
4. 完全重启 Alacritty

## 构建方式

见仓库 `README.md` 或 `claude.md`。
EOF

gh release create "$VERSION" \
  --repo 35iter-cn/jetbrains-lxgw-merged \
  --title "$VERSION - JetBrainsMono LXGW Merged" \
  --notes-file "$NOTES_FILE" \
  "dist/JetBrainsMono-LXGW-Merged.ttf"
```

### 重要提示

- **不要用 `--notes` 直接写包含反引号的多行字符串**，Bash 会把反引号当命令替换执行，导致 `gh` 报错或生成奇怪内容。
- 推荐用 `--notes-file` 从文件读取 release notes，安全且可复用。
- 如果只想更新 release notes 或替换 asset，先删除旧 release：`gh release delete "$VERSION" --repo 35iter-cn/jetbrains-lxgw-merged --yes`。

### 验证发布

```bash
gh release view "$VERSION" --repo 35iter-cn/jetbrains-lxgw-merged
```

确认 asset `JetBrainsMono-LXGW-Merged.ttf` 已列出即可。
