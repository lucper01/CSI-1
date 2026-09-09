from pathlib import Path
import hashlib

p = Path("index.html")
save = Path("index_save.html")
before_save = hashlib.sha256(save.read_bytes()).hexdigest()
text = p.read_text(encoding="utf-8")

marker = "/* CSI_FULL_AXIS_BADGE */"
start = text.index(marker)
end = text.index("</style>", start)
block = text[start:end]

if "font-size: .66rem !important;" not in block:
    old = ".study-axis-badge {\n  max-width: min(100%, 860px);\n  padding: 4px 10px !important;"
    new = ".study-axis-badge {\n  max-width: min(100%, 860px);\n  padding: 4px 10px !important;\n  font-size: .66rem !important;"
    assert old in block
    block = block.replace(old, new, 1)

block = block.replace(
    ".study-axis-badge { max-width: 100%; font-size: .48rem; }",
    ".study-axis-badge { max-width: 100%; font-size: .56rem !important; }"
)

text = text[:start] + block + text[end:]
p.write_text(text, encoding="utf-8")

out = p.read_text(encoding="utf-8")
assert "font-size: .66rem !important;" in out
assert "font-size: .56rem !important;" in out
assert hashlib.sha256(save.read_bytes()).hexdigest() == before_save
