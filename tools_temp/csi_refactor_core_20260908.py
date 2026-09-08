from pathlib import Path
import copy
import json
import re
import hashlib

PATH = Path('index.html')
BACKUP = Path('index_save.html')
text = PATH.read_text(encoding='utf-8')
backup_hash = hashlib.sha256(BACKUP.read_bytes()).hexdigest()
EXPECTED_BACKUP_BLOB_CONTENT_SHA256 = '9948fe7ffbb327340129d83624a51611d7325f3c171fd0834e3e5f7f81c307fe'
if backup_hash != EXPECTED_BACKUP_BLOB_CONTENT_SHA256:
    raise RuntimeError(f'Backup changed before refactor: {backup_hash}')

MARKER = 'const slides = '
start = text.index(MARKER) + len(MARKER)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end
if len(slides) != 64:
    raise RuntimeError(f'Expected 64 source slides, got {len(slides)}')
old = {i + 1: copy.deepcopy(s) for i, s in enumerate(slides)}

AXIS1_FR = "Limites spatio-temporelles de l'olfaction vs celles de la vision et de l'audition"
AXIS2_FR = "Influence de l'olfaction sur la perception spatio-temporelle en audition et en vision"
AXIS1_EN = 'Spatiotemporal limits of olfaction vs those of vision and audition'
AXIS2_EN = 'Influence of olfaction on spatiotemporal perception in audition and vision'

PARTS_FR = ['Introduction', 'Cadre théorique', 'Année 1', 'Année 2', 'Suite', 'Valorisation', 'Planning']
PARTS_EN = ['Introduction', 'Theory', 'Year 1', 'Year 2', 'Next', 'Dissemination', 'Planning']


def block(section, kicker, title, lead, content, notes=''):
    return {
        'section': section,
        'kicker': kicker,
        'title': title,
        'lead': lead,
        'content': content,
        'notes': notes,
    }


def apply_lang(s, fr, en):
    s['_fr'] = fr
    s['_en'] = en
    s.update(fr)
    return s


def rewrite(idx, fr, en, *, chapter=None, study=None, appendix=None, part=None):
    s = copy.deepcopy(old[idx])
    apply_lang(s, fr, en)
    if chapter is not None:
        s['chapter'] = chapter
    if study is not None:
        s['study'] = study
    if appendix is not None:
        s['appendix'] = appendix
    if part is not None:
        s['_csi_part'] = part
    return s


def new_from(idx, fr, en, *, chapter='', study='', appendix=False, part=None):
    s = copy.deepcopy(old[idx])
    for k in list(s):
        if k not in {'className', 'layout'}:
            s.pop(k, None)
    s.update({'chapter': chapter, 'study': study, 'appendix': appendix})
    apply_lang(s, fr, en)
    if part is not None:
        s['_csi_part'] = part
    return s


def divider(idx, fr_title, en_title, part_number, part_key):
    fr = block(fr_title, '', fr_title, '', f'<div class="section-divider-inner"><span class="section-divider-number">PARTIE {part_number}</span><h1>{fr_title}</h1><i aria-hidden="true"></i></div>')
    en = block(en_title, '', en_title, '', f'<div class="section-divider-inner"><span class="section-divider-number">PART {part_number}</span><h1>{en_title}</h1><i aria-hidden="true"></i></div>')
    return rewrite(idx, fr, en, chapter=fr_title, study='', appendix=False, part=part_key)


def make_timeline(part, english=False):
    parts = PARTS_EN if english else PARTS_FR
    active = {
        'Introduction': 0,
        'Cadre théorique': 1,
        'Année 1': 2,
        'Année 2': 3,
        'Suite': 4,
        'Valorisation': 5,
        'Planning': 6,
    }.get(part, -1)
    spans = []
    for i, label in enumerate(parts):
        cls = ' active' if i == active else ''
        spans.append(f'<span class="csi-part-node{cls}">{label}</span>')
    return '<nav class="csi-part-timeline" aria-label="Progression">' + '<i></i>'.join(spans) + '</nav>'


def axis_html(study, english=False):
    a1 = {'TWIXAV', 'SOFT', 'TWIXOLF', 'SOLAR', 'SORBET'}
    a2 = {'VIBEX', 'OASIS', 'BRAUD', 'BRAUDOLF', 'COBEX'}
    if study in a1:
        label = 'Axis 1' if english else 'Axe 1'
        name = AXIS1_EN if english else AXIS1_FR
        return f'<div class="csi-axis-tag axis1"><b>{label}</b><span>{name}</span></div>'
    if study in a2:
        label = 'Axis 2' if english else 'Axe 2'
        name = AXIS2_EN if english else AXIS2_FR
        return f'<div class="csi-axis-tag axis2"><b>{label}</b><span>{name}</span></div>'
    if study == 'FLUXOLF':
        return '<div class="csi-axis-tag side"><b>Side project</b><span>Outside the two STOLF thesis axes</span></div>' if english else '<div class="csi-axis-tag side"><b>Projet annexe</b><span>Hors des deux axes principaux de STOLF</span></div>'
    return ''


def decorate_slide(s):
    if s.get('appendix'):
        return s
    part = s.get('_csi_part')
    if not part:
        return s
    # Keep cover, summary, section dividers and final thanks visually clean.
    title = s.get('title', '')
    if title in {'Y a-t-il un espace-temps pour les odeurs ?', 'Sommaire', 'Merci pour votre attention'}:
        return s
    if 'section-divider-inner' in s.get('content', ''):
        return s
    for key, english in [('_fr', False), ('_en', True)]:
        h = s.get(key)
        if not h:
            continue
        strip = '<div class="csi-context-strip">' + make_timeline(part, english) + axis_html(s.get('study', ''), english) + '</div>'
        h['content'] = strip + h.get('content', '')
    s.update(s['_fr'])
    return s


def resources(study, apparatus, poster=True, m1=None, english=False):
    arr = []
    if poster:
        label = 'Poster' if english else 'Affiche'
        arr.append(f'<a class="float-card poster" href="affiches/{study}.pdf" target="_blank" rel="noopener"><b>{label}</b><span>{study}</span></a>')
    eqlabel = 'Equipment' if english else 'Appareillage'
    eqspan = 'View equipment' if english else "Voir l'appareillage"
    arr.append(f'<button class="float-card apparatus-open" type="button" data-apparatus-study="{study}" data-apparatus-items="{apparatus}"><b>{eqlabel}</b><span>{eqspan}</span></button>')
    if m1:
        mlabel = "Master's thesis" if english else 'Mémoire M1'
        arr.append(f'<div class="float-card m1"><b>{mlabel}</b><span>{m1}</span></div>')
    return f'<div class="study-floating" aria-label="Ressources {study}">' + ''.join(arr) + '</div>'


# ---------------------------------------------------------------------------
# Cover
# ---------------------------------------------------------------------------
cover = copy.deepcopy(old[1])
for key in ['_fr', '_en']:
    h = cover.get(key, {})
    c = h.get('content', '')
    # Add HDR only to Arnaud Leleu's qualification on the cover.
    pos = c.lower().find('arnaud')
    if pos >= 0:
        tail = c[pos:pos + 800]
        if key == '_fr':
            new_tail, n = re.subn(r'Maître de conférences(?!\s*HDR)', 'Maître de conférences HDR', tail, count=1, flags=re.I)
        else:
            new_tail, n = re.subn(r'Associate professor(?![^<]{0,20}HDR)', 'Associate professor - HDR', tail, count=1, flags=re.I)
        if n:
            c = c[:pos] + new_tail + c[pos + len(tail):]
    h['content'] = c
cover.update(cover.get('_fr', {}))
cover['_csi_part'] = 'Introduction'

# ---------------------------------------------------------------------------
# Summary and theory
# ---------------------------------------------------------------------------
som_fr = block('Sommaire', 'Parcours de la présentation', 'Sommaire', 'Un récit continu : comprendre le problème, montrer ce qui est acquis, puis situer la suite de la thèse.', '''
<div class="csi-agenda-grid">
  <article><b>01</b><h3>Cadre théorique</h3><p>Espace, temps, vision, audition, puis olfaction.</p></article>
  <article><b>02</b><h3>Programme de thèse</h3><p>Deux axes et filiation des études.</p></article>
  <article><b>03</b><h3>Année 1</h3><p>TWIXAV et VIBEX : références établies.</p></article>
  <article><b>04</b><h3>Année 2</h3><p>SOFT et OASIS : priorités expérimentales.</p></article>
  <article><b>05</b><h3>Suite de la thèse</h3><p>TWIXOLF et extensions conditionnelles.</p></article>
  <article><b>06</b><h3>Valorisation</h3><p>Communications et articles.</p></article>
  <article><b>07</b><h3>Rétroplanning</h3><p>Jusqu'à la soumission et la soutenance.</p></article>
</div>''')
som_en = block('Contents', 'Presentation roadmap', 'Contents', 'One continuous story: define the problem, show what is established, then locate the next steps of the PhD.', '''
<div class="csi-agenda-grid">
  <article><b>01</b><h3>Theoretical framework</h3><p>Space, time, vision, audition, then olfaction.</p></article>
  <article><b>02</b><h3>PhD programme</h3><p>Two axes and study genealogy.</p></article>
  <article><b>03</b><h3>Year 1</h3><p>TWIXAV and VIBEX: established references.</p></article>
  <article><b>04</b><h3>Year 2</h3><p>SOFT and OASIS: experimental priorities.</p></article>
  <article><b>05</b><h3>Next</h3><p>TWIXOLF and conditional extensions.</p></article>
  <article><b>06</b><h3>Dissemination</h3><p>Communications and papers.</p></article>
  <article><b>07</b><h3>Planning</h3><p>Up to submission and defense.</p></article>
</div>''')
summary_slide = rewrite(2, som_fr, som_en, chapter='Sommaire', study='', appendix=False, part='Introduction')

theory_divider = divider(3, 'Cadre théorique', 'Theoretical framework', 1, 'Cadre théorique')

t4_fr = block('Cadre théorique', 'Espace et temps', 'Vision et audition : deux référentiels spatio-temporels', 'Espace et temps sont fondamentaux, mais leur traitement n’est ni parfaitement indépendant ni identique entre modalités.', '''
<div class="csi-theory-four">
  <article><span>Espace ↔ temps</span><h3>Des systèmes interactifs</h3><p>L’attention spatiale et temporelle peut être dissociée, mais les deux dimensions interagissent.</p><small>Capizzi et al., 2023</small></article>
  <article><span>Vision ≠ audition</span><h3>Une asymétrie relative</h3><p>La vision et l’audition ne présentent pas le même profil d’interférences spatio-temporelles.</p><small>Occelli et al., 2023</small></article>
  <article><span>Structure temporelle</span><h3>Dans et entre les sens</h3><p>Le système perceptif organise des régularités temporelles unimodales et multisensorielles.</p><small>Di Stefano & Spence, 2025</small></article>
  <article><span>Synchronie</span><h3>Une fenêtre de tolérance</h3><p>La Temporal Binding Window décrit la plage d’asynchronie compatible avec un même événement perceptif.</p><small>Ampollini et al., 2024</small></article>
</div><div class="callout"><strong>Référentiel :</strong> ces deux modalités fournissent un cadre pour demander ensuite comment l’olfaction organise l’espace et le temps.</div>''')
t4_en = block('Theoretical framework', 'Space and time', 'Vision and audition: two spatiotemporal references', 'Space and time are fundamental, but their processing is neither fully independent nor identical across modalities.', '''
<div class="csi-theory-four">
  <article><span>Space ↔ time</span><h3>Interactive systems</h3><p>Spatial and temporal attention can be dissociated, yet the two dimensions interact.</p><small>Capizzi et al., 2023</small></article>
  <article><span>Vision ≠ audition</span><h3>A relative asymmetry</h3><p>Vision and audition do not show the same profile of spatiotemporal interference.</p><small>Occelli et al., 2023</small></article>
  <article><span>Temporal structure</span><h3>Within and between senses</h3><p>Perception organizes temporal regularities both within and across modalities.</p><small>Di Stefano & Spence, 2025</small></article>
  <article><span>Synchrony</span><h3>A tolerance window</h3><p>The Temporal Binding Window describes the range of asynchrony compatible with one perceptual event.</p><small>Ampollini et al., 2024</small></article>
</div><div class="callout"><strong>Reference frame:</strong> these modalities provide a benchmark for asking how olfaction organizes space and time.</div>''')
t4 = rewrite(4, t4_fr, t4_en, chapter='Cadre théorique', study='', appendix=False, part='Cadre théorique')

t5_fr = block('Cadre théorique', 'Organisation temporelle', 'Le temps - comment organisons-nous les événements ?', 'Percevoir le temps ne consiste pas à lire une horloge interne unique : plusieurs relations temporelles sont extraites des événements.', '''
<div class="csi-dimension-map time-map">
  <div class="dimension-core"><b>TEMPS</b><span>organiser le « quand »</span></div>
  <div class="dimension-track"><article><b>1</b><span>Ordre</span></article><i></i><article><b>2</b><span>Durée</span></article><i></i><article><b>3</b><span>Simultanéité</span></article><i></i><article><b>4</b><span>Rythme</span></article><i></i><article><b>5</b><span>Structure</span></article><i></i><article><b>6</b><span>Anticipation</span></article></div>
</div><div class="csi-mini-takehome">Ordre · durée · simultanéité · rythme · structure · prédiction</div>''')
t5_en = block('Theoretical framework', 'Temporal organization', 'Time - how do we organize events?', 'Perceiving time is not simply reading a single internal clock: several temporal relations are extracted from events.', '''
<div class="csi-dimension-map time-map"><div class="dimension-core"><b>TIME</b><span>organizing the “when”</span></div><div class="dimension-track"><article><b>1</b><span>Order</span></article><i></i><article><b>2</b><span>Duration</span></article><i></i><article><b>3</b><span>Synchrony</span></article><i></i><article><b>4</b><span>Rhythm</span></article><i></i><article><b>5</b><span>Structure</span></article><i></i><article><b>6</b><span>Prediction</span></article></div></div><div class="csi-mini-takehome">Order · duration · synchrony · rhythm · structure · prediction</div>''')
t5 = rewrite(5, t5_fr, t5_en, chapter='Cadre théorique', study='', appendix=False, part='Cadre théorique')

t6_fr = block('Cadre théorique', 'Organisation spatiale', 'L’espace - comment organisons-nous les sources ?', 'Percevoir l’espace revient à construire des relations entre soi, les objets et les sources à partir d’indices sensoriels.', '''
<div class="csi-dimension-map space-map">
  <div class="dimension-core"><b>ESPACE</b><span>organiser le « où »</span></div>
  <div class="dimension-orbit"><article>Position</article><article>Direction</article><article>Distance</article><article>Localisation</article><article>Relations</article><article>Organisation</article></div>
</div><div class="csi-mini-takehome">Les modalités n’accèdent pas toutes aux mêmes indices spatiaux avec la même précision.</div>''')
t6_en = block('Theoretical framework', 'Spatial organization', 'Space - how do we organize sources?', 'Perceiving space means building relations between oneself, objects and sources from sensory cues.', '''
<div class="csi-dimension-map space-map"><div class="dimension-core"><b>SPACE</b><span>organizing the “where”</span></div><div class="dimension-orbit"><article>Position</article><article>Direction</article><article>Distance</article><article>Localization</article><article>Relations</article><article>Organization</article></div></div><div class="csi-mini-takehome">Modalities do not access the same spatial cues with the same precision.</div>''')
t6 = rewrite(6, t6_fr, t6_en, chapter='Cadre théorique', study='', appendix=False, part='Cadre théorique')

t7_fr = block('Cadre théorique', 'Espace × temps', 'Un même événement doit être situé dans l’espace et dans le temps', 'Pour attribuer plusieurs signaux à une cause commune, le système perceptif exploite leur proximité spatiale et leur proximité temporelle.', '''
<div class="csi-binding-flow"><article><b>Signal visuel</b><span>où ? · quand ?</span></article><i>+</i><article><b>Signal auditif</b><span>où ? · quand ?</span></article><em>→</em><article class="focus"><b>Cause commune ?</b><span>cohérence spatiale + tolérance temporelle</span></article></div><div class="callout"><strong>Synchronie intersensorielle :</strong> une petite asynchronie peut encore être perçue comme un événement unique - c’est le principe de la TBW.</div>''')
t7_en = block('Theoretical framework', 'Space × time', 'The same event must be located in space and time', 'To assign several signals to a common cause, perception uses their spatial and temporal proximity.', '''
<div class="csi-binding-flow"><article><b>Visual signal</b><span>where? · when?</span></article><i>+</i><article><b>Auditory signal</b><span>where? · when?</span></article><em>→</em><article class="focus"><b>Common cause?</b><span>spatial coherence + temporal tolerance</span></article></div><div class="callout"><strong>Cross-sensory synchrony:</strong> a small asynchrony can still be perceived as one event - this is the principle of the TBW.</div>''')
t7 = rewrite(7, t7_fr, t7_en, chapter='Cadre théorique', study='', appendix=False, part='Cadre théorique')

