# 已知限制与改进建议

本文件记录当前构建脚本和生成字体的已知限制，以及未来可以改进的方向。

## 1. `merge.py` 跳过非 BMP 字符

### 现象

`merge.py` 在合并 LXGW 文楷 GB 字符时，跳过了所有 `codepoint > 0xFFFF` 的字符：

```python
if codepoint > 0xFFFF:
    skipped += 1
    continue  # Skip non-BMP codepoints to avoid cmap format 4 overflow
```

当前构建结果：LXGW 源字体中有 **3,012 个非 BMP 字符** 未被合并到最终字体中。

### 影响

- 合并后的字体仍然包含 JetBrainsMono NFM 原有的非 BMP 字符（主要是 Nerd Fonts 图标）。
- 丢失的是 LXGW 中非 BMP 的字符，主要是 **CJK 扩展区罕用汉字**。
- 日常编程、终端显示用到的 99.9% 字符都在 BMP 内，因此影响很小。

### 建议修改

如果确实需要支持这些罕用汉字，可以：

1. 保留跳过逻辑作为可选项（`--skip-non-bmp`）。
2. 默认情况下合并所有字符：
   - 对 `cmap` format 12 表写入非 BMP 字符。
   - 对 `cmap` format 4 表继续跳过非 BMP（format 4 本身不支持）。
3. 合并后验证 `cmap` format 12 是否正确包含非 BMP 字符。

---

## 2. 中文 OpenType 特性表未合并

### 现象

`merge.py` 只复制了 `glyf`（字形）和 `hmtx`（水平宽度），没有合并 LXGW 的 `GSUB`、`GPOS`、`GDEF` 表。

合并后的字体中，`GSUB`/`GPOS`/`GDEF` 仍然是 JetBrainsMono NFM 原表的内容。

### 影响

| 表 | 丢失的能力 |
|---|---|
| `GSUB` | 中文连字、替代字形 |
| `GPOS` | 中文字偶距、位置调整 |
| `GDEF` | 中文标记符号、基字符定义 |

- 终端和代码编辑基本无感知，因为终端主要关心「字符是否存在、宽度是否正确」。
- 如果用于中文排版（如 LibreOffice、InDesign），字距和排版效果可能不如原版 LXGW。

### 建议修改

- 评估是否真的需要：如果只是终端字体，可以维持现状。
- 如果需要，可以尝试使用 `fontTools.merge` 模块，或者手动合并特性表，同时处理 glyph 名冲突。
- 修改后需要对比原版 LXGW 和合并后的字体在不同应用中的渲染效果。

---

## 3. `OS/2` 代码页位图未更新

### 现象

合并后的字体虽然实际包含了大量中文字符，但 `OS/2` 表的 `ulUnicodeRange` 和 `ulCodePageRange` 字段仍然沿用了 JetBrainsMono NFM 原表的值，没有根据实际 `cmap` 重新计算。

### 影响

- **Windows 字体列表**：系统可能不把这个字体识别为「中文字体」，导致某些按代码页筛选的应用无法列出它。
- **Alacritty / VS Code**：直接按字体名加载，不走这个位图筛选，因此不受影响。
- **Microsoft Office / 浏览器**：如果应用依赖 `OS/2` 位图做字体 fallback，可能选不到这个字体。

### 建议修改

合并完成后，根据最终 `cmap` 重新计算并设置：

- `OS/2.ulUnicodeRange`：声明覆盖的 Unicode 区块。
- `OS/2.ulCodePageRange`：声明支持的 Windows 代码页（如 936 简体中文、950 繁体中文）。

fontTools 的 `fontTools.ttLib.tables.O_S_2f_2` 可以手动设置这些位，但需要自己计算哪些位需要置 1。

---

## 4. `name` 表输出显示为 bytes（正常现象）

### 现象

在调试输出中，`name` 表的字符串可能显示为 `b'JetBrainsMono LXGW Merged'` 或 `b'\x00J\x00e...'`。

### 说明

这不是 bug，而是 `name` 表的正常存储方式：

- **platformID=0（Macintosh）**：字符串按字节存储。
- **platformID=3（Windows）**：字符串使用 UTF-16-BE 编码存储。

`merge.py` 已经正确更新了 nameID 1、4、6、16、17，Windows 和 macOS 都能正确识别字体名。

### 建议

无需修改。如果未来需要让调试输出更可读，可以在脚本里根据 `record.platformID` 和 `record.platEncID` 解码后再打印。

---

## 验证命令

检查 `cmap` 覆盖范围：

```python
from fontTools.ttLib import TTFont
font = TTFont('dist/JetBrainsMono-LXGW-Merged.ttf')
cmap = font['cmap'].getBestCmap()
print(f'Total codepoints: {len(cmap)}')
print(f'Non-BMP codepoints: {sum(1 for cp in cmap if cp > 0xFFFF)}')
```

检查 `OS/2` 代码页位图：

```python
from fontTools.ttLib import TTFont
font = TTFont('dist/JetBrainsMono-LXGW-Merged.ttf')
os2 = font['OS/2']
print(f'ulUnicodeRange: {os2.ulUnicodeRange}')
print(f'ulCodePageRange: {os2.ulCodePageRange}')
```
