from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

# Requested French wording changes. Each visible French value is duplicated in
# the slide object's _fr block and its active top-level fields.
replacements = [
    ("<h3>Le verrou à lever</h3>", "<h3>Un manque à combler</h3>", 2),
    ('"title": "Une influence olfactive est plausible"', '"title": "Influence Olfactive ?"', 2),
]
for old, new, expected in replacements:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"Expected {expected} occurrence(s), found {count}: {old}")
    text = text.replace(old, new)
    print(f"Replaced {count} occurrence(s): {old} -> {new}")

# Remove the complete slide object entitled "Ce qui a été fait cette année".
array_marker = "const slides = ["
array_pos = text.find(array_marker)
if array_pos < 0:
    raise SystemExit("slides array not found")
array_start = text.find("[", array_pos) + 1
marker = '"title": "Ce qui a été fait cette année"'


def matching_brace(s, start):
    depth = 0
    in_string = False
    quote = ""
    escaped = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                in_string = False
            continue
        if ch in ('"', "'"):
            in_string = True
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    raise SystemExit("Unmatched slide object brace")

objects = []
i = array_start
while i < len(text):
    while i < len(text) and text[i] in " \t\r\n,":
        i += 1
    if i >= len(text) or text[i] == "]":
        break
    if text[i] != "{":
        raise SystemExit(f"Unexpected token in slides array at {i}: {text[i:i+20]!r}")
    end = matching_brace(text, i)
    objects.append((i, end, text[i:end + 1]))
    i = end + 1

matches = [(start, end) for start, end, obj in objects if marker in obj]
if len(matches) != 1:
    raise SystemExit(f"Expected exactly one matching slide object, found {len(matches)}")

start, end = matches[0]
remove_end = end + 1
while remove_end < len(text) and text[remove_end] in " \t\r":
    remove_end += 1
if remove_end < len(text) and text[remove_end] == ",":
    remove_end += 1
text = text[:start] + text[remove_end:]

if marker in text:
    raise SystemExit("Target slide title still present after removal")

path.write_text(text, encoding="utf-8")
print(f"Removed 1 complete slide object; slide objects before removal: {len(objects)}")