va1_fr = block('Cadre théorique', 'Vision - audition', 'Vision et audition - des profils complémentaires', 'Les deux modalités traitent espace et temps, mais leur efficacité relative et leurs interférences ne sont pas symétriques.', '''
<div class="csi-va-compare"><article class="vision"><span>VISION</span><h3>Espace très explicite</h3><p>Position · profondeur · mouvement</p><small>Le traitement spatial constitue un point fort relatif.</small></article><div class="va-mid"><b>≠</b><span>profils spatio-temporels</span></div><article class="audition"><span>AUDITION</span><h3>Temps très explicite</h3><p>Onsets · ordre · rythme</p><small>La précision temporelle constitue un point fort relatif.</small></article></div><div class="callout"><strong>Occelli et al. (2023) :</strong> l’opposition « sight for space / sound for time » est utile comme tendance relative, pas comme séparation absolue.</div>''')
va1_en = block('Theoretical framework', 'Vision - audition', 'Vision and audition - complementary profiles', 'Both modalities process space and time, but their relative efficiency and interference patterns are not symmetric.', '''
<div class="csi-va-compare"><article class="vision"><span>VISION</span><h3>Highly explicit space</h3><p>Position · depth · motion</p><small>Spatial processing is a relative strength.</small></article><div class="va-mid"><b>≠</b><span>spatiotemporal profiles</span></div><article class="audition"><span>AUDITION</span><h3>Highly explicit time</h3><p>Onsets · order · rhythm</p><small>Temporal precision is a relative strength.</small></article></div><div class="callout"><strong>Occelli et al. (2023):</strong> “sight for space / sound for time” is useful as a relative tendency, not an absolute separation.</div>''')
va1 = new_from(7, va1_fr, va1_en, chapter='Cadre théorique', part='Cadre théorique')

va2_fr = block('Cadre théorique', 'Pourquoi comparer ?', 'Deux modalités de référence pour interroger l’olfaction', 'Vision et audition offrent des paradigmes bien caractérisés pour rendre la question olfactive testable.', '''
<div class="csi-benchmark-flow"><article><b>VISION</b><span>localisation · scènes · limites spatiales</span></article><article><b>AUDITION</b><span>onsets · durée · synchronie</span></article><em>→</em><article class="focus"><b>RÉFÉRENTIEL</b><span>paradigmes + métriques</span></article><em>→</em><article class="odor"><b>OLFACTION</b><span>mêmes questions, contraintes différentes</span></article></div><div class="csi-mini-takehome">Comparer ne signifie pas supposer que l’olfaction fonctionne comme la vision ou l’audition.</div>''')
va2_en = block('Theoretical framework', 'Why compare?', 'Two reference modalities for questioning olfaction', 'Vision and audition provide well-characterized paradigms that make the olfactory question testable.', '''
<div class="csi-benchmark-flow"><article><b>VISION</b><span>localization · scenes · spatial boundaries</span></article><article><b>AUDITION</b><span>onsets · duration · synchrony</span></article><em>→</em><article class="focus"><b>BENCHMARK</b><span>paradigms + metrics</span></article><em>→</em><article class="odor"><b>OLFACTION</b><span>same questions, different constraints</span></article></div><div class="csi-mini-takehome">Comparison does not mean assuming that olfaction works like vision or audition.</div>''')
va2 = new_from(7, va2_fr, va2_en, chapter='Cadre théorique', part='Cadre théorique')

no_fr = block('Cadre théorique', 'Le contraste olfactif', '« No space, no time? » - le paradoxe de l’attention olfactive', 'Sela et Sobel (2010) décrivent une modalité dont les transformations spatiales et temporelles attirent étonnamment peu l’attention consciente.', '''
<div class="csi-no-space"><div class="provocation"><span>SPACE?</span><b>NO.</b><span>TIME?</span><b>NO.</b></div><div class="grid three"><div class="card"><div class="mono">Espace</div><h3>Une spatialisation limitée</h3><p>La localisation d’une source odorante est relativement imprécise chez l’humain.</p></div><div class="card"><div class="mono">Temps</div><h3>Un échantillonnage par le sniff</h3><p>L’entrée olfactive est rythmée par la respiration et évolue continuellement.</p></div><div class="card dark"><div class="mono">STOLF</div><h3>Le verrou à lever</h3><p>Transformer cette opposition en questions expérimentales mesurables.</p></div></div></div><div class="callout"><strong>Point de départ :</strong> « No space, no time? » est un slogan volontairement radical, pas une conclusion littérale.</div>''')
no_en = block('Theoretical framework', 'The olfactory contrast', '“No space, no time?” - the olfactory-attention paradox', 'Sela and Sobel (2010) describe a modality whose spatial and temporal transformations attract surprisingly little conscious attention.', '''
<div class="csi-no-space"><div class="provocation"><span>SPACE?</span><b>NO.</b><span>TIME?</span><b>NO.</b></div><div class="grid three"><div class="card"><div class="mono">Space</div><h3>Limited spatialization</h3><p>Human localization of an odor source is relatively imprecise.</p></div><div class="card"><div class="mono">Time</div><h3>Sampling through sniffing</h3><p>Olfactory input is paced by respiration and changes continuously.</p></div><div class="card dark"><div class="mono">STOLF</div><h3>The lock to open</h3><p>Turn this opposition into measurable experimental questions.</p></div></div></div><div class="callout"><strong>Starting point:</strong> “No space, no time?” is deliberately radical wording, not a literal conclusion.</div>''')
no_slide = rewrite(8, no_fr, no_en, chapter='Cadre théorique', study='', appendix=False, part='Cadre théorique')

less_fr = block('Cadre théorique', 'Nuancer le slogan', 'Less space, less time', 'L’espace et le temps ne sont pas absents de l’olfaction : ils sont moins directement structurés et moins spontanément accessibles à la conscience.', '''
<div class="csi-less-grid"><article><b>Le monde odorant change</b><p>Concentrations, gradients et proximité à la source varient dans l’espace.</p></article><article><b>Le signal change dans le temps</b><p>Le sniff impose une structure rythmique et l’information olfactive évolue.</p></article><article><b>Mais nous le suivons peu</b><p>La localisation reste médiocre et beaucoup de changements passent inaperçus.</p></article><article class="focus"><b>Change-blindness</b><p>Sela & Sobel : l’olfaction humaine se trouve dans un « constant state of change-blindness ».</p></article></div><div class="less-equation"><span>Space? No. Time? No.</span><i>→</i><strong>Less space, less time</strong></div>''')
less_en = block('Theoretical framework', 'Nuancing the slogan', 'Less space, less time', 'Space and time are not absent from olfaction: they are less directly structured and less spontaneously accessible to awareness.', '''
<div class="csi-less-grid"><article><b>The odor world changes</b><p>Concentrations, gradients and distance to the source vary in space.</p></article><article><b>The signal changes in time</b><p>Sniffing creates rhythmic structure and olfactory information evolves.</p></article><article><b>Yet we track it poorly</b><p>Localization remains weak and many changes go unnoticed.</p></article><article class="focus"><b>Change-blindness</b><p>Sela & Sobel describe human olfaction as a “constant state of change-blindness”.</p></article></div><div class="less-equation"><span>Space? No. Time? No.</span><i>→</i><strong>Less space, less time</strong></div>''')
less_slide = new_from(8, less_fr, less_en, chapter='Cadre théorique', part='Cadre théorique')

axis2t_fr = block('Cadre théorique', 'Préparer l’axe 2', 'Une odeur peut déjà modifier d’autres traitements perceptifs', 'La littérature établit une plausibilité intermodale, sans démontrer à l’avance les effets spatio-temporels précis recherchés dans la thèse.', '''
<div class="csi-axis2-evidence"><article><span>VISION</span><h3>Voir ce qui est peu saillant</h3><p>Des odeurs peuvent faciliter la catégorisation visuelle lorsque l’information visuelle est difficile à extraire.</p><small>Rekow et al., 2022</small></article><article><span>AUDITION / TEMPO</span><h3>Modifier une préférence temporelle</h3><p>Des odeurs ambiantes relaxantes ou stimulantes modulent les préférences pour le tempo musical.</p><small>Baccarani & Brochard, 2024</small></article><article class="focus"><span>QUESTION</span><h3>Et l’espace-temps perceptif ?</h3><p>L’axe 2 teste de façon ciblée si l’olfaction modifie certains traitements spatio-temporels visuels ou auditifs.</p></article></div>''')
axis2t_en = block('Theoretical framework', 'Preparing Axis 2', 'Odors can already influence other perceptual processes', 'The literature establishes crossmodal plausibility without pre-demonstrating the precise spatiotemporal effects targeted by the thesis.', '''
<div class="csi-axis2-evidence"><article><span>VISION</span><h3>Seeing weak information</h3><p>Odors can facilitate visual categorization when visual information is difficult to extract.</p><small>Rekow et al., 2022</small></article><article><span>AUDITION / TEMPO</span><h3>Changing a temporal preference</h3><p>Relaxing or stimulating ambient odors modulate preferences for musical tempo.</p><small>Baccarani & Brochard, 2024</small></article><article class="focus"><span>QUESTION</span><h3>What about perceptual space-time?</h3><p>Axis 2 directly tests whether olfaction changes visual or auditory spatiotemporal processing.</p></article></div>''')
axis2_theory = new_from(12, axis2t_fr, axis2t_en, chapter='Cadre théorique', part='Cadre théorique')

axes9_fr = block('Cadre théorique', 'Question scientifique', 'Deux axes', 'La lacune olfactive conduit à deux questions complémentaires.', f'''
<div class="csi-axis-pair"><article class="axis1"><span>AXE 1</span><h3>{AXIS1_FR}</h3><p>Caractériser précisément comment les informations olfactives, visuelles et auditives s'organisent dans l'espace et dans le temps.</p></article><article class="axis2"><span>AXE 2</span><h3>{AXIS2_FR}</h3><p>Tester si l’olfaction peut modifier certains traitements spatio-temporels visuels ou auditifs.</p></article></div>''')
axes9_en = block('Theoretical framework', 'Scientific question', 'Two axes', 'The olfactory gap leads to two complementary questions.', f'''
<div class="csi-axis-pair"><article class="axis1"><span>AXIS 1</span><h3>{AXIS1_EN}</h3><p>Precisely characterize how olfactory, visual and auditory information is organized in space and time.</p></article><article class="axis2"><span>AXIS 2</span><h3>{AXIS2_EN}</h3><p>Test whether olfaction can modify visual or auditory spatiotemporal processing.</p></article></div>''')
axes9 = rewrite(9, axes9_fr, axes9_en, chapter='Cadre théorique', study='', appendix=False, part='Cadre théorique')

# ---------------------------------------------------------------------------
# Programme / architecture
# ---------------------------------------------------------------------------
programme_div = divider(14, 'Programme de thèse', 'PhD programme', 2, 'Cadre théorique')

axes15_fr = block('Programme de thèse', 'Organisation canonique', 'Deux axes, quatre couples de projets', 'Les récapitulatifs regroupent les projets par proximité conceptuelle ; l’arbre suivant montrera leur filiation scientifique.', f'''
<div class="csi-program-pairs"><section class="axis1"><header><b>AXE 1</b><span>{AXIS1_FR}</span></header><div><article><strong>TWIXAV + TWIXOLF</strong><small>fenêtres temporelles</small></article><article><strong>SOFT + SOLAR</strong><small>limites élémentaires et espace</small></article></div></section><section class="axis2"><header><b>AXE 2</b><span>{AXIS2_FR}</span></header><div><article><strong>VIBEX + OASIS</strong><small>scènes visuelles puis olfaction</small></article><article><strong>BRAUD + BRAUDOLF</strong><small>extension vers l’audition</small></article></div></section></div>''')
axes15_en = block('PhD programme', 'Canonical organization', 'Two axes, four project pairs', 'Summary slides group projects by conceptual proximity; the next tree shows scientific filiation.', f'''
<div class="csi-program-pairs"><section class="axis1"><header><b>AXIS 1</b><span>{AXIS1_EN}</span></header><div><article><strong>TWIXAV + TWIXOLF</strong><small>temporal windows</small></article><article><strong>SOFT + SOLAR</strong><small>elementary limits and space</small></article></div></section><section class="axis2"><header><b>AXIS 2</b><span>{AXIS2_EN}</span></header><div><article><strong>VIBEX + OASIS</strong><small>visual scenes then olfaction</small></article><article><strong>BRAUD + BRAUDOLF</strong><small>extension to audition</small></article></div></section></div>''')
axes15 = rewrite(15, axes15_fr, axes15_en, chapter='Programme de thèse', study='', appendix=False, part='Cadre théorique')

tree16_fr = block('Programme de thèse', 'Filiation scientifique', 'Comment les études s’engendrent', 'Deux branches, une progression temporelle et un statut clair entre études noyaux et extensions conditionnelles.', f'''
<div class="csi-genealogy"><section class="axis1"><header><b>AXE 1</b><span>{AXIS1_FR}</span></header><div class="gene-chain"><article data-year="Année 1" data-study="TWIXAV"><strong>TWIXAV</strong><small>référence audiovisuelle</small></article><i>↓</i><article data-year="Année 2" data-study="SOFT"><strong>SOFT</strong><small>limites de durée</small></article><i>↓</i><article data-year="Année 3" data-study="TWIXOLF"><strong>TWIXOLF</strong><small>transposition olfactive</small></article><i>↓</i><article class="optional" data-year="si temps" data-study="SOLAR"><strong>SOLAR</strong><small>optionnel</small></article></div></section><section class="axis2"><header><b>AXE 2</b><span>{AXIS2_FR}</span></header><div class="gene-chain"><article data-year="Année 1" data-study="VIBEX"><strong>VIBEX</strong><small>référence visuelle</small></article><i>↓</i><article data-year="Année 2" data-study="OASIS"><strong>OASIS</strong><small>influence olfactive</small></article><div class="gene-branch"><article class="optional" data-year="si temps" data-study="BRAUD"><strong>BRAUD</strong></article><i>↓</i><article class="optional" data-year="si temps" data-study="BRAUDOLF"><strong>BRAUDOLF</strong></article></div></div></section></div>''')
tree16_en = block('PhD programme', 'Scientific filiation', 'How the studies generate one another', 'Two branches, a temporal progression and a clear distinction between core and conditional studies.', f'''
<div class="csi-genealogy"><section class="axis1"><header><b>AXIS 1</b><span>{AXIS1_EN}</span></header><div class="gene-chain"><article data-year="Year 1" data-study="TWIXAV"><strong>TWIXAV</strong><small>audiovisual benchmark</small></article><i>↓</i><article data-year="Year 2" data-study="SOFT"><strong>SOFT</strong><small>duration limits</small></article><i>↓</i><article data-year="Year 3" data-study="TWIXOLF"><strong>TWIXOLF</strong><small>olfactory translation</small></article><i>↓</i><article class="optional" data-year="if time" data-study="SOLAR"><strong>SOLAR</strong><small>optional</small></article></div></section><section class="axis2"><header><b>AXIS 2</b><span>{AXIS2_EN}</span></header><div class="gene-chain"><article data-year="Year 1" data-study="VIBEX"><strong>VIBEX</strong><small>visual benchmark</small></article><i>↓</i><article data-year="Year 2" data-study="OASIS"><strong>OASIS</strong><small>olfactory influence</small></article><div class="gene-branch"><article class="optional" data-year="if time" data-study="BRAUD"><strong>BRAUD</strong></article><i>↓</i><article class="optional" data-year="if time" data-study="BRAUDOLF"><strong>BRAUDOLF</strong></article></div></div></section></div>''')
tree16 = rewrite(16, tree16_fr, tree16_en, chapter='Programme de thèse', study='', appendix=False, part='Cadre théorique')

# ---------------------------------------------------------------------------
# Year 1
# ---------------------------------------------------------------------------
y1_div = divider(17, 'Année 1', 'Year 1', 3, 'Année 1')

