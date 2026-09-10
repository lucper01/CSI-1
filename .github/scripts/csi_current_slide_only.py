from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

replacements = {
    '<span id="slideCounter" class="slide-counter">1 / 32</span>': '<span id="slideCounter" class="slide-counter">1</span>',
    "document.getElementById('slideCounter').textContent=`${pos+1} / ${vis.length}`;": "document.getElementById('slideCounter').textContent=`${pos+1}`;",
}

for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly 1 occurrence, found {count}: {old}")
    text = text.replace(old, new)
    print(f"Replaced: {old} -> {new}")

path.write_text(text, encoding="utf-8")
