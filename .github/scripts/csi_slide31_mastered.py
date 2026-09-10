from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

replacements = {
    "Deux paradigmes stabilisés ouvrent la deuxième année": "Deux paradigmes maîtrisés ouvrent la deuxième année",
    "Paradigme, protocole, mesures et analyses sont stabilisés.": "Paradigme, protocole, mesures et analyses sont maîtrisés.",
}

for old, new in replacements.items():
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"Expected text not found: {old}")
    text = text.replace(old, new)
    print(f"Replaced {count} occurrence(s): {old} -> {new}")

path.write_text(text, encoding="utf-8")