y1sum_fr = block('Année 1', 'Bilan 2025-2026', 'Deux références expérimentales établies', 'La première année a surtout servi à construire les deux bases nécessaires au programme.', '''
<div class="csi-year-foundations"><article data-study="TWIXAV"><span>TEMPS</span><h3>TWIXAV</h3><p>Référence audiovisuelle pour la liaison temporelle.</p></article><article data-study="VIBEX"><span>ESPACE</span><h3>VIBEX</h3><p>Référence visuelle pour la représentation des limites d’une scène.</p></article><article class="side"><span>ANNEXE</span><h3>FLUXOLF</h3><p>Projet parallèle musique-odeur.</p></article></div>''')
y1sum_en = block('Year 1', '2025-2026 review', 'Two experimental references established', 'The first year primarily built the two foundations required by the programme.', '''
<div class="csi-year-foundations"><article data-study="TWIXAV"><span>TIME</span><h3>TWIXAV</h3><p>Audiovisual benchmark for temporal binding.</p></article><article data-study="VIBEX"><span>SPACE</span><h3>VIBEX</h3><p>Visual benchmark for scene-boundary representation.</p></article><article class="side"><span>SIDE PROJECT</span><h3>FLUXOLF</h3><p>Parallel music-odor project.</p></article></div>''')
y1sum = rewrite(18, y1sum_fr, y1sum_en, chapter='Année 1', study='', appendix=False, part='Année 1')

twintro_fr = block('Études de l’année 1', 'TWIXAV - Introduction', 'TWIXAV - construire le référentiel audiovisuel', 'Avant de tester l’olfaction, il faut disposer d’un benchmark temporel dans deux modalités dont la synchronie est bien caractérisée.', '''
<div class="csi-benchmark-study"><article class="source"><span>AUDIO + VISION</span><h3>TWIXAV</h3><p>Jugement de simultanéité à différents SOA.</p></article><em>→</em><article class="focus"><span>RÉFÉRENTIEL</span><h3>Temporal Binding Window</h3><p>Quelle asynchronie reste compatible avec « le même moment » ?</p></article><em>→</em><article class="future"><span>CONTINUITÉ</span><h3>TWIXOLF</h3><p>Transposer ensuite le raisonnement à l’olfaction.</p></article></div><div class="callout"><strong>À ce stade :</strong> TWIXAV sert d’abord de référence audiovisuelle. La motivation vers SOFT vient seulement après les résultats.</div>''')
twintro_en = block('Year 1 studies', 'TWIXAV - Introduction', 'TWIXAV - building the audiovisual benchmark', 'Before testing olfaction, a temporal benchmark is needed in two modalities whose synchrony is well characterized.', '''
<div class="csi-benchmark-study"><article class="source"><span>AUDIO + VISION</span><h3>TWIXAV</h3><p>Synchrony judgments across SOAs.</p></article><em>→</em><article class="focus"><span>BENCHMARK</span><h3>Temporal Binding Window</h3><p>How much asynchrony remains compatible with “the same moment”?</p></article><em>→</em><article class="future"><span>CONTINUITY</span><h3>TWIXOLF</h3><p>Then translate the reasoning to olfaction.</p></article></div><div class="callout"><strong>At this stage:</strong> TWIXAV first serves as an audiovisual benchmark. The motivation for SOFT comes only after the results.</div>''')
twintro = rewrite(19, twintro_fr, twintro_en, chapter='Année 1', study='TWIXAV', appendix=False, part='Année 1')

twmethod_fr = block('Études de l’année 1', 'TWIXAV - Méthode', 'TWIXAV - comment mesurer la TBW ?', 'Un paradigme simple : décaler un événement visuel et un événement auditif, puis demander s’ils sont simultanés.', '''
<div class="csi-method-simple"><article class="primary"><span>QUESTION</span><h3>Simultanés ?</h3><p>Réponse binaire à chaque essai.</p></article><article><span>VARIABLE</span><h3>SOA</h3><p>Décalage temporel entre vision et audition.</p></article><article><span>PARAMÈTRE</span><h3>Durée</h3><p>50 · 150 · 250 ms.</p></article><article><span>SORTIE</span><h3>TBW</h3><p>Largeur, PSS et asymétrie.</p></article></div>''' + resources('TWIXAV', 'PsychoPy · écran · système audio', poster=True, m1='Alicia Emorine', english=False))
twmethod_en = block('Year 1 studies', 'TWIXAV - Method', 'TWIXAV - how to measure the TBW?', 'A simple paradigm: offset a visual and an auditory event, then ask whether they are simultaneous.', '''
<div class="csi-method-simple"><article class="primary"><span>QUESTION</span><h3>Simultaneous?</h3><p>Binary response on every trial.</p></article><article><span>VARIABLE</span><h3>SOA</h3><p>Temporal offset between vision and audition.</p></article><article><span>PARAMETER</span><h3>Duration</h3><p>50 · 150 · 250 ms.</p></article><article><span>OUTPUT</span><h3>TBW</h3><p>Width, PSS and asymmetry.</p></article></div>''' + resources('TWIXAV', 'PsychoPy · display · audio system', poster=True, m1='Alicia Emorine', english=True))
twmethod = rewrite(20, twmethod_fr, twmethod_en, chapter='Année 1', study='TWIXAV', appendix=False, part='Année 1')

twres_fr = block('Études de l’année 1', 'TWIXAV - Résultats', 'TWIXAV - la Temporal Binding Window dépend de la durée', 'La probabilité de simultanéité dessine une TBW, et cette fenêtre se resserre lorsque la durée des stimuli augmente.', '''
<div class="csi-result-dual"><figure><img src="assets/results/twixav_empirical_curves.svg" alt="Probabilité de réponse simultané selon le SOA et la durée"><figcaption>Courbes empiriques de simultanéité.</figcaption></figure><figure><img src="assets/results/twixav_tbw_width.svg" alt="Largeur de la TBW selon la durée"><figcaption>Largeur moyenne de la TBW.</figcaption></figure></div><div class="csi-result-facts"><div class="result-meta-row"><div class="m1-owner"><span>Mémoire M1</span><strong>Alicia Emorine</strong></div><div class="m1-owner result-n"><strong>n = 19</strong></div></div><article><b>SOA</b><span>p &lt; .001</span></article><article><b>Durée</b><span>p &lt; .001</span></article><article><b>SOA × durée</b><span>p = .001</span></article><article class="key"><b>660 → 594 → 558 ms</b><span>TBW : 50 → 150 → 250 ms</span></article><article><b>PSS</b><span>p = .232 - n.s.</span></article><article><b>Asymétrie</b><span>p = .991 - n.s.</span></article></div>''')
twres_en = block('Year 1 studies', 'TWIXAV - Results', 'TWIXAV - the Temporal Binding Window depends on duration', 'Synchrony probability defines a TBW, and this window narrows as stimulus duration increases.', '''
<div class="csi-result-dual"><figure><img src="assets/results/twixav_empirical_curves.svg" alt="Synchrony responses by SOA and duration"><figcaption>Empirical synchrony curves.</figcaption></figure><figure><img src="assets/results/twixav_tbw_width.svg" alt="TBW width by duration"><figcaption>Mean TBW width.</figcaption></figure></div><div class="csi-result-facts"><div class="result-meta-row"><div class="m1-owner"><span>Master's thesis</span><strong>Alicia Emorine</strong></div><div class="m1-owner result-n"><strong>n = 19</strong></div></div><article><b>SOA</b><span>p &lt; .001</span></article><article><b>Duration</b><span>p &lt; .001</span></article><article><b>SOA × duration</b><span>p = .001</span></article><article class="key"><b>660 → 594 → 558 ms</b><span>TBW: 50 → 150 → 250 ms</span></article><article><b>PSS</b><span>p = .232 - n.s.</span></article><article><b>Asymmetry</b><span>p = .991 - n.s.</span></article></div>''')
twres = rewrite(21, twres_fr, twres_en, chapter='Année 1', study='TWIXAV', appendix=False, part='Année 1')

twtake_fr = block('Études de l’année 1', 'TWIXAV - À retenir', 'Ce que TWIXAV fixe', 'Trois résultats suffisent pour fermer le benchmark audiovisuel avant de poser une nouvelle question.', '''
<div class="grid three"><div class="card"><div class="mono">1</div><h3>Une TBW mesurable</h3><p>Le jugement de simultanéité fournit une fenêtre temporelle robuste.</p></div><div class="card"><div class="mono">2</div><h3>La durée compte</h3><p>La TBW se resserre lorsque les stimuli sont plus longs.</p></div><div class="card dark"><div class="mono">3</div><h3>PSS et asymétrie stables</h3><p>La durée modifie surtout la largeur de la fenêtre.</p></div></div>''')
twtake_en = block('Year 1 studies', 'TWIXAV - Take-home', 'What TWIXAV establishes', 'Three results are enough to close the audiovisual benchmark before asking a new question.', '''
<div class="grid three"><div class="card"><div class="mono">1</div><h3>A measurable TBW</h3><p>Synchrony judgments provide a robust temporal window.</p></div><div class="card"><div class="mono">2</div><h3>Duration matters</h3><p>The TBW narrows for longer stimuli.</p></div><div class="card dark"><div class="mono">3</div><h3>Stable PSS and asymmetry</h3><p>Duration mainly changes window width.</p></div></div>''')
twtake = rewrite(24, twtake_fr, twtake_en, chapter='Année 1', study='TWIXAV', appendix=False, part='Année 1')

twsoft_fr = block('Études de l’année 1', 'TWIXAV → SOFT', 'Du résultat TWIXAV à une nouvelle question', 'Le benchmark audiovisuel révèle que la durée du stimulus modifie la largeur de la fenêtre temporelle.', '''
<div class="csi-transition-chain"><article data-study="TWIXAV"><span>TWIXAV</span><strong>Résultat</strong><small>la TBW dépend de la durée</small></article><i>↓</i><article class="question"><span>NOUVELLE QUESTION</span><strong>Les modalités ont-elles les mêmes limites de durée ?</strong></article><i>↓</i><article data-study="SOFT"><span>SOFT</span><strong>Onset · offset · durée</strong><small>mesurer les bornes propres à chaque modalité</small></article></div>''')
twsoft_en = block('Year 1 studies', 'TWIXAV → SOFT', 'From the TWIXAV result to a new question', 'The audiovisual benchmark shows that stimulus duration changes the width of the temporal window.', '''
<div class="csi-transition-chain"><article data-study="TWIXAV"><span>TWIXAV</span><strong>Result</strong><small>TBW depends on duration</small></article><i>↓</i><article class="question"><span>NEW QUESTION</span><strong>Do modalities have the same duration limits?</strong></article><i>↓</i><article data-study="SOFT"><span>SOFT</span><strong>Onset · offset · duration</strong><small>measure modality-specific boundaries</small></article></div>''')
twsoft = rewrite(23, twsoft_fr, twsoft_en, chapter='Année 1', study='TWIXAV', appendix=False, part='Année 1')

vintro_fr = block('Études de l’année 1', 'VIBEX - Introduction', 'VIBEX - établir la référence spatiale visuelle', 'VIBEX caractérise la Boundary Extension et teste un paramètre qui a une double fonction : la taille de l’image.', '''
<div class="csi-vibex-size"><article><span>PHÉNOMÈNE</span><h3>Boundary Extension</h3><p>La mémoire d’une scène peut dépasser ses limites réellement vues.</p></article><article class="split"><span>TAILLE DE L’IMAGE</span><div><b>Méthodologique</b><p>Choisir un paramètre optimal et discriminant.</p></div><div><b>Théorique</b><p>Tester si l’amplitude du phénomène dépend de l’échelle du stimulus.</p></div></article></div><div class="callout"><strong>Message :</strong> l’effet de taille n’est pas un simple réglage technique.</div>''')
vintro_en = block('Year 1 studies', 'VIBEX - Introduction', 'VIBEX - establishing the visual spatial benchmark', 'VIBEX characterizes Boundary Extension and tests a parameter with two roles: image size.', '''
<div class="csi-vibex-size"><article><span>PHENOMENON</span><h3>Boundary Extension</h3><p>Memory for a scene can extend beyond its actually viewed boundaries.</p></article><article class="split"><span>IMAGE SIZE</span><div><b>Methodological</b><p>Select an optimal and discriminative parameter.</p></div><div><b>Theoretical</b><p>Test whether phenomenon magnitude depends on stimulus scale.</p></div></article></div><div class="callout"><strong>Message:</strong> image size is not merely a technical setting.</div>''')
vintro = rewrite(26, vintro_fr, vintro_en, chapter='Année 1', study='VIBEX', appendix=False, part='Année 1')

vmethod_fr = block('Études de l’année 1', 'VIBEX - Méthode', 'VIBEX - quatre conditions à comprendre', 'La manipulation repose sur le cadrage de la première et de la seconde image. La séquence peut être déclenchée manuellement pendant la présentation.', '''
<div class="csi-vibex-conditions"><article><b>LL</b><span>large → large</span></article><article><b>SS</b><span>serré → serré</span></article><article class="pair-a"><b>SL</b><span>serré → large</span></article><article class="pair-b"><b>LS</b><span>large → serré</span></article></div>
<div class="vibex-manual-demo" data-vibex-state="0"><div class="vibex-demo-stage"><div class="vibex-demo-ready"><b>Démo manuelle</b><span>Image 1 → masque → image 2</span></div><img alt="Stimulus VIBEX" hidden></div><div class="vibex-demo-controls"><button type="button" data-vibex-next>Suivant</button><button type="button" data-vibex-reset>Recommencer</button><span data-vibex-label>Prêt</span></div></div>''' + resources('VIBEX', 'PsychoPy · écran', poster=True, m1='Olivia Hiridjee', english=False))
vmethod_en = block('Year 1 studies', 'VIBEX - Method', 'VIBEX - four conditions to understand', 'The manipulation depends on the framing of the first and second images. The sequence can be advanced manually during the presentation.', '''
<div class="csi-vibex-conditions"><article><b>LL</b><span>large → large</span></article><article><b>SS</b><span>close → close</span></article><article class="pair-a"><b>SL</b><span>close → large</span></article><article class="pair-b"><b>LS</b><span>large → close</span></article></div>
<div class="vibex-manual-demo" data-vibex-state="0"><div class="vibex-demo-stage"><div class="vibex-demo-ready"><b>Manual demo</b><span>Image 1 → mask → Image 2</span></div><img alt="VIBEX stimulus" hidden></div><div class="vibex-demo-controls"><button type="button" data-vibex-next>Next</button><button type="button" data-vibex-reset>Restart</button><span data-vibex-label>Ready</span></div></div>''' + resources('VIBEX', 'PsychoPy · display', poster=True, m1='Olivia Hiridjee', english=True))
vmethod = rewrite(27, vmethod_fr, vmethod_en, chapter='Année 1', study='VIBEX', appendix=False, part='Année 1')

vres1_fr = block('Études de l’année 1', 'VIBEX - Résultats', 'VIBEX - deux paires de conditions, une asymétrie nette', 'LL et SS restent proches ; SL et LS se séparent fortement, signature attendue du phénomène de Boundary Extension.', '''
<div class="results-expanded"><div class="results-copy"><div class="result-meta-row"><div class="m1-owner"><span>Mémoire M1</span><strong>Olivia Hiridjee</strong></div><div class="m1-owner result-n"><strong>n = 24</strong></div></div><div class="m1-stat-grid"><div><b>LL ↔ SS</b><span>p = .121 - n.s.</span></div><div><b>SL &gt; LS</b><span>p &lt; .001</span></div><div><b>Condition</b><span>p &lt; .001</span></div></div></div><figure class="result-figure-large"><img src="assets/results/vibex_conditions.svg" alt="VIBEX : conditions LL, SS, SL et LS par taille avec intervalles de confiance"><figcaption>Les paires LL-SS et SL-LS sont regroupées visuellement. IC95 issus des données par taille.</figcaption></figure></div>''')
vres1_en = block('Year 1 studies', 'VIBEX - Results', 'VIBEX - two condition pairs, one clear asymmetry', 'LL and SS remain close; SL and LS strongly diverge, the expected signature of Boundary Extension.', '''
<div class="results-expanded"><div class="results-copy"><div class="result-meta-row"><div class="m1-owner"><span>Master's thesis</span><strong>Olivia Hiridjee</strong></div><div class="m1-owner result-n"><strong>n = 24</strong></div></div><div class="m1-stat-grid"><div><b>LL ↔ SS</b><span>p = .121 - n.s.</span></div><div><b>SL &gt; LS</b><span>p &lt; .001</span></div><div><b>Condition</b><span>p &lt; .001</span></div></div></div><figure class="result-figure-large"><img src="assets/results/vibex_conditions.svg" alt="VIBEX conditions LL SS SL LS by size with confidence intervals"><figcaption>LL-SS and SL-LS are visually paired. 95% CIs from the size-specific data.</figcaption></figure></div>''')
vres1 = rewrite(28, vres1_fr, vres1_en, chapter='Année 1', study='VIBEX', appendix=False, part='Année 1')

