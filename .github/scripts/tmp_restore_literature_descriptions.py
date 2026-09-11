from pathlib import Path
import html
import json
import re

PATH = Path("index.html")
text = PATH.read_text(encoding="utf-8")
MARKER = "CSI_LITERATURE_MINI_DESCRIPTIONS_V1"
if MARKER in text:
    raise SystemExit("Literature mini descriptions already applied")

FR = {
    "Vision et audition - espace et temps ne pèsent pas pareil": [
        "La vision privilégie davantage l’espace, l’audition davantage le temps dans leurs interférences réciproques.",
        "L’attention spatiale et temporelle interagissent selon le contexte et la tâche.",
        "La structure temporelle dépend des contraintes propres à chaque système sensoriel.",
        "La fenêtre de synchronie varie selon les combinaisons sensorielles.",
    ],
    "Le temps - des événements que l’on sait organiser": [
        "Début, présence et fin peuvent être perçus et jugés séparément.",
        "Deux événements peuvent être comparés selon leur simultanéité perçue.",
        "Une certaine asynchronie reste compatible avec un événement perceptif unique.",
    ],
    "L’espace - des signaux que l’on sait organiser": [
        "Vision et audition extraient la position à partir d’indices différents.",
        "Direction, distance et profondeur organisent la scène au-delà de la position.",
        "La cohérence spatiale aide à attribuer plusieurs signaux à une même source.",
    ],
    "Espace + temps - organiser un même événement": [
        "Un événement peut produire plusieurs signaux sensoriels à regrouper.",
        "Des positions compatibles renforcent l’hypothèse d’une source commune.",
        "Une proximité temporelle suffisante favorise l’intégration multisensorielle.",
    ],
    "Deux organisations spatio-temporelles": [
        "Positions et limites de scène sont explicites, tandis que le temps se lit dans les changements.",
        "Onsets, rythme et synchronie sont précis, tandis que l’espace est reconstruit acoustiquement.",
    ],
    "« No space, no time? » - le paradoxe de l’attention olfactive": [
        "La localisation olfactive humaine reste grossière comparée à la vision et à l’audition.",
        "Le signal est échantillonné par les inspirations et la dynamique de délivrance.",
        "STOLF teste si ces spécificités limitent l’accès à l’espace et au temps olfactifs.",
    ],
    "Less space, less time": [
        "Proximité, concentration et respiration structurent déjà l’expérience olfactive.",
        "Des changements peuvent survenir sans devenir saillants pour l’attention consciente.",
        "Les dimensions spatiales et temporelles sont moins accessibles, mais bien présentes.",
    ],
    "Influence Olfactive ?": [
        "Un contexte olfactif peut faciliter la catégorisation de stimuli visuels ambigus.",
        "Des odeurs relaxantes ou stimulantes peuvent moduler le tempo musical préféré.",
    ],
}

EN = {
    "Vision et audition - espace et temps ne pèsent pas pareil": [
        "Vision gives greater weight to space, while audition gives greater weight to time.",
        "Spatial and temporal attention interact depending on context and task demands.",
        "Temporal structure depends on constraints specific to each sensory system.",
        "The synchrony window varies across sensory combinations.",
    ],
    "Le temps - des événements que l’on sait organiser": [
        "Onset, presence and offset can be perceived and judged separately.",
        "Two events can be compared according to their perceived simultaneity.",
        "Some asynchrony remains compatible with a single perceived event.",
    ],
    "L’espace - des signaux que l’on sait organiser": [
        "Vision and audition recover position from different spatial cues.",
        "Direction, distance and depth organize a scene beyond absolute position.",
        "Spatial coherence helps assign multiple signals to a common source.",
    ],
    "Espace + temps - organiser un même événement": [
        "One event can generate several sensory signals that must be grouped.",
        "Compatible locations strengthen the hypothesis of a common source.",
        "Sufficient temporal proximity promotes multisensory integration.",
    ],
    "Deux organisations spatio-temporelles": [
        "Positions and scene boundaries are explicit, while time is read through change and order.",
        "Onsets, rhythm and synchrony are precise, while space is reconstructed from acoustic cues.",
    ],
    "« No space, no time? » - le paradoxe de l’attention olfactive": [
        "Human olfactory localization remains coarse compared with vision and audition.",
        "Olfactory input is sampled through inspirations and stimulus-delivery dynamics.",
        "STOLF tests whether these specificities limit access to olfactory space and time.",
    ],
    "Less space, less time": [
        "Distance, concentration and respiration already structure olfactory experience.",
        "Changes can occur without becoming salient to conscious attention.",
        "Spatial and temporal dimensions are less accessible, but not absent.",
    ],
    "Influence Olfactive ?": [
        "An olfactory context can facilitate categorization of ambiguous visual stimuli.",
        "Relaxing or stimulating odors can modulate preferred musical tempo.",
    ],
}

prefix = "const slides = "
start = text.index(prefix) + len(prefix)
slides, used = json.JSONDecoder().raw_decode(text[start:])
end = start + used

def inject(content, descriptions):
    if "lit-mini" in content:
        raise SystemExit("Unexpected pre-existing lit-mini block")
    i = 0
    def repl(match):
        nonlocal i
        if i >= len(descriptions):
            return match.group(0)
        desc = html.escape(descriptions[i], quote=False)
        i += 1
        return f'</h3><div class="lit-mini">{desc}</div></div>'
    out, _ = re.subn(r'</h3></div>', repl, content)
    if i != len(descriptions):
        raise SystemExit(f"Expected {len(descriptions)} cards, inserted {i}")
    return out

changed = []
for slide in slides:
    title = slide.get("title")
    if title not in FR:
        continue
    if not slide.get("_theory_cards_compacted"):
        raise SystemExit(f"Target slide is not marked compacted: {title}")
    slide["content"] = inject(slide["content"], FR[title])
    if isinstance(slide.get("_fr"), dict) and slide["_fr"].get("content"):
        slide["_fr"]["content"] = inject(slide["_fr"]["content"], FR[title])
    if isinstance(slide.get("_en"), dict) and slide["_en"].get("content"):
        slide["_en"]["content"] = inject(slide["_en"]["content"], EN[title])
    slide["_literature_mini_descriptions"] = "v1"
    changed.append(title)

if set(changed) != set(FR):
    missing = set(FR) - set(changed)
    extra = set(changed) - set(FR)
    raise SystemExit(f"Target mismatch. Missing={missing}, extra={extra}")

new_array = json.dumps(slides, ensure_ascii=False, indent=2)
text = text[:start] + new_array + text[end:]

style = f'''\n  <style id="csi-literature-mini-descriptions-v1">\n    /* {MARKER} */\n    .card .lit-mini {{ margin-top:.52rem; font-size:clamp(.70rem,.78vw,.80rem); line-height:1.34; color:var(--muted); font-weight:650; }}\n    .card.dark .lit-mini {{ color:rgba(255,255,255,.80); }}\n    @media(max-width:900px) {{ .card .lit-mini {{ font-size:.70rem; line-height:1.28; }} }}\n  </style>\n'''
head_close = "</head>"
if text.count(head_close) != 1:
    raise SystemExit("Unexpected </head> count")
text = text.replace(head_close, style + head_close, 1)

PATH.write_text(text, encoding="utf-8")
print(f"Updated {len(changed)} literature/theory slides with concise descriptions")
for title in changed:
    print(" -", title)