vres2_fr = block('Études de l’année 1', 'VIBEX - Résultats', 'VIBEX - la taille module l’amplitude du phénomène', 'L’effet global de taille n’est pas significatif, mais la relation entre condition et taille l’est.', '''
<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>Taille</b><span>p = .601 - n.s.</span></div><div><b>Condition × taille</b><span>p &lt; .001</span></div><div><b>SL-LS</b><span>30,6 · 25,3 · 14,8 %</span></div><div><b>SL petite vs grande</b><span>p = .045</span></div></div><div class="callout"><strong>Double fonction :</strong> sélectionner le paramètre le plus informatif et documenter un effet théorique de l’échelle du stimulus.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_size_interaction.svg" alt="VIBEX : réponses identique selon condition, présentées en facettes par taille"><figcaption>Petite, moyenne et grande : même ordre des conditions, IC95.</figcaption></figure></div>''')
vres2_en = block('Year 1 studies', 'VIBEX - Results', 'VIBEX - image size modulates phenomenon magnitude', 'The main effect of size is not significant, but the condition-by-size relationship is.', '''
<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>Size</b><span>p = .601 - n.s.</span></div><div><b>Condition × size</b><span>p &lt; .001</span></div><div><b>SL-LS</b><span>30.6 · 25.3 · 14.8%</span></div><div><b>SL small vs large</b><span>p = .045</span></div></div><div class="callout"><strong>Dual role:</strong> select the most informative parameter and document a theoretical effect of stimulus scale.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_size_interaction.svg" alt="VIBEX same responses by condition faceted by image size"><figcaption>Small, medium and large: same condition order, 95% CIs.</figcaption></figure></div>''')
vres2 = rewrite(29, vres2_fr, vres2_en, chapter='Année 1', study='VIBEX', appendix=False, part='Année 1')

vres3_fr = block('Études de l’année 1', 'VIBEX - Résultats', 'VIBEX - les temps de réaction convergent', 'La condition SL ralentit davantage la réponse que LS, surtout pour les petites images.', '''
<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>Condition</b><span>p = .031</span></div><div><b>Condition × taille</b><span>p = .005</span></div><div><b>SL-LS - petite</b><span>+53 ms · p = .024</span></div><div><b>Moyenne / grande</b><span>+37 / +14 ms · n.s.</span></div></div><div class="callout"><strong>Convergence :</strong> les RT reproduisent la direction observée dans les jugements, sans ajouter d’intervalles par taille qui ne sont pas disponibles dans l’asset source.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_rt_interaction.svg" alt="VIBEX : temps de réaction par condition en facettes de taille"><figcaption>Trois facettes comparables - axe Y en millisecondes.</figcaption></figure></div>''')
vres3_en = block('Year 1 studies', 'VIBEX - Results', 'VIBEX - reaction times converge', 'The SL condition slows responses more than LS, especially for small images.', '''
<div class="results-expanded"><div class="results-copy"><div class="m1-stat-grid"><div><b>Condition</b><span>p = .031</span></div><div><b>Condition × size</b><span>p = .005</span></div><div><b>SL-LS - small</b><span>+53 ms · p = .024</span></div><div><b>Medium / large</b><span>+37 / +14 ms · n.s.</span></div></div><div class="callout"><strong>Convergence:</strong> RTs reproduce the direction seen in judgments, without fabricating size-specific intervals absent from the source asset.</div></div><figure class="result-figure-large"><img src="assets/results/vibex_rt_interaction.svg" alt="VIBEX reaction times by condition faceted by size"><figcaption>Three comparable facets - Y axis in milliseconds.</figcaption></figure></div>''')
vres3 = rewrite(30, vres3_fr, vres3_en, chapter='Année 1', study='VIBEX', appendix=False, part='Année 1')

vtake_fr = block('Études de l’année 1', 'VIBEX - À retenir', 'Ce que VIBEX apporte à la manipulation olfactive', 'VIBEX n’est pas un simple prétest : il fixe ce qui doit être conservé lorsque l’olfaction sera introduite.', '''
<div class="csi-transfer-grid"><article><b>Conditions</b><span>SL-LS discrimine clairement le phénomène.</span></article><article><b>Taille</b><span>Le paramètre module l’amplitude et guide le choix expérimental.</span></article><article><b>Contrôle</b><span>Cadrage standardisé et mouvement oculaire maîtrisé.</span></article><article class="focus"><b>Transfert</b><span>Une base visuelle stable pour isoler ensuite l’influence olfactive.</span></article></div>''')
vtake_en = block('Year 1 studies', 'VIBEX - Take-home', 'What VIBEX contributes to the olfactory manipulation', 'VIBEX is not merely a pre-test: it fixes what must be preserved when olfaction is introduced.', '''
<div class="csi-transfer-grid"><article><b>Conditions</b><span>SL-LS clearly discriminates the phenomenon.</span></article><article><b>Size</b><span>The parameter modulates magnitude and guides experimental choice.</span></article><article><b>Control</b><span>Standardized framing and controlled eye movement.</span></article><article class="focus"><b>Transfer</b><span>A stable visual basis for isolating olfactory influence next.</span></article></div>''')
vtake = rewrite(31, vtake_fr, vtake_en, chapter='Année 1', study='VIBEX', appendix=False, part='Année 1')

y1diff_fr = block('Année 1', 'Retour d’expérience', 'Année 1 - difficultés techniques', 'Les deux paradigmes ont surtout demandé de transformer des timings programmés en timings réellement contrôlés.', '''
<div class="csi-difficulty-summary"><section><span>RENCONTRÉ</span><p>Refresh écran · SOA audiovisuel · tailles et cadrages</p></section><section><span>SOLUTIONS</span><p>Frames mesurées · prétests / logs · stimuli standardisés</p></section><section><span>RESTE À SÉCURISER</span><p>Portabilité du dispositif · contrôle final avant réplication</p></section></div>''')
y1diff_en = block('Year 1', 'Technical feedback', 'Year 1 - technical difficulties', 'Both paradigms mainly required turning programmed timing into actually controlled timing.', '''
<div class="csi-difficulty-summary"><section><span>ENCOUNTERED</span><p>Display refresh · audiovisual SOA · sizes and crops</p></section><section><span>SOLUTIONS</span><p>Measured frames · pre-tests / logs · standardized stimuli</p></section><section><span>STILL TO SECURE</span><p>Setup portability · final control before replication</p></section></div>''')
y1diff = new_from(25, y1diff_fr, y1diff_en, chapter='Année 1', part='Année 1')

# FLUXOLF: retain the actual project content but remove the visible equipment list.
flux = copy.deepcopy(old[33])
flux['_csi_part'] = 'Année 1'
flux['chapter'] = 'Année 1'
for key, english in [('_fr', False), ('_en', True)]:
    h = flux.get(key, {})
    c = h.get('content', '')
    c = re.sub(r'(<button class="[^"]*apparatus-open[^"]*"[^>]*><b>[^<]*</b><span>).*?(</span></button>)', r'\1' + ('View equipment' if english else "Voir l'appareillage") + r'\2', c, flags=re.S)
    h['content'] = c
flux.update(flux.get('_fr', {}))

# Activities Year 1: keep factual volumes, add timeline later.
y1act = copy.deepcopy(old[34]); y1act['_csi_part'] = 'Année 1'; y1act['chapter'] = 'Année 1'

jdd_fr = block('Année 1', 'Communication scientifique', 'JDD 2026 - STOLF en une question', 'Une première mise à l’épreuve publique du fil narratif de la thèse.', '''
<div class="csi-jdd-simple"><div class="jdd-question">« Y a-t-il un espace-temps pour les odeurs ? »</div><div class="jdd-points"><article><b>2 axes</b><span>rendre le programme lisible</span></article><article><b>1 architecture</b><span>montrer l’enchaînement des études</span></article><article class="award"><b>Prix de l’originalité</b><span>Journée des Doctorants 2026</span></article></div></div>''')
jdd_en = block('Year 1', 'Scientific communication', 'JDD 2026 - STOLF in one question', 'A first public test of the thesis narrative.', '''
<div class="csi-jdd-simple"><div class="jdd-question">“Is there a space-time for odors?”</div><div class="jdd-points"><article><b>2 axes</b><span>make the programme readable</span></article><article><b>1 architecture</b><span>show how studies connect</span></article><article class="award"><b>Originality prize</b><span>2026 Doctoral Day</span></article></div></div>''')
jdd = rewrite(35, jdd_fr, jdd_en, chapter='Année 1', study='', appendix=False, part='Année 1')

trans36_fr = block('Année 1', 'Transition', 'Deux références ouvrent la suite', 'À la fin de l’année 1, les deux branches disposent chacune d’un paradigme de référence.', '''
<div class="csi-two-foundations"><article data-study="TWIXAV"><span>TEMPS</span><h3>TWIXAV</h3><p>Benchmark audiovisuel acquis.</p><b>→ SOFT → TWIXOLF</b></article><article data-study="VIBEX"><span>ESPACE</span><h3>VIBEX</h3><p>Benchmark visuel acquis.</p><b>→ OASIS</b></article></div>''')
trans36_en = block('Year 1', 'Transition', 'Two benchmarks open the next stage', 'At the end of Year 1, each branch has an experimental reference paradigm.', '''
<div class="csi-two-foundations"><article data-study="TWIXAV"><span>TIME</span><h3>TWIXAV</h3><p>Audiovisual benchmark established.</p><b>→ SOFT → TWIXOLF</b></article><article data-study="VIBEX"><span>SPACE</span><h3>VIBEX</h3><p>Visual benchmark established.</p><b>→ OASIS</b></article></div>''')
trans36 = rewrite(36, trans36_fr, trans36_en, chapter='Année 1', study='', appendix=False, part='Année 1')

# ---------------------------------------------------------------------------
# Year 2
# ---------------------------------------------------------------------------
y2_div = divider(37, 'Année 2', 'Year 2', 4, 'Année 2')

axes38_fr = block('Année 2', 'Logique expérimentale', 'Deux axes, des priorités différentes', 'L’année 2 avance sur les deux branches sans confondre leur logique scientifique.', f'''
<div class="csi-program-pairs compact"><section class="axis1"><header><b>AXE 1</b><span>{AXIS1_FR}</span></header><div><article><strong>TWIXAV + TWIXOLF</strong><small>référentiel et transposition</small></article><article class="focus"><strong>SOFT + SOLAR</strong><small>SOFT prioritaire · SOLAR conditionnel</small></article></div></section><section class="axis2"><header><b>AXE 2</b><span>{AXIS2_FR}</span></header><div><article class="focus"><strong>VIBEX + OASIS</strong><small>OASIS prioritaire</small></article><article><strong>BRAUD + BRAUDOLF</strong><small>conditionnels</small></article></div></section></div>''')
axes38_en = block('Year 2', 'Experimental logic', 'Two axes, different priorities', 'Year 2 advances both branches without conflating their scientific logic.', f'''
<div class="csi-program-pairs compact"><section class="axis1"><header><b>AXIS 1</b><span>{AXIS1_EN}</span></header><div><article><strong>TWIXAV + TWIXOLF</strong><small>benchmark and translation</small></article><article class="focus"><strong>SOFT + SOLAR</strong><small>SOFT priority · SOLAR conditional</small></article></div></section><section class="axis2"><header><b>AXIS 2</b><span>{AXIS2_EN}</span></header><div><article class="focus"><strong>VIBEX + OASIS</strong><small>OASIS priority</small></article><article><strong>BRAUD + BRAUDOLF</strong><small>conditional</small></article></div></section></div>''')
axes38 = rewrite(38, axes38_fr, axes38_en, chapter='Année 2', study='', appendix=False, part='Année 2')

prio_fr = block('Année 2', 'Priorités', 'Les trois prochaines étapes', 'SOFT et OASIS constituent les priorités immédiates ; TWIXOLF reste l’étape majeure de l’axe 1 en année 3.', '''
<div class="csi-priority-road"><article data-study="SOFT"><b>1</b><h3>SOFT</h3><span>Sept. - déc. 2026</span><p>Mesurer onset, offset et durée.</p></article><article data-study="OASIS"><b>2</b><h3>OASIS</h3><span>2027</span><p>Tester l’influence olfactive sur la représentation spatiale.</p></article><article data-study="TWIXOLF"><b>3</b><h3>TWIXOLF</h3><span>Année 3</span><p>Transposer la TBW à l’olfaction.</p></article></div>''')
prio_en = block('Year 2', 'Priorities', 'The next three stages', 'SOFT and OASIS are the immediate priorities; TWIXOLF remains the major Axis 1 step in Year 3.', '''
<div class="csi-priority-road"><article data-study="SOFT"><b>1</b><h3>SOFT</h3><span>Sep. - Dec. 2026</span><p>Measure onset, offset and duration.</p></article><article data-study="OASIS"><b>2</b><h3>OASIS</h3><span>2027</span><p>Test olfactory influence on spatial representation.</p></article><article data-study="TWIXOLF"><b>3</b><h3>TWIXOLF</h3><span>Year 3</span><p>Translate the TBW to olfaction.</p></article></div>''')
prio = rewrite(39, prio_fr, prio_en, chapter='Année 2', study='', appendix=False, part='Année 2')

soft_intro_fr = block('Études de l’année 2', 'SOFT - Introduction', 'SOFT - quelles sont les limites temporelles propres à chaque modalité ?', 'SOFT naît directement du résultat TWIXAV : avant de comparer les fenêtres multisensorielles, il faut connaître la précision temporelle élémentaire de chaque sens.', '''
<div class="csi-soft-question"><article><b>AUDITION</b><span>onset · offset · durée</span></article><article><b>VISION</b><span>onset · offset · durée</span></article><article><b>OLFACTION</b><span>onset · offset · durée</span></article><em>→</em><div class="focus"><strong>Mêmes limites ?</strong><span>ou signatures temporelles propres à chaque modalité ?</span></div></div>''')
soft_intro_en = block('Year 2 studies', 'SOFT - Introduction', 'SOFT - what are the temporal limits of each modality?', 'SOFT follows directly from TWIXAV: before comparing multisensory windows, we need the elementary temporal precision of each sense.', '''
<div class="csi-soft-question"><article><b>AUDITION</b><span>onset · offset · duration</span></article><article><b>VISION</b><span>onset · offset · duration</span></article><article><b>OLFACTION</b><span>onset · offset · duration</span></article><em>→</em><div class="focus"><strong>Same limits?</strong><span>or modality-specific temporal signatures?</span></div></div>''')
soft_intro = rewrite(40, soft_intro_fr, soft_intro_en, chapter='Année 2', study='SOFT', appendix=False, part='Année 2')

soft_method_fr = block('Études de l’année 2', 'SOFT - Méthode', 'SOFT - comparer trois modalités dans la même logique', 'La variable conceptuelle est la précision avec laquelle un participant estime le début, la fin et la durée d’un événement.', '''
<div class="csi-method-simple"><article class="primary"><span>MODALITÉS</span><h3>A · V · O</h3><p>Audition, vision, olfaction.</p></article><article><span>ÉVÉNEMENT</span><h3>Onset</h3><p>Quand commence le stimulus ?</p></article><article><span>ÉVÉNEMENT</span><h3>Offset</h3><p>Quand se termine-t-il ?</p></article><article><span>ESTIMATION</span><h3>Durée</h3><p>Combien de temps a-t-il duré ?</p></article></div>''' + resources('SOFT', 'Sniff-0 · Spir-0 · BIOPAC MP160 · EEG BioSemi · PsychoPy', poster=True, english=False))
soft_method_en = block('Year 2 studies', 'SOFT - Method', 'SOFT - comparing three modalities with one logic', 'The conceptual variable is how precisely a participant estimates the beginning, end and duration of an event.', '''
<div class="csi-method-simple"><article class="primary"><span>MODALITIES</span><h3>A · V · O</h3><p>Audition, vision, olfaction.</p></article><article><span>EVENT</span><h3>Onset</h3><p>When does the stimulus begin?</p></article><article><span>EVENT</span><h3>Offset</h3><p>When does it end?</p></article><article><span>ESTIMATE</span><h3>Duration</h3><p>How long did it last?</p></article></div>''' + resources('SOFT', 'Sniff-0 · Spir-0 · BIOPAC MP160 · EEG BioSemi · PsychoPy', poster=True, english=True))
soft_method = rewrite(41, soft_method_fr, soft_method_en, chapter='Année 2', study='SOFT', appendix=False, part='Année 2')

oasis_intro_fr = block('Études de l’année 2', 'OASIS - Introduction', 'OASIS - l’odeur modifie-t-elle la représentation spatiale d’une scène ?', 'VIBEX fournit la référence visuelle ; OASIS introduit l’olfaction pour tester une influence causale sur la mémoire spatiale.', '''
<div class="csi-oasis-flow"><article data-study="VIBEX"><span>RÉFÉRENCE</span><h3>VIBEX</h3><p>Boundary Extension caractérisée.</p></article><i>+</i><article class="odor"><span>CONTEXTE</span><h3>Odeur</h3><p>présente ou contrôlée selon la condition</p></article><em>→</em><article class="focus" data-study="OASIS"><span>TEST</span><h3>OASIS</h3><p>La représentation spatiale change-t-elle ?</p></article></div>''')
oasis_intro_en = block('Year 2 studies', 'OASIS - Introduction', 'OASIS - does odor change the spatial representation of a scene?', 'VIBEX provides the visual benchmark; OASIS introduces olfaction to test a causal influence on spatial memory.', '''
<div class="csi-oasis-flow"><article data-study="VIBEX"><span>REFERENCE</span><h3>VIBEX</h3><p>Boundary Extension characterized.</p></article><i>+</i><article class="odor"><span>CONTEXT</span><h3>Odor</h3><p>present or controlled by condition</p></article><em>→</em><article class="focus" data-study="OASIS"><span>TEST</span><h3>OASIS</h3><p>Does spatial representation change?</p></article></div>''')
oasis_intro = rewrite(43, oasis_intro_fr, oasis_intro_en, chapter='Année 2', study='OASIS', appendix=False, part='Année 2')

oasis_method_fr = block('Études de l’année 2', 'OASIS - Méthode', 'OASIS - conserver le visuel, ajouter l’olfaction', 'Le cœur du paradigme VIBEX est maintenu afin que la différence interprétable vienne du contexte olfactif.', '''
<div class="csi-method-simple"><article class="primary"><span>BASE</span><h3>Scènes VIBEX</h3><p>Mêmes principes de cadrage.</p></article><article><span>VARIABLE</span><h3>Contexte olfactif</h3><p>Manipulation ajoutée au paradigme visuel.</p></article><article><span>RÉPONSE</span><h3>Identique / différent</h3><p>Même logique de jugement.</p></article><article><span>QUESTION</span><h3>Influence</h3><p>Le biais spatial est-il modifié ?</p></article></div>''' + resources('OASIS', 'Sniff-0 · Spir-0 · BIOPAC MP160 · PsychoPy', poster=True, english=False))
oasis_method_en = block('Year 2 studies', 'OASIS - Method', 'OASIS - keep the visual core, add olfaction', 'The VIBEX core is preserved so the interpretable difference comes from olfactory context.', '''
<div class="csi-method-simple"><article class="primary"><span>BASE</span><h3>VIBEX scenes</h3><p>Same framing principles.</p></article><article><span>VARIABLE</span><h3>Olfactory context</h3><p>Manipulation added to the visual paradigm.</p></article><article><span>RESPONSE</span><h3>Same / different</h3><p>Same judgment logic.</p></article><article><span>QUESTION</span><h3>Influence</h3><p>Is the spatial bias modified?</p></article></div>''' + resources('OASIS', 'Sniff-0 · Spir-0 · BIOPAC MP160 · PsychoPy', poster=True, english=True))
oasis_method = rewrite(44, oasis_method_fr, oasis_method_en, chapter='Année 2', study='OASIS', appendix=False, part='Année 2')

twixo_intro_fr = block('Études de l’année 2', 'TWIXOLF - Introduction', 'TWIXOLF - transposer la fenêtre temporelle à l’olfaction', 'TWIXOLF reprend la logique de TWIXAV après avoir caractérisé avec SOFT certaines contraintes temporelles propres aux modalités.', '''
<div class="csi-twixolf-flow"><article data-study="TWIXAV"><b>TWIXAV</b><span>benchmark TBW</span></article><i>→</i><article data-study="SOFT"><b>SOFT</b><span>bornes de durée</span></article><i>→</i><article class="focus" data-study="TWIXOLF"><b>TWIXOLF</b><span>fenêtre impliquant l’olfaction</span></article></div><div class="csi-vibex-size compact"><article class="split"><span>DURÉE</span><div><b>Méthodologique</b><p>Choisir des paramètres compatibles avec la modalité.</p></div><div><b>Théorique</b><p>Tester une dimension encore peu documentée en olfaction.</p></div></article></div>''')
twixo_intro_en = block('Year 2 studies', 'TWIXOLF - Introduction', 'TWIXOLF - translating the temporal window to olfaction', 'TWIXOLF reuses the TWIXAV logic after SOFT has characterized some modality-specific temporal constraints.', '''
<div class="csi-twixolf-flow"><article data-study="TWIXAV"><b>TWIXAV</b><span>TBW benchmark</span></article><i>→</i><article data-study="SOFT"><b>SOFT</b><span>duration boundaries</span></article><i>→</i><article class="focus" data-study="TWIXOLF"><b>TWIXOLF</b><span>window involving olfaction</span></article></div><div class="csi-vibex-size compact"><article class="split"><span>DURATION</span><div><b>Methodological</b><p>Select parameters compatible with the modality.</p></div><div><b>Theoretical</b><p>Test a dimension still poorly documented in olfaction.</p></div></article></div>''')
twixo_intro = rewrite(46, twixo_intro_fr, twixo_intro_en, chapter='Année 2', study='TWIXOLF', appendix=False, part='Année 2')

twixo_method_fr = block('Études de l’année 2', 'TWIXOLF - Méthode', 'TWIXOLF - construire un décalage temporel avec une odeur', 'La logique reste un jugement temporel multisensoriel, mais le repère olfactif doit être défini de façon reproductible.', '''
<div class="csi-method-simple"><article class="primary"><span>PARADIGME</span><h3>Simultanéité</h3><p>Olfaction + modalité de référence.</p></article><article><span>VARIABLE</span><h3>SOA</h3><p>Décalage entre les événements.</p></article><article><span>ANCRE</span><h3>Inspiration</h3><p>Repère temporel olfactif reproductible.</p></article><article><span>SORTIE</span><h3>TBW</h3><p>Fenêtre temporelle impliquant l’olfaction.</p></article></div>''' + resources('TWIXOLF', 'Sniff-0 · Spir-0 · BIOPAC MP160 · PsychoPy', poster=True, english=False))
twixo_method_en = block('Year 2 studies', 'TWIXOLF - Method', 'TWIXOLF - building a temporal offset with an odor', 'The logic remains a multisensory temporal judgment, but the olfactory reference must be defined reproducibly.', '''
<div class="csi-method-simple"><article class="primary"><span>PARADIGM</span><h3>Synchrony</h3><p>Olfaction + reference modality.</p></article><article><span>VARIABLE</span><h3>SOA</h3><p>Offset between events.</p></article><article><span>ANCHOR</span><h3>Inhalation</h3><p>Reproducible olfactory temporal reference.</p></article><article><span>OUTPUT</span><h3>TBW</h3><p>Temporal window involving olfaction.</p></article></div>''' + resources('TWIXOLF', 'Sniff-0 · Spir-0 · BIOPAC MP160 · PsychoPy', poster=True, english=True))
twixo_method = rewrite(47, twixo_method_fr, twixo_method_en, chapter='Année 2', study='TWIXOLF', appendix=False, part='Année 2')

y2diff_fr = block('Année 2', 'Développement expérimental', 'Année 2 - difficultés techniques', 'Le défi commun est la synchronisation de plusieurs systèmes autour d’un événement olfactif dépendant de la respiration.', '''
<div class="csi-difficulty-summary"><section><span>RENCONTRÉ</span><p>Systèmes multiples · onset olfactif · résiduel entre essais</p></section><section><span>SOLUTIONS</span><p>Pilotage modulaire · ancre inspiratoire · calibration / flush</p></section><section><span>RESTE À VALIDER</span><p>Latence bout-en-bout · robustesse sur session complète</p></section></div>''')
y2diff_en = block('Year 2', 'Experimental development', 'Year 2 - technical difficulties', 'The shared challenge is synchronizing several systems around an olfactory event that depends on respiration.', '''
<div class="csi-difficulty-summary"><section><span>ENCOUNTERED</span><p>Multiple systems · olfactory onset · inter-trial residual</p></section><section><span>SOLUTIONS</span><p>Modular control · inhalation anchor · calibration / flush</p></section><section><span>STILL TO VALIDATE</span><p>End-to-end latency · full-session robustness</p></section></div>''')
y2diff = new_from(42, y2diff_fr, y2diff_en, chapter='Année 2', part='Année 2')

y2act = copy.deepcopy(old[49]); y2act['_csi_part'] = 'Année 2'; y2act['chapter'] = 'Année 2'

# ---------------------------------------------------------------------------
# Dissemination and next studies
# ---------------------------------------------------------------------------
val_div_fr = block('Valorisation', '', 'Valorisation', '', '<div class="section-divider-inner"><span class="section-divider-number">PARTIE 5</span><h1>Valorisation</h1><i aria-hidden="true"></i></div>')
val_div_en = block('Dissemination', '', 'Dissemination', '', '<div class="section-divider-inner"><span class="section-divider-number">PART 5</span><h1>Dissemination</h1><i aria-hidden="true"></i></div>')
val_div = new_from(51, val_div_fr, val_div_en, chapter='Valorisation', part='Valorisation')

comms_fr = block('Valorisation', 'Communications et médiation', 'Faire circuler les résultats au fil de la thèse', 'Les rendez-vous n’ont pas tous le même statut : conférences, communications locales et médiation sont distinguées.', '''
<div class="csi-comms-timeline"><section><b>2026</b><article class="local"><strong>Nuit des Chercheurs 2026</strong><span>communication / diffusion</span></article></section><section><b>2027</b><article class="local"><strong>Forum des Jeunes Chercheurs 2027</strong></article><article class="local"><strong>Journée des Doctorants 2027</strong></article><article class="mediation"><strong>Expérimentarium 2027</strong><span>médiation scientifique</span></article><article class="conference"><strong>ECRO 2027</strong></article><article class="conference"><strong>GDR O3 2027</strong></article></section><section><b>2028</b><article class="local"><strong>Forum des Jeunes Chercheurs 2028</strong></article><article class="local"><strong>Journée des Doctorants 2028</strong></article><article class="conference conditional"><strong>ISOT 2028</strong><span>si financement</span></article></section></div><div class="csi-comms-legend"><span class="conference">Conférence</span><span class="local">Local / national</span><span class="mediation">Médiation</span><span class="conditional">Conditionnel</span></div>''')
comms_en = block('Dissemination', 'Communications and outreach', 'Circulating results throughout the PhD', 'These events do not have the same status: conferences, local communications and public engagement are distinguished.', '''
<div class="csi-comms-timeline"><section><b>2026</b><article class="local"><strong>Nuit des Chercheurs 2026</strong><span>communication / dissemination</span></article></section><section><b>2027</b><article class="local"><strong>Forum des Jeunes Chercheurs 2027</strong></article><article class="local"><strong>Journée des Doctorants 2027</strong></article><article class="mediation"><strong>Expérimentarium 2027</strong><span>public engagement</span></article><article class="conference"><strong>ECRO 2027</strong></article><article class="conference"><strong>GDR O3 2027</strong></article></section><section><b>2028</b><article class="local"><strong>Forum des Jeunes Chercheurs 2028</strong></article><article class="local"><strong>Journée des Doctorants 2028</strong></article><article class="conference conditional"><strong>ISOT 2028</strong><span>if funded</span></article></section></div><div class="csi-comms-legend"><span class="conference">Conference</span><span class="local">Local / national</span><span class="mediation">Outreach</span><span class="conditional">Conditional</span></div>''')
comms = new_from(50, comms_fr, comms_en, chapter='Valorisation', part='Valorisation')

pub_fr = block('Valorisation', 'Publications', 'Trois continuités scientifiques, trois articles', 'Les regroupements suivent la filiation théorique et expérimentale des études.', '''
<div class="csi-publication-groups"><article><b>ARTICLE 1</b><h3>TWIXAV + TWIXOLF</h3><p>Du benchmark audiovisuel à la fenêtre impliquant l’olfaction.</p><span>Cycle rédaction → cible : ~6 mois après données exploitables</span></article><article><b>ARTICLE 2</b><h3>VIBEX + OASIS</h3><p>De la référence visuelle à l’influence du contexte olfactif.</p><span>Cycle rédaction → cible : ~6 mois après données exploitables</span></article><article><b>ARTICLE 3</b><h3>SOFT</h3><p>Limites élémentaires d’onset, offset et durée entre modalités.</p><span>Cycle rédaction → cible : ~6 mois après données exploitables</span></article></div>''')
pub_en = block('Dissemination', 'Publications', 'Three scientific continuities, three papers', 'The groupings follow the theoretical and experimental filiation of the studies.', '''
<div class="csi-publication-groups"><article><b>PAPER 1</b><h3>TWIXAV + TWIXOLF</h3><p>From audiovisual benchmark to a window involving olfaction.</p><span>Writing → target cycle: ~6 months after usable data</span></article><article><b>PAPER 2</b><h3>VIBEX + OASIS</h3><p>From the visual benchmark to olfactory-context influence.</p><span>Writing → target cycle: ~6 months after usable data</span></article><article><b>PAPER 3</b><h3>SOFT</h3><p>Elementary onset, offset and duration limits across modalities.</p><span>Writing → target cycle: ~6 months after usable data</span></article></div>''')
pubs = rewrite(50, pub_fr, pub_en, chapter='Valorisation', study='', appendix=False, part='Valorisation')

suite_div = divider(51, 'Suite de la thèse', 'Next steps', 6, 'Suite')

evo_fr = block('Suite de la thèse', 'Programme évolutif', 'Où se situe TWIXOLF dans le programme ?', 'À ce stade du récit, les références sont acquises, SOFT et OASIS sont prioritaires, et TWIXOLF devient le prochain verrou majeur de l’axe 1.', f'''
<div class="csi-evolution-tree"><section class="axis1"><header><b>AXE 1</b><span>{AXIS1_FR}</span></header><div><article class="past">TWIXAV</article><i>→</i><article class="past">SOFT</article><i>→</i><article class="active">TWIXOLF</article><i>→</i><article class="optional">SOLAR</article></div></section><section class="axis2"><header><b>AXE 2</b><span>{AXIS2_FR}</span></header><div><article class="past">VIBEX</article><i>→</i><article class="past">OASIS</article><span class="branch-gap"></span><article class="optional">BRAUD</article><i>→</i><article class="optional">BRAUDOLF</article></div></section></div><div class="csi-opacity-key"><span class="past">déjà présenté</span><span class="active">focus</span><span class="future">à venir</span><span class="optional">optionnel</span></div>''')
evo_en = block('Next steps', 'Evolving programme', 'Where does TWIXOLF sit in the programme?', 'At this point, the benchmarks are established, SOFT and OASIS are priorities, and TWIXOLF becomes the next major Axis 1 lock.', f'''
<div class="csi-evolution-tree"><section class="axis1"><header><b>AXIS 1</b><span>{AXIS1_EN}</span></header><div><article class="past">TWIXAV</article><i>→</i><article class="past">SOFT</article><i>→</i><article class="active">TWIXOLF</article><i>→</i><article class="optional">SOLAR</article></div></section><section class="axis2"><header><b>AXIS 2</b><span>{AXIS2_EN}</span></header><div><article class="past">VIBEX</article><i>→</i><article class="past">OASIS</article><span class="branch-gap"></span><article class="optional">BRAUD</article><i>→</i><article class="optional">BRAUDOLF</article></div></section></div><div class="csi-opacity-key"><span class="past">already presented</span><span class="active">focus</span><span class="future">next</span><span class="optional">optional</span></div>''')
evo = rewrite(52, evo_fr, evo_en, chapter='Suite de la thèse', study='', appendix=False, part='Suite')

# Optional project slides retained in the main path, with corrected axes and concise status.
def optional_project(idx, study, axis_fr, axis_en, principle_fr, principle_en, question_fr, question_en):
    fr = block('Suite de la thèse', f'{axis_fr} - conditionnel', study, 'Étude supplémentaire - uniquement si le calendrier des études noyaux le permet.', f'''<div class="csi-optional-project"><article><span>PRINCIPE</span><p>{principle_fr}</p></article><article><span>QUESTION</span><p>{question_fr}</p></article><div class="status">Juil. - déc. 2027 · conditionnel</div></div>''')
    en = block('Next steps', f'{axis_en} - conditional', study, 'Additional study - only if the core-study schedule allows it.', f'''<div class="csi-optional-project"><article><span>PRINCIPLE</span><p>{principle_en}</p></article><article><span>QUESTION</span><p>{question_en}</p></article><div class="status">Jul. - Dec. 2027 · conditional</div></div>''')
    return rewrite(idx, fr, en, chapter='Suite de la thèse', study=study, appendix=False, part='Suite')

solar = optional_project(54, 'SOLAR', 'Axe 1', 'Axis 1', 'Utiliser un indice olfactif pour orienter l’attention spatiale.', 'Use an olfactory cue to orient spatial attention.', 'L’olfaction peut-elle fournir un signal spatial exploitable pour une réponse visuelle ?', 'Can olfaction provide a usable spatial cue for a visual response?')
braud = optional_project(56, 'BRAUD', 'Axe 2', 'Axis 2', 'Étendre la logique des limites de scène au domaine auditif.', 'Extend scene-boundary logic to audition.', 'La mémoire auditive présente-t-elle une restriction systématique de ses limites ?', 'Does auditory memory show systematic restriction of its boundaries?')
braudolf = optional_project(57, 'BRAUDOLF', 'Axe 2', 'Axis 2', 'Ajouter un contexte olfactif au paradigme auditif.', 'Add olfactory context to the auditory paradigm.', 'L’odeur peut-elle modifier cette représentation auditive ?', 'Can odor modify this auditory representation?')

# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------
plan_div = divider(58, 'Rétroplanning', 'Planning', 7, 'Planning')

retro_fr = block('Rétroplanning', 'Rétrospective', 'Passé, présent, futur', 'Le comité doit pouvoir situer immédiatement ce qui est réalisé et ce qui reste à faire.', '''
<div class="csi-now"><section class="past"><span>PASSÉ / RÉALISÉ</span><h3>2025-2026</h3><p>TWIXAV · VIBEX · JDD 2026 · FLUXOLF en parallèle</p></section><div class="now-marker"><b>NOUS SOMMES ICI</b><span>Septembre 2026</span><strong>SOFT : développement → collecte</strong></div><section class="future"><span>À VENIR</span><h3>2026-2028</h3><p>OASIS · TWIXOLF · articles · rédaction · soutenance</p></section></div>''')
retro_en = block('Planning', 'Retrospective', 'Past, present, future', 'The committee should immediately see what is done and what remains.', '''
<div class="csi-now"><section class="past"><span>PAST / COMPLETED</span><h3>2025-2026</h3><p>TWIXAV · VIBEX · JDD 2026 · FLUXOLF in parallel</p></section><div class="now-marker"><b>WE ARE HERE</b><span>September 2026</span><strong>SOFT: development → data collection</strong></div><section class="future"><span>NEXT</span><h3>2026-2028</h3><p>OASIS · TWIXOLF · papers · thesis writing · defense</p></section></div>''')
retro = new_from(59, retro_fr, retro_en, chapter='Rétroplanning', part='Planning')

studplan_fr = block('Rétroplanning', 'Études de thèse', 'Rétroplanning des études', 'Les études noyaux restent prioritaires ; les extensions sont concentrées entre juillet et décembre 2027 et restent conditionnelles.', f'''
<div class="csi-study-plan"><div class="periods"><span>Année 1</span><span>Sept.-déc. 2026</span><span>2027</span><span>Juil.-déc. 2027</span><span>2028</span></div><section class="axis1"><header><b>AXE 1</b><span>{AXIS1_FR}</span></header><div class="lane"><article class="done">TWIXAV</article><article>SOFT</article><article class="major span2">TWIXOLF · Année 3</article><article class="optional">SOLAR</article><i></i></div></section><section class="axis2"><header><b>AXE 2</b><span>{AXIS2_FR}</span></header><div class="lane"><article class="done">VIBEX</article><i></i><article>OASIS</article><article class="optional stack"><span>BRAUD</span><span>BRAUDOLF</span></article><i></i></div></section></div><div class="csi-mini-takehome">SOLAR · BRAUD · BRAUDOLF : juillet-décembre 2027, uniquement si les études noyaux et le temps disponible le permettent.</div>''')
studplan_en = block('Planning', 'Thesis studies', 'Study schedule', 'Core studies remain the priority; extensions are concentrated between July and December 2027 and remain conditional.', f'''
<div class="csi-study-plan"><div class="periods"><span>Year 1</span><span>Sep.-Dec. 2026</span><span>2027</span><span>Jul.-Dec. 2027</span><span>2028</span></div><section class="axis1"><header><b>AXIS 1</b><span>{AXIS1_EN}</span></header><div class="lane"><article class="done">TWIXAV</article><article>SOFT</article><article class="major span2">TWIXOLF · Year 3</article><article class="optional">SOLAR</article><i></i></div></section><section class="axis2"><header><b>AXIS 2</b><span>{AXIS2_EN}</span></header><div class="lane"><article class="done">VIBEX</article><i></i><article>OASIS</article><article class="optional stack"><span>BRAUD</span><span>BRAUDOLF</span></article><i></i></div></section></div><div class="csi-mini-takehome">SOLAR · BRAUD · BRAUDOLF: July-December 2027, only if core studies and available time allow.</div>''')
study_plan = rewrite(59, studplan_fr, studplan_en, chapter='Rétroplanning', study='', appendix=False, part='Planning')

writeplan_fr = block('Rétroplanning', 'Rédaction et valorisation', 'De la collecte à la soutenance', 'Le planning articule publications, rédaction de thèse et communications sans publier avant que les données nécessaires soient disponibles.', '''
<div class="csi-track-plan"><section><b>ARTICLES</b><div><span>Article 3 · SOFT</span><span>Article 2 · VIBEX + OASIS</span><span>Article 1 · TWIXAV + TWIXOLF</span></div><small>Pour chaque article : environ 6 mois entre début de rédaction et cible de publication, après données exploitables.</small></section><section class="thesis"><b>THÈSE</b><div><span>Mars 2028</span><i>→</i><strong>Rédaction principale</strong><i>→</i><span>Oct. 2028 · soumission</span><i>~2 mois</i><span>Déc. 2028 · soutenance</span></div></section><section><b>COMMUNICATIONS</b><p>2026 · Nuit des Chercheurs | 2027 · FJC · JDD · ECRO · GDR O3 | 2028 · FJC · JDD · ISOT si financement</p></section><section><b>MÉDIATION</b><p>Expérimentarium 2027</p></section><section><b>ENSEIGNEMENT / FORMATION</b><p>2025-2026 : 54 h eq. TD / 60 h · 2026-2027 : 58 h eq. TD / 60,5 h</p></section></div>''')
writeplan_en = block('Planning', 'Writing and dissemination', 'From data collection to defense', 'The schedule coordinates papers, thesis writing and communications without publishing before the required data are available.', '''
<div class="csi-track-plan"><section><b>PAPERS</b><div><span>Paper 3 · SOFT</span><span>Paper 2 · VIBEX + OASIS</span><span>Paper 1 · TWIXAV + TWIXOLF</span></div><small>For each paper: about 6 months from writing start to publication target, after usable data.</small></section><section class="thesis"><b>THESIS</b><div><span>Mar. 2028</span><i>→</i><strong>Main writing period</strong><i>→</i><span>Oct. 2028 · submission</span><i>~2 months</i><span>Dec. 2028 · defense</span></div></section><section><b>COMMUNICATIONS</b><p>2026 · Nuit des Chercheurs | 2027 · FJC · JDD · ECRO · GDR O3 | 2028 · FJC · JDD · ISOT if funded</p></section><section><b>OUTREACH</b><p>Expérimentarium 2027</p></section><section><b>TEACHING / TRAINING</b><p>2025-2026: 54 h eq. TD / 60 h · 2026-2027: 58 h eq. TD / 60.5 h</p></section></div>''')
writing_plan = new_from(59, writeplan_fr, writeplan_en, chapter='Rétroplanning', part='Planning')

concl_fr = block('Conclusion', 'Synthèse', 'Une thèse construite par étapes', 'Le programme part de deux références solides, ouvre deux tests olfactifs prioritaires, puis converge vers TWIXOLF et la rédaction.', '''
<div class="csi-conclusion-flow"><article><b>ANNÉE 1</b><span>TWIXAV · VIBEX</span></article><i>→</i><article><b>ANNÉE 2</b><span>SOFT · OASIS</span></article><i>→</i><article><b>ANNÉE 3</b><span>TWIXOLF · analyses · articles</span></article><i>→</i><article class="focus"><b>2028</b><span>rédaction · soumission · soutenance</span></article></div>''')
concl_en = block('Conclusion', 'Synthesis', 'A thesis built in stages', 'The programme starts from two solid benchmarks, opens two priority olfactory tests, then converges on TWIXOLF and writing.', '''
<div class="csi-conclusion-flow"><article><b>YEAR 1</b><span>TWIXAV · VIBEX</span></article><i>→</i><article><b>YEAR 2</b><span>SOFT · OASIS</span></article><i>→</i><article><b>YEAR 3</b><span>TWIXOLF · analyses · papers</span></article><i>→</i><article class="focus"><b>2028</b><span>writing · submission · defense</span></article></div>''')
conclusion = rewrite(60, concl_fr, concl_en, chapter='Conclusion', study='', appendix=False, part='Planning')

points_fr = block('Conclusion', 'Arbitrages CSI', 'Points à discuter', 'Les arbitrages concernent maintenant la faisabilité et les priorités, pas l’architecture générale du programme.', '''
<div class="v16-decisions compact"><article><b>1</b><h3>SOFT</h3><p>Niveau de simplification compatible avec une collecte robuste.</p></article><article><b>2</b><h3>Ordre des collectes</h3><p>SOFT → OASIS → TWIXOLF.</p></article><article><b>3</b><h3>Extensions</h3><p>Critères de lancement de SOLAR, BRAUD et BRAUDOLF.</p></article><article><b>4</b><h3>Valorisation</h3><p>Calendrier des trois articles et communications.</p></article></div>''')
points_en = block('Conclusion', 'CSI decisions', 'Points to discuss', 'The decisions now concern feasibility and priorities, not the overall architecture of the programme.', '''
<div class="v16-decisions compact"><article><b>1</b><h3>SOFT</h3><p>Simplification level compatible with robust data collection.</p></article><article><b>2</b><h3>Collection order</h3><p>SOFT → OASIS → TWIXOLF.</p></article><article><b>3</b><h3>Extensions</h3><p>Launch criteria for SOLAR, BRAUD and BRAUDOLF.</p></article><article><b>4</b><h3>Dissemination</h3><p>Schedule for the three papers and communications.</p></article></div>''')
points = rewrite(61, points_fr, points_en, chapter='Conclusion', study='', appendix=False, part='Planning')

thanks = copy.deepcopy(old[64]); thanks['chapter'] = 'Conclusion'; thanks['_csi_part'] = 'Planning'

# ---------------------------------------------------------------------------
# Hidden bibliography / deferred studies
# ---------------------------------------------------------------------------
bib1_fr = block('Annexes', 'Bibliographie', 'Bibliographie - cadre théorique et axe 1', '', '''
<div class="csi-bibliography">
<p>Occelli, V., Calce, R. P., D'Alessandro, M., Turini, J., Battal, C., Cattoir, S., Bottini, R., Falagiarda, F., Lombardi, L., & Collignon, O. (2023). <i>Is Sight for Space and Sound for Time? Different Asymmetry of Spatiotemporal Interferences in Vision and Audition.</i> SSRN. https://doi.org/10.2139/ssrn.4524392</p>
<p>Capizzi, M., Chica, A. B., Lupiáñez, J., & Charras, P. (2023). Attention to space and time: Independent or interactive systems? A narrative review. <i>Psychonomic Bulletin & Review, 30</i>, 2030-2048. https://doi.org/10.3758/s13423-023-02325-y</p>
<p>Di Stefano, N., & Spence, C. (2025). Perceiving temporal structure within and between the senses: A multisensory/crossmodal perspective. <i>Attention, Perception, & Psychophysics, 87</i>, 1811-1838. https://doi.org/10.3758/s13414-025-03045-2</p>
<p>Ampollini, S., Ardizzi, M., Ferroni, F., & Cigala, A. (2024). Synchrony perception across senses: A systematic review of temporal binding window changes from infancy to adolescence in typical and atypical development. <i>Neuroscience & Biobehavioral Reviews, 162</i>, 105711. https://doi.org/10.1016/j.neubiorev.2024.105711</p>
<p>Sela, L., & Sobel, N. (2010). Human olfaction: a constant state of change-blindness. <i>Experimental Brain Research, 205</i>, 13-29. https://doi.org/10.1007/s00221-010-2348-6</p>
<p>Vroomen, J., & Keetels, M. (2010). Perception of intersensory synchrony: A tutorial review. <i>Attention, Perception, & Psychophysics, 72</i>, 871-884. https://doi.org/10.3758/APP.72.4.871</p>
<p>Powers, A. R., Hillock, A. R., & Wallace, M. T. (2009). Perceptual training narrows the temporal window of multisensory binding. <i>Journal of Neuroscience, 29</i>, 12265-12274.</p>
</div>''')
bib1_en = copy.deepcopy(bib1_fr); bib1_en['title'] = 'Bibliography - theoretical framework and Axis 1'; bib1_en['section'] = 'Appendices'; bib1_en['kicker'] = 'Bibliography'
bib1 = rewrite(62, bib1_fr, bib1_en, chapter='Annexes', study='', appendix=True, part=None)

bib2_fr = block('Annexes', 'Bibliographie', 'Bibliographie - axe 2 et scènes', '', '''
<div class="csi-bibliography">
<p>Rekow, D., Baudouin, J.-Y., Durand, K., & Leleu, A. (2022). Smell what you hardly see: Odors assist visual categorization in the human brain. <i>NeuroImage, 255</i>, 119181. https://doi.org/10.1016/j.neuroimage.2022.119181</p>
<p>Baccarani, A., & Brochard, R. (2024). Relaxing and stimulating ambient odors influence preferences for musical tempo. <i>Musicae Scientiae, 28</i>, 273-286. https://doi.org/10.1177/10298649231202976</p>
<p>Intraub, H., & Richardson, M. (1989). Wide-angle memories of close-up scenes. <i>Journal of Experimental Psychology: Learning, Memory, and Cognition, 15</i>, 179-187. https://doi.org/10.1037/0278-7393.15.2.179</p>
<p>Bainbridge, W. A., & Baker, C. I. (2020). Boundaries extend and contract in scene memory depending on image properties. <i>Current Biology, 30</i>.</p>
</div>''')
bib2_en = copy.deepcopy(bib2_fr); bib2_en['title'] = 'Bibliography - Axis 2 and scenes'; bib2_en['section'] = 'Appendices'; bib2_en['kicker'] = 'Bibliography'
bib2 = rewrite(63, bib2_fr, bib2_en, chapter='Annexes', study='', appendix=True, part=None)

sorbet = copy.deepcopy(old[53]); sorbet['appendix'] = True; sorbet['chapter'] = 'Annexes'; sorbet['_csi_part'] = None
for key, english in [('_fr', False), ('_en', True)]:
    h = sorbet.get(key, {})
    h['section'] = 'Annexes - pistes reportées' if not english else 'Appendices - deferred ideas'
    h['kicker'] = 'Axe 1 - piste reportée' if not english else 'Axis 1 - deferred idea'
    h['lead'] = 'Piste conservée pour discussion avec le jury, mais retirée du parcours principal.' if not english else 'Retained for jury discussion but removed from the main presentation path.'
sorbet.update(sorbet.get('_fr', {}))

cobex = copy.deepcopy(old[55]); cobex['appendix'] = True; cobex['chapter'] = 'Annexes'; cobex['_csi_part'] = None
for key, english in [('_fr', False), ('_en', True)]:
    h = cobex.get(key, {})
    h['section'] = 'Annexes - pistes reportées' if not english else 'Appendices - deferred ideas'
    h['kicker'] = 'Axe 2 - piste reportée' if not english else 'Axis 2 - deferred idea'
    h['lead'] = 'Piste conservée pour discussion avec le jury, mais retirée du parcours principal.' if not english else 'Retained for jury discussion but removed from the main presentation path.'
cobex.update(cobex.get('_fr', {}))

# ---------------------------------------------------------------------------
# Assemble final deck using the ORIGINAL slide-number map.
# ---------------------------------------------------------------------------
final = [
    cover, summary_slide, theory_divider, t4, t5, t6, t7, va1, va2, no_slide, less_slide, axis2_theory, axes9,
    programme_div, axes15, tree16,
    y1_div, y1sum, twintro, twmethod, twres, twtake, twsoft, vintro, vmethod, vres1, vres2, vres3, vtake, y1diff,
    flux, y1act, jdd, trans36,
    y2_div, axes38, prio, soft_intro, soft_method, oasis_intro, oasis_method, twixo_intro, twixo_method, y2diff, y2act,
    val_div, comms, pubs,
    suite_div, evo, solar, braud, braudolf,
    plan_div, retro, study_plan, writing_plan, conclusion, points, thanks,
    bib1, bib2, sorbet, cobex,
]
if len(final) != 64:
    raise RuntimeError(f'Final deck should contain 64 slides, got {len(final)}')

# Apply context strip after all structural operations.
for s in final:
    decorate_slide(s)
    s.pop('_csi_part', None)

# Genericize any remaining visible equipment detail while keeping popup metadata.
for s in final:
    for key, english in [('_fr', False), ('_en', True)]:
        h = s.get(key, {})
        c = h.get('content', '')
        if not c:
            continue
        repl = 'View equipment' if english else "Voir l'appareillage"
        c = re.sub(r'(<button class="[^"]*apparatus-open[^"]*"[^>]*><b>[^<]*</b><span>).*?(</span></button>)', lambda m: m.group(1) + repl + m.group(2), c, flags=re.S)
        h['content'] = c
    if s.get('_fr'):
        s.update(s['_fr'])

# ---------------------------------------------------------------------------
# CSS for the refactored narrative.
# ---------------------------------------------------------------------------
css = r'''
/* CSI-STRUCTURAL-REFACTOR-20260908 */
.csi-context-strip{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin:-2px 0 12px;min-height:28px}.csi-part-timeline{display:flex;align-items:center;gap:4px;flex:1;min-width:0;white-space:nowrap}.csi-part-timeline .csi-part-node{font-size:.57rem;letter-spacing:.035em;text-transform:uppercase;color:var(--muted);opacity:.58}.csi-part-timeline .csi-part-node.active{opacity:1;color:var(--accent);font-weight:800}.csi-part-timeline i{width:12px;height:1px;background:var(--line);flex:0 0 12px}.csi-axis-tag{display:flex;align-items:flex-start;gap:7px;max-width:46%;padding:5px 9px;border:1px solid var(--line);border-radius:10px;background:var(--white);font-size:.58rem;line-height:1.22}.csi-axis-tag b{white-space:nowrap;color:var(--accent)}.csi-axis-tag span{color:var(--muted)}.csi-axis-tag.axis1{border-left:3px solid #2f6f9f}.csi-axis-tag.axis2{border-left:3px solid #2f7d5a}.csi-axis-tag.side{border-left:3px solid #8c6e58}
.csi-agenda-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.csi-agenda-grid article{padding:16px;border:1px solid var(--line);border-radius:18px;background:var(--white)}.csi-agenda-grid b{font-size:.7rem;color:var(--accent)}.csi-agenda-grid h3{font-size:1rem;margin:5px 0}.csi-agenda-grid p{font-size:.78rem;margin:0;color:var(--muted)}
.csi-theory-four{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.csi-theory-four article,.csi-axis2-evidence article{padding:16px;border:1px solid var(--line);border-radius:18px;background:var(--white)}.csi-theory-four span,.csi-axis2-evidence span{font-size:.67rem;font-weight:800;letter-spacing:.06em;color:var(--accent)}.csi-theory-four h3,.csi-axis2-evidence h3{font-size:1rem;margin:7px 0}.csi-theory-four p,.csi-axis2-evidence p{font-size:.78rem;line-height:1.42;color:var(--muted);margin:0 0 8px}.csi-theory-four small,.csi-axis2-evidence small{font-size:.68rem;color:var(--muted)}
.csi-dimension-map{display:grid;grid-template-columns:180px 1fr;gap:22px;align-items:center;border:1px solid var(--line);border-radius:24px;padding:22px;background:var(--white)}.dimension-core{width:160px;height:160px;border-radius:50%;display:grid;place-items:center;align-content:center;background:color-mix(in srgb,var(--accent) 11%,var(--white));border:2px solid color-mix(in srgb,var(--accent) 35%,var(--line));text-align:center}.dimension-core b{font-size:1.25rem;color:var(--accent)}.dimension-core span{font-size:.72rem;color:var(--muted)}.dimension-track{display:flex;align-items:center;justify-content:space-between;gap:5px}.dimension-track article{min-width:76px;padding:12px 8px;border:1px solid var(--line);border-radius:15px;text-align:center}.dimension-track article b{display:block;color:var(--accent);font-size:.68rem}.dimension-track article span{font-size:.78rem;font-weight:700}.dimension-track i{height:1px;background:var(--line);flex:1}.dimension-orbit{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.dimension-orbit article{padding:18px 10px;border:1px solid var(--line);border-radius:16px;text-align:center;font-size:.86rem;font-weight:700}.csi-mini-takehome{margin-top:12px;text-align:center;padding:9px 14px;border-radius:13px;background:color-mix(in srgb,var(--accent) 7%,var(--white));font-size:.75rem;color:var(--muted)}
.csi-binding-flow,.csi-benchmark-flow,.csi-transition-chain,.csi-twixolf-flow{display:flex;align-items:center;justify-content:center;gap:12px}.csi-binding-flow article,.csi-benchmark-flow article,.csi-transition-chain article,.csi-twixolf-flow article{flex:1;padding:18px;border:1px solid var(--line);border-radius:18px;background:var(--white);text-align:center}.csi-binding-flow .focus,.csi-benchmark-flow .focus,.csi-transition-chain .question,.csi-twixolf-flow .focus{background:color-mix(in srgb,var(--accent) 10%,var(--white));border-color:color-mix(in srgb,var(--accent) 35%,var(--line))}.csi-binding-flow b,.csi-benchmark-flow b,.csi-transition-chain strong,.csi-twixolf-flow b{display:block}.csi-binding-flow span,.csi-benchmark-flow span,.csi-transition-chain span,.csi-transition-chain small,.csi-twixolf-flow span{font-size:.75rem;color:var(--muted)}.csi-binding-flow i,.csi-binding-flow em,.csi-benchmark-flow em,.csi-transition-chain i,.csi-twixolf-flow i{font-style:normal;font-size:1.5rem;color:var(--muted)}
.csi-va-compare{display:grid;grid-template-columns:1fr 100px 1fr;gap:16px;align-items:stretch}.csi-va-compare article{padding:24px;border-radius:22px;border:1px solid var(--line);background:var(--white)}.csi-va-compare article span{font-size:.68rem;font-weight:900;letter-spacing:.08em;color:var(--accent)}.csi-va-compare article h3{margin:8px 0}.csi-va-compare article p{font-weight:700}.csi-va-compare article small{color:var(--muted)}.va-mid{display:grid;place-items:center;align-content:center;text-align:center}.va-mid b{font-size:2rem;color:var(--accent)}.va-mid span{font-size:.66rem;color:var(--muted)}
.csi-no-space .provocation{display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:14px;font-size:1.1rem;letter-spacing:.07em}.csi-no-space .provocation b{font-size:1.7rem;color:var(--accent)}.csi-less-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.csi-less-grid article{padding:16px;border:1px solid var(--line);border-radius:18px;background:var(--white)}.csi-less-grid article.focus{background:color-mix(in srgb,var(--accent) 9%,var(--white));border-color:color-mix(in srgb,var(--accent) 35%,var(--line))}.csi-less-grid b{display:block;margin-bottom:6px}.csi-less-grid p{font-size:.76rem;color:var(--muted);margin:0}.less-equation{display:flex;align-items:center;justify-content:center;gap:18px;margin-top:16px;padding:12px;border-radius:16px;background:color-mix(in srgb,var(--accent) 7%,var(--white))}.less-equation strong{color:var(--accent);font-size:1.15rem}.csi-axis2-evidence{display:grid;grid-template-columns:1fr 1fr 1.1fr;gap:14px}.csi-axis2-evidence .focus{background:color-mix(in srgb,var(--accent) 9%,var(--white))}
.csi-axis-pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}.csi-axis-pair article{padding:22px;border-radius:22px;border:1px solid var(--line);background:var(--white)}.csi-axis-pair article.axis1{border-top:4px solid #2f6f9f}.csi-axis-pair article.axis2{border-top:4px solid #2f7d5a}.csi-axis-pair span{font-size:.7rem;font-weight:900;letter-spacing:.08em}.csi-axis-pair h3{font-size:1.05rem;margin:8px 0}.csi-axis-pair p{font-size:.8rem;color:var(--muted)}
.csi-program-pairs{display:grid;grid-template-columns:1fr 1fr;gap:18px}.csi-program-pairs section{border:1px solid var(--line);border-radius:22px;overflow:hidden;background:var(--white)}.csi-program-pairs section.axis1{border-top:4px solid #2f6f9f}.csi-program-pairs section.axis2{border-top:4px solid #2f7d5a}.csi-program-pairs header{padding:14px 16px;border-bottom:1px solid var(--line)}.csi-program-pairs header b{display:block;font-size:.7rem;color:var(--accent)}.csi-program-pairs header span{font-size:.72rem;color:var(--muted)}.csi-program-pairs section>div{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:14px}.csi-program-pairs article{padding:13px;border-radius:15px;background:color-mix(in srgb,var(--accent) 6%,var(--white));text-align:center}.csi-program-pairs article strong{display:block}.csi-program-pairs article small{color:var(--muted)}.csi-program-pairs.compact article.focus{box-shadow:inset 0 0 0 2px color-mix(in srgb,var(--accent) 35%,transparent)}
.csi-genealogy,.csi-evolution-tree{display:grid;grid-template-columns:1fr 1fr;gap:20px}.csi-genealogy section,.csi-evolution-tree section{padding:16px;border:1px solid var(--line);border-radius:22px;background:var(--white)}.csi-genealogy section.axis1,.csi-evolution-tree section.axis1{border-top:4px solid #2f6f9f}.csi-genealogy section.axis2,.csi-evolution-tree section.axis2{border-top:4px solid #2f7d5a}.csi-genealogy header,.csi-evolution-tree header{margin-bottom:12px}.csi-genealogy header b,.csi-evolution-tree header b{font-size:.7rem;color:var(--accent)}.csi-genealogy header span,.csi-evolution-tree header span{display:block;font-size:.62rem;color:var(--muted)}.gene-chain{display:flex;flex-direction:column;align-items:center;gap:4px}.gene-chain>article{position:relative;width:78%;padding:10px 14px;border:1px solid var(--line);border-radius:14px;text-align:center}.gene-chain>article:before{content:attr(data-year);position:absolute;left:-74px;top:50%;transform:translateY(-50%);font-size:.58rem;color:var(--muted)}.gene-chain i{font-style:normal;color:var(--muted)}.gene-chain .optional{opacity:.5;border-style:dashed}.gene-branch{display:flex;align-items:center;gap:6px;margin-top:8px}.gene-branch article{padding:8px 12px;border:1px dashed var(--line);border-radius:12px;opacity:.55}.gene-branch i{transform:rotate(-90deg)}
.csi-year-foundations{display:grid;grid-template-columns:1fr 1fr .7fr;gap:16px}.csi-year-foundations article,.csi-two-foundations article{padding:22px;border:1px solid var(--line);border-radius:22px;background:var(--white)}.csi-year-foundations article span,.csi-two-foundations article span{font-size:.68rem;font-weight:900;letter-spacing:.07em;color:var(--accent)}.csi-year-foundations .side{opacity:.72}.csi-benchmark-study{display:flex;align-items:center;gap:10px}.csi-benchmark-study article{flex:1;padding:20px;border:1px solid var(--line);border-radius:20px;background:var(--white);text-align:center}.csi-benchmark-study .focus{background:color-mix(in srgb,#0072B2 8%,var(--white));border-color:color-mix(in srgb,#0072B2 35%,var(--line))}.csi-benchmark-study .future{opacity:.7}.csi-benchmark-study em{font-style:normal;font-size:1.5rem;color:var(--muted)}.csi-benchmark-study span{font-size:.65rem;font-weight:900;color:#0072B2}.csi-benchmark-study p{font-size:.75rem;color:var(--muted)}
.csi-method-simple{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.csi-method-simple article{padding:16px;border:1px solid var(--line);border-radius:18px;background:var(--white)}.csi-method-simple article.primary{border-color:color-mix(in srgb,var(--study,var(--accent)) 42%,var(--line));background:color-mix(in srgb,var(--study,var(--accent)) 7%,var(--white))}.csi-method-simple article span{font-size:.62rem;font-weight:900;letter-spacing:.06em;color:var(--study,var(--accent))}.csi-method-simple h3{margin:6px 0;font-size:1rem}.csi-method-simple p{font-size:.74rem;color:var(--muted);margin:0}.study-floating{margin-top:12px}.study-floating .apparatus-open span{max-width:145px}
.csi-result-dual{display:grid;grid-template-columns:1.35fr .75fr;gap:14px}.csi-result-dual figure{margin:0;padding:8px;border:1px solid var(--line);border-radius:18px;background:#fff}.csi-result-dual img{width:100%;height:min(35vh,330px);object-fit:contain}.csi-result-dual figcaption{font-size:.65rem;color:#5f6f65;text-align:center}.csi-result-facts{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:10px}.csi-result-facts article{padding:8px 11px;border:1px solid var(--line);border-radius:12px;background:var(--white)}.csi-result-facts article b{display:block;font-size:.72rem}.csi-result-facts article span{font-size:.65rem;color:var(--muted)}.csi-result-facts .key{border-color:color-mix(in srgb,#0072B2 45%,var(--line));background:color-mix(in srgb,#0072B2 7%,var(--white))}.csi-result-facts .result-meta-row{margin:0}
.csi-vibex-size{display:grid;grid-template-columns:.8fr 1.3fr;gap:16px}.csi-vibex-size>article{padding:20px;border:1px solid var(--line);border-radius:20px;background:var(--white)}.csi-vibex-size article>span{font-size:.65rem;font-weight:900;color:var(--accent)}.csi-vibex-size .split{display:grid;grid-template-columns:1fr 1fr;gap:10px}.csi-vibex-size .split>span{grid-column:1/-1}.csi-vibex-size .split div{padding:12px;border-radius:13px;background:color-mix(in srgb,var(--accent) 6%,var(--white))}.csi-vibex-size .split p{font-size:.72rem;color:var(--muted)}.csi-vibex-size.compact{grid-template-columns:1fr;margin-top:12px}.csi-vibex-size.compact>article{padding:12px 16px}
.csi-vibex-conditions{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:10px}.csi-vibex-conditions article{padding:11px;border:1px solid var(--line);border-radius:14px;text-align:center;background:var(--white)}.csi-vibex-conditions b{font-size:1rem}.csi-vibex-conditions span{display:block;font-size:.65rem;color:var(--muted)}.csi-vibex-conditions .pair-a,.csi-vibex-conditions .pair-b{border-color:color-mix(in srgb,#2f7d5a 45%,var(--line))}.vibex-manual-demo{display:grid;grid-template-columns:1fr auto;gap:12px;border:1px solid var(--line);border-radius:18px;padding:10px;background:var(--white)}.vibex-demo-stage{height:185px;border-radius:13px;overflow:hidden;background:#111;display:grid;place-items:center}.vibex-demo-stage img{width:100%;height:100%;object-fit:contain}.vibex-demo-ready{color:#fff;text-align:center}.vibex-demo-ready b{display:block}.vibex-demo-ready span{font-size:.72rem;opacity:.7}.vibex-demo-controls{display:flex;flex-direction:column;gap:7px;justify-content:center;min-width:125px}.vibex-demo-controls button{border:1px solid var(--line);border-radius:11px;padding:9px 12px;background:var(--white);color:var(--text);font:inherit;cursor:pointer}.vibex-demo-controls button:first-child{background:#2f7d5a;color:#fff;border-color:#2f7d5a}.vibex-demo-controls span{font-size:.68rem;color:var(--muted);text-align:center}
.csi-transfer-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.csi-transfer-grid article{padding:17px;border:1px solid var(--line);border-radius:18px;background:var(--white)}.csi-transfer-grid b{display:block;color:var(--accent);margin-bottom:5px}.csi-transfer-grid span{font-size:.75rem;color:var(--muted)}.csi-transfer-grid .focus{background:color-mix(in srgb,#2f7d5a 8%,var(--white));border-color:color-mix(in srgb,#2f7d5a 35%,var(--line))}.csi-difficulty-summary{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}.csi-difficulty-summary section{padding:20px;border:1px solid var(--line);border-radius:20px;background:var(--white)}.csi-difficulty-summary span{font-size:.68rem;font-weight:900;letter-spacing:.07em;color:var(--accent)}.csi-difficulty-summary p{font-size:.85rem;line-height:1.5;margin:9px 0 0;color:var(--muted)}
.csi-jdd-simple .jdd-question{padding:22px;border:1px solid var(--line);border-radius:22px;background:color-mix(in srgb,var(--accent) 7%,var(--white));font-size:1.35rem;font-weight:800;text-align:center}.jdd-points{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px}.jdd-points article{padding:14px;border:1px solid var(--line);border-radius:16px;background:var(--white);text-align:center}.jdd-points b{display:block}.jdd-points span{font-size:.7rem;color:var(--muted)}.jdd-points .award{border-color:color-mix(in srgb,#D8AF55 55%,var(--line));background:color-mix(in srgb,#D8AF55 10%,var(--white))}.csi-two-foundations{display:grid;grid-template-columns:1fr 1fr;gap:18px}.csi-two-foundations article b{display:block;margin-top:12px;color:var(--accent)}
.csi-priority-road{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.csi-priority-road article{position:relative;padding:20px;border:1px solid var(--line);border-radius:20px;background:var(--white)}.csi-priority-road article>b{position:absolute;right:14px;top:12px;font-size:1.5rem;opacity:.18}.csi-priority-road article span{font-size:.7rem;color:var(--accent);font-weight:800}.csi-priority-road article p{font-size:.75rem;color:var(--muted)}.csi-soft-question{display:grid;grid-template-columns:1fr 1fr 1fr 50px 1.2fr;gap:10px;align-items:stretch}.csi-soft-question article,.csi-soft-question .focus{padding:18px;border:1px solid var(--line);border-radius:18px;background:var(--white);text-align:center}.csi-soft-question .focus{background:color-mix(in srgb,var(--accent) 8%,var(--white))}.csi-soft-question span{font-size:.7rem;color:var(--muted)}.csi-soft-question em{display:grid;place-items:center;font-size:1.4rem;font-style:normal}.csi-oasis-flow{display:flex;gap:10px;align-items:center}.csi-oasis-flow article{flex:1;padding:18px;border:1px solid var(--line);border-radius:18px;background:var(--white);text-align:center}.csi-oasis-flow .focus{background:color-mix(in srgb,#2f7d5a 8%,var(--white))}.csi-oasis-flow i,.csi-oasis-flow em{font-style:normal;font-size:1.4rem;color:var(--muted)}.csi-oasis-flow span{font-size:.65rem;font-weight:900;color:var(--accent)}
.csi-comms-timeline{display:grid;grid-template-columns:.7fr 1.5fr 1fr;gap:14px}.csi-comms-timeline section{padding:14px;border:1px solid var(--line);border-radius:18px;background:var(--white);display:grid;gap:8px;align-content:start}.csi-comms-timeline section>b{font-size:1.15rem;color:var(--accent)}.csi-comms-timeline article{padding:8px 10px;border-radius:11px;background:color-mix(in srgb,var(--accent) 5%,var(--white));border-left:3px solid var(--line)}.csi-comms-timeline article strong{font-size:.73rem}.csi-comms-timeline article span{display:block;font-size:.62rem;color:var(--muted)}.csi-comms-timeline .conference{border-left-color:#2f6f9f}.csi-comms-timeline .local{border-left-color:#2f7d5a}.csi-comms-timeline .mediation{border-left-color:#b0793d}.csi-comms-timeline .conditional{opacity:.62;border-style:dashed}.csi-comms-legend{display:flex;justify-content:center;gap:14px;margin-top:10px;font-size:.65rem;color:var(--muted)}.csi-publication-groups{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.csi-publication-groups article{padding:20px;border:1px solid var(--line);border-radius:20px;background:var(--white)}.csi-publication-groups b{font-size:.65rem;color:var(--accent)}.csi-publication-groups h3{margin:8px 0}.csi-publication-groups p{font-size:.76rem;color:var(--muted)}.csi-publication-groups span{font-size:.65rem;color:var(--muted);border-top:1px solid var(--line);display:block;padding-top:8px}
.csi-evolution-tree section>div{display:flex;align-items:center;gap:7px}.csi-evolution-tree article{flex:1;padding:11px;border:1px solid var(--line);border-radius:13px;text-align:center}.csi-evolution-tree article.past{opacity:.47}.csi-evolution-tree article.active{opacity:1;transform:scale(1.04);background:color-mix(in srgb,var(--accent) 12%,var(--white));border:2px solid var(--accent);font-weight:900}.csi-evolution-tree article.optional{opacity:.28;border-style:dashed}.csi-evolution-tree i{font-style:normal;color:var(--muted)}.branch-gap{flex:.3}.csi-opacity-key{display:flex;justify-content:center;gap:12px;margin-top:12px}.csi-opacity-key span{font-size:.62rem;padding:5px 9px;border-radius:9px;border:1px solid var(--line)}.csi-opacity-key .past{opacity:.47}.csi-opacity-key .optional{opacity:.3}.csi-optional-project{display:grid;grid-template-columns:1fr 1fr;gap:14px}.csi-optional-project article{padding:20px;border:1px solid var(--line);border-radius:20px;background:var(--white)}.csi-optional-project article span{font-size:.65rem;font-weight:900;color:var(--accent)}.csi-optional-project article p{font-size:.82rem;color:var(--muted)}.csi-optional-project .status{grid-column:1/-1;text-align:center;font-size:.72rem;padding:9px;border:1px dashed var(--line);border-radius:12px;color:var(--muted)}
.csi-now{display:grid;grid-template-columns:1fr .82fr 1fr;gap:14px;align-items:stretch}.csi-now section,.now-marker{padding:22px;border:1px solid var(--line);border-radius:22px;background:var(--white)}.csi-now .past{opacity:.52}.csi-now .future{opacity:.72}.now-marker{display:grid;place-items:center;align-content:center;text-align:center;border:2px solid var(--accent);background:color-mix(in srgb,var(--accent) 10%,var(--white));box-shadow:0 0 0 5px color-mix(in srgb,var(--accent) 7%,transparent)}.now-marker b{font-size:.75rem;letter-spacing:.07em;color:var(--accent)}.now-marker span{font-size:.7rem;color:var(--muted);margin:5px}.now-marker strong{font-size:.9rem}.csi-now section>span{font-size:.65rem;font-weight:900;color:var(--muted)}.csi-now section p{font-size:.78rem;color:var(--muted)}
.csi-study-plan{display:grid;gap:10px}.csi-study-plan .periods{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-left:158px}.csi-study-plan .periods span{font-size:.61rem;text-align:center;color:var(--muted)}.csi-study-plan section{display:grid;grid-template-columns:150px 1fr;gap:8px;align-items:center}.csi-study-plan header{font-size:.62rem}.csi-study-plan header b{display:block;color:var(--accent)}.csi-study-plan header span{color:var(--muted);font-size:.55rem;line-height:1.25}.csi-study-plan .lane{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}.csi-study-plan article,.csi-study-plan .lane>i{min-height:48px;border-radius:10px}.csi-study-plan article{display:grid;place-items:center;padding:7px;border:1px solid var(--line);background:var(--white);font-size:.7rem;font-weight:800;text-align:center}.csi-study-plan article.done{opacity:.5}.csi-study-plan article.major{border:2px solid var(--accent)}.csi-study-plan article.optional{opacity:.45;border-style:dashed}.csi-study-plan article.stack{gap:2px}.csi-study-plan .span2{grid-column:3/5}.csi-study-plan section.axis1{border-left:3px solid #2f6f9f;padding-left:8px}.csi-study-plan section.axis2{border-left:3px solid #2f7d5a;padding-left:8px}
.csi-track-plan{display:grid;gap:8px}.csi-track-plan section{display:grid;grid-template-columns:120px 1fr;gap:12px;padding:11px 14px;border:1px solid var(--line);border-radius:14px;background:var(--white)}.csi-track-plan section>b{font-size:.64rem;color:var(--accent)}.csi-track-plan section>div{display:flex;align-items:center;gap:7px;flex-wrap:wrap}.csi-track-plan section span,.csi-track-plan section strong{font-size:.7rem;padding:5px 8px;border-radius:9px;background:color-mix(in srgb,var(--accent) 6%,var(--white))}.csi-track-plan section small{grid-column:2;font-size:.6rem;color:var(--muted)}.csi-track-plan section p{margin:0;font-size:.68rem;color:var(--muted)}.csi-track-plan .thesis{border-color:color-mix(in srgb,var(--accent) 35%,var(--line))}.csi-track-plan i{font-size:.62rem;color:var(--muted);font-style:normal}
.csi-conclusion-flow{display:flex;align-items:stretch;gap:9px}.csi-conclusion-flow article{flex:1;padding:18px;border:1px solid var(--line);border-radius:18px;background:var(--white);text-align:center}.csi-conclusion-flow article.focus{background:color-mix(in srgb,var(--accent) 9%,var(--white));border-color:color-mix(in srgb,var(--accent) 35%,var(--line))}.csi-conclusion-flow b{display:block;color:var(--accent)}.csi-conclusion-flow span{font-size:.72rem;color:var(--muted)}.csi-conclusion-flow i{display:grid;place-items:center;font-style:normal;color:var(--muted)}.v16-decisions.compact{grid-template-columns:repeat(4,1fr)}.csi-bibliography{display:grid;grid-template-columns:1fr 1fr;gap:10px}.csi-bibliography p{margin:0;padding:10px 12px;border:1px solid var(--line);border-radius:12px;background:var(--white);font-size:.62rem;line-height:1.35;color:var(--muted)}
@media(max-width:1100px){.csi-agenda-grid{grid-template-columns:repeat(3,1fr)}.csi-theory-four,.csi-less-grid,.csi-transfer-grid{grid-template-columns:1fr 1fr}.csi-method-simple{grid-template-columns:1fr 1fr}.csi-context-strip{display:block}.csi-axis-tag{max-width:100%;margin-top:6px}.csi-part-timeline{overflow:hidden}.csi-program-pairs,.csi-genealogy,.csi-evolution-tree{grid-template-columns:1fr}.csi-result-dual{grid-template-columns:1fr 1fr}.csi-comms-timeline{grid-template-columns:1fr 1fr}.csi-publication-groups{grid-template-columns:1fr}.csi-study-plan .periods{margin-left:0}.csi-study-plan section{grid-template-columns:1fr}.csi-soft-question{grid-template-columns:1fr 1fr 1fr}.csi-soft-question em{display:none}}
@media(max-width:720px){.csi-agenda-grid,.csi-theory-four,.csi-less-grid,.csi-axis2-evidence,.csi-axis-pair,.csi-year-foundations,.csi-method-simple,.csi-transfer-grid,.csi-difficulty-summary,.csi-publication-groups,.csi-now{grid-template-columns:1fr}.csi-dimension-map{grid-template-columns:1fr}.dimension-core{margin:auto}.dimension-track{flex-wrap:wrap}.dimension-track i{display:none}.csi-va-compare{grid-template-columns:1fr}.va-mid{display:none}.csi-binding-flow,.csi-benchmark-flow,.csi-transition-chain,.csi-oasis-flow,.csi-twixolf-flow,.csi-conclusion-flow{flex-direction:column}.csi-binding-flow i,.csi-binding-flow em,.csi-benchmark-flow em,.csi-transition-chain i,.csi-oasis-flow i,.csi-oasis-flow em,.csi-twixolf-flow i,.csi-conclusion-flow i{transform:rotate(90deg)}.csi-result-dual{grid-template-columns:1fr}.csi-vibex-size{grid-template-columns:1fr}.csi-vibex-conditions{grid-template-columns:1fr 1fr}.vibex-manual-demo{grid-template-columns:1fr}.vibex-demo-controls{flex-direction:row;flex-wrap:wrap}.csi-comms-timeline{grid-template-columns:1fr}.csi-study-plan .periods{display:none}.csi-study-plan .lane{grid-template-columns:1fr}.csi-study-plan .span2{grid-column:auto}.csi-track-plan section{grid-template-columns:1fr}.csi-track-plan section small{grid-column:1}.csi-bibliography{grid-template-columns:1fr}.v16-decisions.compact{grid-template-columns:1fr 1fr}}
'''
if '/* CSI-STRUCTURAL-REFACTOR-20260908 */' not in text:
    text = text.replace('</style>', css + '\n</style>', 1)

# ---------------------------------------------------------------------------
# Manual VIBEX demo. Real repository stimuli only; no automatic animation.
# ---------------------------------------------------------------------------
js = r'''
<script id="csiVibexManualDemo">
(()=>{
  const steps=[
    {src:'assets/demo/image_L_16.jpg',fr:'Image 1',en:'Image 1'},
    {src:'assets/demo/Masque_SCR.webp',fr:'Masque',en:'Mask'},
    {src:'assets/demo/image_S_16.jpg',fr:'Image 2',en:'Image 2'}
  ];
  function isEn(){return (document.documentElement.lang||'fr').toLowerCase().startsWith('en')}
  function reset(root){root.dataset.vibexState='0';const img=root.querySelector('img'),ready=root.querySelector('.vibex-demo-ready'),lab=root.querySelector('[data-vibex-label]');if(img){img.hidden=true;img.removeAttribute('src')}if(ready)ready.hidden=false;if(lab)lab.textContent=isEn()?'Ready':'Prêt'}
  function next(root){let state=Number(root.dataset.vibexState||0);if(state>=steps.length)return reset(root);const step=steps[state],img=root.querySelector('img'),ready=root.querySelector('.vibex-demo-ready'),lab=root.querySelector('[data-vibex-label]');if(ready)ready.hidden=true;if(img){img.src=step.src;img.hidden=false}if(lab)lab.textContent=isEn()?step.en:step.fr;root.dataset.vibexState=String(state+1)}
  document.addEventListener('click',e=>{const n=e.target.closest('[data-vibex-next]');if(n){e.preventDefault();const root=n.closest('.vibex-manual-demo');if(root)next(root);return}const r=e.target.closest('[data-vibex-reset]');if(r){e.preventDefault();const root=r.closest('.vibex-manual-demo');if(root)reset(root)}});
})();
</script>
'''
if 'id="csiVibexManualDemo"' not in text:
    text = text.replace('</body>', js + '\n</body>', 1)

# Replace slides only after external CSS/JS injections have been calculated from original indices.
new_json = json.dumps(final, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

# Remove prohibited long-dash glyphs throughout user-visible code/text.
text = text.replace('—', '-').replace('–', '-')

# Guard the frozen backup.
if hashlib.sha256(BACKUP.read_bytes()).hexdigest() != backup_hash:
    raise RuntimeError('index_save.html changed during refactor')

# Structural validation.
check_start = text.index(MARKER) + len(MARKER)
check, _ = json.JSONDecoder().raw_decode(text[check_start:])
if len(check) != 64:
    raise RuntimeError('Final slide count changed unexpectedly')
main = [s for s in check if not s.get('appendix')]
apps = [s for s in check if s.get('appendix')]
if len(main) != 60 or len(apps) != 4:
    raise RuntimeError(f'Expected 60 main + 4 appendix, got {len(main)} + {len(apps)}')
for s in main:
    blob = ' '.join([s.get('title',''), s.get('lead',''), s.get('content',''), (s.get('_fr') or {}).get('content','')])
    if 'SORBET' in blob or 'COBEX' in blob:
        raise RuntimeError(f'Deferred project remains in main path: {s.get("title")}')
for s in main:
    if s.get('study') == 'SOLAR':
        blob = ' '.join([s.get('kicker',''), s.get('content','')])
        if 'Axe 2' in blob:
            raise RuntimeError('SOLAR still shown in Axis 2')
for required in [AXIS1_FR, AXIS2_FR, 'Less space, less time', 'Occelli et al., 2023', 'Capizzi et al., 2023', 'Di Stefano & Spence, 2025', 'Ampollini et al., 2024', 'Rekow et al., 2022', 'Baccarani & Brochard, 2024', 'Nuit des Chercheurs 2026', 'Expérimentarium 2027', 'ISOT 2028', 'NOUS SOMMES ICI', 'Mars 2028', 'Oct. 2028', 'Déc. 2028']:
    if required not in text:
        raise RuntimeError(f'Missing required content: {required}')
if 'À consolider' in ' '.join(s.get('content','') for s in main):
    raise RuntimeError('Obsolete TWIXAV consolidation block remains')
if 'F(' in check[20]['content']:
    raise RuntimeError('F value remains on fused TWIXAV result slide')
if 'mouvement oculaire maîtrisé' not in text:
    raise RuntimeError('Required VIBEX wording missing')
if 'data-vibex-next' not in text or 'assets/demo/Masque_SCR.webp' not in text:
    raise RuntimeError('Manual VIBEX demo missing')
if '—' in text or '–' in text:
    raise RuntimeError('Long dash glyph remains')

PATH.write_text(text, encoding='utf-8')
print('Core refactor complete')
print('Slides:', len(check), 'main:', len(main), 'appendix:', len(apps))
print('Backup SHA256:', backup_hash)
