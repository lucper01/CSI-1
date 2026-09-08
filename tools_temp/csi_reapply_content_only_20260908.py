from pathlib import Path
import copy, json, re, hashlib

BACKUP = Path('index_save.html')
OUT = Path('index.html')
EXPECTED_BACKUP = '9948fe7ffbb327340129d83624a51611d7325f3c171fd0834e3e5f7f81c307fe'
source = BACKUP.read_text(encoding='utf-8')
if hashlib.sha256(BACKUP.read_bytes()).hexdigest() != EXPECTED_BACKUP:
    raise RuntimeError('Frozen backup changed')

MARKER='const slides = '
st=source.index(MARKER)+len(MARKER)
slides, rel=json.JSONDecoder().raw_decode(source[st:])
en=st+rel
if len(slides)!=64:
    raise RuntimeError(f'Expected 64 saved slides, got {len(slides)}')
slides=copy.deepcopy(slides)

AX1_FR="Limites spatio-temporelles de l'olfaction vs celles de la vision et de l'audition"
AX2_FR="Influence de l'olfaction sur la perception spatio-temporelle en audition et en vision"
AX1_EN='Spatiotemporal limits of olfaction vs those of vision and audition'
AX2_EN='Influence of olfaction on spatiotemporal perception in audition and vision'


def set_lang(i, fr=None, en=None):
    s=slides[i-1]
    if fr:
        h=s.get('_fr') or {}
        h.update(fr); s['_fr']=h; s.update(h)
    if en:
        h=s.get('_en') or {}
        h.update(en); s['_en']=h
    return s

# 1 - Cover: content-only edits inside the existing cover components.
for key, is_en in [('_fr',False),('_en',True)]:
    h=slides[0].get(key) or {}
    c=h.get('content','')
    if is_en:
        c=re.sub(r'(<strong>Arnaud LELEU</strong><br>)Associate Professor(?![^<]*HDR)',r'\1Associate Professor, HDR',c,1,flags=re.I)
    else:
        c=re.sub(r'(<strong>Arnaud LELEU</strong><br>)Maître de conférences(?!\s*HDR)',r'\1Maître de conférences HDR',c,1,flags=re.I)
    if 'assets/logos/logo_docc.png' not in c:
        c=c.replace('</div></div><aside class="identity-card">','<img src="assets/logos/logo_docc.png" alt="DOCC Lab"></div></div><aside class="identity-card">',1)
    h['content']=c; slides[0][key]=h
slides[0].update(slides[0]['_fr'])

# 4 - Theoretical slide refocused on the four explicitly requested studies, using the saved grid/card DA.
set_lang(4,
 {'title':'Vision et audition - espace et temps ne sont pas pondérés de la même façon',
  'lead':'Les travaux récents convergent vers une idée importante pour STOLF : espace et temps sont disponibles dans les deux modalités, mais leur poids relatif, leur sélection attentionnelle et leur structuration perceptive ne sont pas équivalents.',
  'content':'''<div class="grid two"><div class="card"><div class="mono">Occelli et al., 2023</div><h3>« Is sight for space and sound for time? »</h3><p>Les interférences espace-temps ne sont pas symétriques entre vision et audition. La vision fournit un référentiel spatial particulièrement robuste, tandis que l’audition montre une forte sensibilité aux relations temporelles.</p></div><div class="card dark"><div class="mono">Capizzi et al., 2023</div><h3>Attention à l’espace et au temps</h3><p>La revue souligne que sélection spatiale et sélection temporelle peuvent être dissociées tout en interagissant selon la tâche et les contraintes attentionnelles.</p></div><div class="card"><div class="mono">Di Stefano & Spence, 2025</div><h3>Percevoir une structure temporelle</h3><p>La temporalité perceptive peut être étudiée à l’intérieur d’une modalité et entre modalités, depuis les événements élémentaires jusqu’à leur organisation multisensorielle.</p></div><div class="card"><div class="mono">Ampollini et al., 2024</div><h3>Synchronie et fenêtre de liaison</h3><p>La synchronie perçue repose sur une fenêtre de tolérance temporelle dont la largeur et les propriétés varient avec les systèmes sensoriels et le développement.</p></div></div><div class="callout" style="margin-top:16px"><strong>Point de départ pour STOLF :</strong> vision et audition offrent deux références spatio-temporelles bien documentées, mais déjà opposées dans la manière dont espace et temps structurent la perception.</div><div class="csi-cite">Occelli et al. (2023); Capizzi et al. (2023); Di Stefano & Spence (2025); Ampollini et al. (2024).</div>'''},
 {'title':'Vision and audition - space and time are not weighted in the same way',
  'lead':'Recent work converges on an important idea for STOLF: space and time are available in both modalities, but their relative weight, attentional selection and perceptual structuring are not equivalent.',
  'content':'''<div class="grid two"><div class="card"><div class="mono">Occelli et al., 2023</div><h3>“Is sight for space and sound for time?”</h3><p>Space-time interference is not symmetric across vision and audition. Vision provides a particularly robust spatial reference, whereas audition shows strong sensitivity to temporal relations.</p></div><div class="card dark"><div class="mono">Capizzi et al., 2023</div><h3>Attention to space and time</h3><p>The review emphasizes that spatial and temporal selection can be dissociated while still interacting depending on task and attentional constraints.</p></div><div class="card"><div class="mono">Di Stefano & Spence, 2025</div><h3>Perceiving temporal structure</h3><p>Perceptual timing can be studied within and across modalities, from elementary events to multisensory temporal organization.</p></div><div class="card"><div class="mono">Ampollini et al., 2024</div><h3>Synchrony and binding windows</h3><p>Perceived synchrony relies on a temporal tolerance window whose width and properties vary across sensory systems and development.</p></div></div><div class="callout" style="margin-top:16px"><strong>Starting point for STOLF:</strong> vision and audition provide well-documented spatiotemporal references, yet already differ in how space and time structure perception.</div><div class="csi-cite">Occelli et al. (2023); Capizzi et al. (2023); Di Stefano & Spence (2025); Ampollini et al. (2024).</div>'''})

# 8 - Requested wording only.
for h in [slides[7], slides[7].get('_fr') or {}, slides[7].get('_en') or {}]:
    if 'lead' in h:
        h['lead']=h['lead'].replace('asymétrie','opposition').replace('asymmetry','contrast')
    if 'content' in h:
        h['content']=h['content'].replace('Le verrou à tester','Le verrou à lever').replace('The constraint to test','The constraint to address')
slides[7].update(slides[7].get('_fr') or {})

# 9 - Reuse the redundant saved "Deux axes" slide for the requested nuance. Same v16-axes/callout DA.
set_lang(9,
 {'section':'Cadre théorique','kicker':'Nuancer le contraste olfactif','title':'Less space, less time','lead':'L’olfaction n’est ni sans espace ni sans temps. Ces dimensions y sont surtout moins directement accessibles, moins précises et moins spontanément structurantes que dans la vision ou l’audition.',
  'content':'''<div class="v16-axes"><article><b>Espace</b><h3>Présent, mais moins directement disponible</h3><p>Les gradients, la distance à une source, le suivi actif d’une trace et les comparaisons inter-narinaires montrent qu’une information spatiale olfactive existe.</p></article><article><b>Temps</b><h3>Présent, mais échantillonné autrement</h3><p>Le signal évolue dans le temps et le sniff impose un échantillonnage rythmique qui lie disponibilité du stimulus, respiration et perception.</p></article></div><div class="callout" style="margin-top:16px"><strong>Reformulation :</strong> plutôt que « no space, no time », l’hypothèse de travail devient « less space, less time » : espace et temps existent, mais sont moins saillants et plus difficiles à exploiter consciemment.</div><div class="csi-cite">Sela & Sobel (2010); Porter et al. (2007); Mainland & Sobel (2006).</div>''',
  'notes':'Nuancer explicitement le slogan : l’objectif n’est pas de nier des représentations spatiales ou temporelles olfactives.'},
 {'section':'Theoretical context','kicker':'Nuancing the olfactory contrast','title':'Less space, less time','lead':'Olfaction is neither spaceless nor timeless. These dimensions are instead less directly accessible, less precise and less spontaneously structuring than in vision or audition.',
  'content':'''<div class="v16-axes"><article><b>Space</b><h3>Present, but less directly available</h3><p>Gradients, source distance, active scent tracking and inter-nostril comparisons show that olfactory spatial information does exist.</p></article><article><b>Time</b><h3>Present, but sampled differently</h3><p>The signal evolves over time and sniffing imposes rhythmic sampling that links stimulus availability, respiration and perception.</p></article></div><div class="callout" style="margin-top:16px"><strong>Reframing:</strong> rather than “no space, no time”, the working hypothesis becomes “less space, less time”: both dimensions exist but are less salient and harder to exploit consciously.</div><div class="csi-cite">Sela & Sobel (2010); Porter et al. (2007); Mainland & Sobel (2006).</div>''',
  'notes':'Explicitly nuance the slogan: the aim is not to deny olfactory spatial or temporal representations.'})

# 12-13 - Add the two requested crossmodal evidence anchors without changing their grid/card DA.
set_lang(12,
 {'content':'''<div class="grid three"><div class="card"><div class="mono">Perception</div><h3>Catégorisation visuelle</h3><p>Une odeur peut faciliter la catégorisation d’un objet lorsque l’information visuelle est difficile à extraire, montrant que le contexte olfactif peut influencer le traitement visuel.</p></div><div class="card"><div class="mono">Attention</div><h3>Objets visuels congruents</h3><p>Lorsqu’une odeur est présente, les participants fixent davantage les objets visuels qui lui correspondent.</p></div><div class="card dark"><div class="mono">Espace de scène</div><h3>Une représentation reconstruite</h3><p>La mémoire des limites d’une scène peut s’étendre ou se contracter, offrant un terrain expérimental pour tester une influence olfactive.</p></div></div><div class="callout" style="margin-top:16px"><strong>Enjeu :</strong> l’olfaction peut déjà modifier certains traitements visuels. OASIS teste plus spécifiquement si elle modifie la représentation spatiale mémorisée d’une scène.</div><div class="csi-cite">Rekow et al. (2022); Seo et al. (2010); Intraub & Richardson (1989); Bainbridge & Baker (2020).</div>'''},
 {'content':'''<div class="grid three"><div class="card"><div class="mono">Perception</div><h3>Visual categorization</h3><p>An odor can facilitate object categorization when visual information is difficult to extract, showing that olfactory context can influence visual processing.</p></div><div class="card"><div class="mono">Attention</div><h3>Congruent visual objects</h3><p>When an odor is present, observers look more often at visually corresponding objects.</p></div><div class="card dark"><div class="mono">Scene space</div><h3>A reconstructed representation</h3><p>Memory for scene boundaries can extend or contract, providing an experimental test bed for olfactory influence.</p></div></div><div class="callout" style="margin-top:16px"><strong>Issue:</strong> olfaction can already alter some visual processes. OASIS more specifically tests whether it changes remembered spatial representation of a scene.</div><div class="csi-cite">Rekow et al. (2022); Seo et al. (2010); Intraub & Richardson (1989); Bainbridge & Baker (2020).</div>'''})
set_lang(13,
 {'content':'''<div class="grid three"><div class="card"><div class="mono">Correspondances</div><h3>Odeurs et propriétés sonores</h3><p>Les participants associent de manière non aléatoire certaines odeurs à des hauteurs et à des timbres particuliers.</p></div><div class="card"><div class="mono">Préférence temporelle</div><h3>Odeur et tempo musical</h3><p>Des odeurs ambiantes relaxantes ou stimulantes peuvent modifier les préférences pour le tempo musical, ce qui confirme une influence olfactivo-auditive sans démontrer encore un effet direct sur les jugements temporels élémentaires.</p></div><div class="card dark"><div class="mono">Question ouverte</div><h3>Et le temps ou l’espace auditif ?</h3><p>Les effets directs d’une odeur sur la durée, l’onset, l’offset, la synchronie ou la localisation auditive restent beaucoup moins documentés.</p></div></div><div class="callout" style="margin-top:16px"><strong>Positionnement :</strong> cette lacune délimite le versant exploratoire de l’Axe 2, sans extrapoler au-delà des résultats existants.</div><div class="csi-cite">Crisinel & Spence (2012); Baccarani & Brochard (2024); Zhou et al. (2019).</div>'''},
 {'content':'''<div class="grid three"><div class="card"><div class="mono">Correspondences</div><h3>Odors and sound properties</h3><p>Participants non-randomly match certain odors with particular pitches and timbres.</p></div><div class="card"><div class="mono">Temporal preference</div><h3>Odor and musical tempo</h3><p>Relaxing or stimulating ambient odors can alter musical-tempo preferences, confirming an olfactory-auditory influence without yet demonstrating a direct effect on elementary temporal judgments.</p></div><div class="card dark"><div class="mono">Open question</div><h3>What about auditory time or space?</h3><p>Direct odor effects on auditory duration, onset, offset, synchrony or localization remain far less documented.</p></div></div><div class="callout" style="margin-top:16px"><strong>Positioning:</strong> this gap defines the exploratory part of Axis 2 without extrapolating beyond existing evidence.</div><div class="csi-cite">Crisinel & Spence (2012); Baccarani & Brochard (2024); Zhou et al. (2019).</div>'''})

# 15 - New axis wording and project allocation, same v16-axes/v16-pills layout.
set_lang(15,
 {'lead':'La thèse s’organise autour de deux axes complémentaires : caractériser les limites spatio-temporelles de l’olfaction par comparaison aux modalités de référence, puis tester l’influence de l’olfaction sur la perception visuelle et auditive.',
  'content':f'''<div class="v16-axes"><article><b>Axe 1</b><h3>{AX1_FR}</h3><p>Comparer les contraintes spatiales et temporelles propres aux modalités et déterminer ce qui change lorsque l’olfaction est impliquée.</p><div class="v16-pills"><span data-study="TWIXAV">TWIXAV</span><span data-study="SOFT">SOFT</span><span data-study="TWIXOLF">TWIXOLF</span><span data-study="SOLAR">SOLAR</span></div></article><article><b>Axe 2</b><h3>{AX2_FR}</h3><p>Déterminer si un contexte olfactif peut modifier certains traitements spatio-temporels visuels ou auditifs.</p><div class="v16-pills"><span data-study="VIBEX">VIBEX</span><span data-study="OASIS">OASIS</span><span data-study="BRAUD">BRAUD</span><span data-study="BRAUDOLF">BRAUDOLF</span></div></article></div><div class="v16-ref"><strong>Références</strong><span>Sela & Sobel, 2010; Vroomen & Keetels, 2010; Intraub & Richardson, 1989; Rekow et al., 2022.</span></div>'''},
 {'lead':'The thesis is organized around two complementary axes: characterize the spatiotemporal limits of olfaction relative to reference modalities, then test the influence of olfaction on visual and auditory perception.',
  'content':f'''<div class="v16-axes"><article><b>Axis 1</b><h3>{AX1_EN}</h3><p>Compare modality-specific spatial and temporal constraints and determine what changes when olfaction is involved.</p><div class="v16-pills"><span data-study="TWIXAV">TWIXAV</span><span data-study="SOFT">SOFT</span><span data-study="TWIXOLF">TWIXOLF</span><span data-study="SOLAR">SOLAR</span></div></article><article><b>Axis 2</b><h3>{AX2_EN}</h3><p>Determine whether an olfactory context can modify visual or auditory spatiotemporal processing.</p><div class="v16-pills"><span data-study="VIBEX">VIBEX</span><span data-study="OASIS">OASIS</span><span data-study="BRAUD">BRAUD</span><span data-study="BRAUDOLF">BRAUDOLF</span></div></article></div><div class="v16-ref"><strong>References</strong><span>Sela & Sobel, 2010; Vroomen & Keetels, 2010; Intraub & Richardson, 1989; Rekow et al., 2022.</span></div>'''})

# 16 - Keep saved architecture grid, but remove deferred extensions and do not motivate SOFT before TWIXAV results.
for key,is_en in [('_fr',False),('_en',True)]:
    h=slides[15].get(key) or {}
    c=h.get('content','')
    if is_en:
        c=c.replace('Audiovisual temporal window and asymmetry motivating SOFT.','Audiovisual temporal window used as the reference benchmark before olfactory translation.')
        c=c.replace('SORBET - SOLAR - COBEX - BRAUD - BRAUDOLF.','SOLAR - BRAUD - BRAUDOLF.')
    else:
        c=c.replace('Fenêtre temporelle audiovisuelle et asymétrie qui motive SOFT.','Fenêtre temporelle audiovisuelle servant de référentiel avant la transposition à l’olfaction.')
        c=c.replace('SORBET - SOLAR - COBEX - BRAUD - BRAUDOLF.','SOLAR - BRAUD - BRAUDOLF.')
    h['content']=c; slides[15][key]=h
slides[15].update(slides[15].get('_fr') or {})

# 19 - TWIXAV is first a benchmark. SOFT appears only after the results.
set_lang(19,
 {'title':'TWIXAV - construire le référentiel audiovisuel','lead':'Avant de tester l’olfaction, TWIXAV établit un benchmark temporel dans deux modalités dont la synchronie est bien caractérisée.',
  'content':'''<div class="grid three"><div class="card"><div class="mono">Concept</div><h3>Temporal Binding Window</h3><p>La probabilité de juger deux événements comme simultanés varie avec leur décalage temporel et permet de caractériser une fenêtre d’intégration.</p></div><div class="card"><div class="mono">Question</div><h3>La durée modifie-t-elle cette fenêtre ?</h3><p>TWIXAV teste si la durée des stimuli affecte la tolérance au décalage audiovisuel plutôt que de supposer une fenêtre unique et fixe.</p></div><div class="card dark"><div class="mono">Rôle</div><h3>Un benchmark avant l’olfaction</h3><p>Les propriétés de la fenêtre audiovisuelle servent de référence avant toute transposition à une situation impliquant l’olfaction.</p></div></div>'''},
 {'title':'TWIXAV - building the audiovisual benchmark','lead':'Before testing olfaction, TWIXAV establishes a temporal benchmark in two modalities whose synchrony is well characterized.',
  'content':'''<div class="grid three"><div class="card"><div class="mono">Concept</div><h3>Temporal Binding Window</h3><p>The probability of judging two events as simultaneous varies with their temporal offset and characterizes an integration window.</p></div><div class="card"><div class="mono">Question</div><h3>Does duration change this window?</h3><p>TWIXAV tests whether stimulus duration affects audiovisual temporal tolerance rather than assuming one fixed window.</p></div><div class="card dark"><div class="mono">Role</div><h3>A benchmark before olfaction</h3><p>The properties of the audiovisual window provide a reference before translating the question to a situation involving olfaction.</p></div></div>'''})

# 21 - Fuse former result slides 21/22 around the TBW, keeping the saved results layout. F values intentionally removed.
set_lang(21,
 {'kicker':'TWIXAV - Résultats','title':'TWIXAV - la Temporal Binding Window dépend de la durée','lead':'Le jugement de simultanéité dépend fortement du SOA, et la largeur individuelle moyenne de la fenêtre se rétrécit lorsque la durée des stimuli augmente.',
  'content':'''<div class="results-expanded"><div class="results-copy"><div class="result-meta-row"><div class="m1-owner"><span>Mémoire M1</span><strong>Alicia Emorine</strong></div><div class="m1-owner result-n"><strong>n = 19</strong></div></div><div class="m1-stat-grid"><div><b>p &lt; .001</b><span>effet du SOA</span></div><div><b>p &lt; .001</b><span>effet de la durée</span></div><div><b>660 ms</b><span>durée 50 ms</span></div><div><b>594 / 558 ms</b><span>durées 150 / 250 ms</span></div></div><div class="callout"><strong>Post-hoc FDR :</strong> 50 vs 150 ms, pFDR = .030 - 50 vs 250 ms, pFDR = .006 - 150 vs 250 ms, pFDR = .060.</div></div><figure class="result-figure-large"><img src="assets/results/twixav_tbw_width.svg" alt="Largeur moyenne de la fenêtre temporelle audiovisuelle selon la durée"><figcaption>La largeur individuelle moyenne de la TBW diminue d’environ 102 ms entre 50 et 250 ms.</figcaption></figure></div>'''},
 {'kicker':'TWIXAV - Results','title':'TWIXAV - the Temporal Binding Window depends on duration','lead':'Simultaneity judgments strongly depend on SOA, and mean individual window width narrows as stimulus duration increases.',
  'content':'''<div class="results-expanded"><div class="results-copy"><div class="result-meta-row"><div class="m1-owner"><span>Master’s thesis</span><strong>Alicia Emorine</strong></div><div class="m1-owner result-n"><strong>n = 19</strong></div></div><div class="m1-stat-grid"><div><b>p &lt; .001</b><span>SOA effect</span></div><div><b>p &lt; .001</b><span>duration effect</span></div><div><b>660 ms</b><span>50 ms duration</span></div><div><b>594 / 558 ms</b><span>150 / 250 ms durations</span></div></div><div class="callout"><strong>FDR post-hoc:</strong> 50 vs 150 ms, pFDR = .030 - 50 vs 250 ms, pFDR = .006 - 150 vs 250 ms, pFDR = .060.</div></div><figure class="result-figure-large"><img src="assets/results/twixav_tbw_width.svg" alt="Mean audiovisual temporal-window width by duration"><figcaption>Mean individual TBW width decreases by about 102 ms between 50 and 250 ms.</figcaption></figure></div>'''})

# 22 - Preserve PSS/asymmetry result as the second result slide.
old23=copy.deepcopy(slides[22])
slides[21]=old23
for h in [slides[21],slides[21].get('_fr') or {},slides[21].get('_en') or {}]:
    if 'kicker' in h:
        h['kicker']=h['kicker'].replace('3/3','2/2').replace('Results 3/3','Results 2/2')
slides[21].update(slides[21].get('_fr') or {})

# 23 - Use the freed third results slot as the requested reasoning bridge, with the existing grid/card DA.
set_lang(23,
 {'kicker':'TWIXAV - Transition','title':'TWIXAV - du résultat à la question mécanistique','lead':'Le benchmark audiovisuel montre qu’une même asynchronie n’est pas traitée indépendamment des propriétés temporelles du stimulus. Il faut maintenant déterminer où se situent les limites propres à chaque modalité.',
  'content':'''<div class="grid three"><div class="card"><div class="mono">Résultat</div><h3>La TBW n’est pas fixe</h3><p>Sa largeur varie avec la durée, tandis que le PSS et l’asymétrie restent relativement stables dans ce prétest.</p></div><div class="card"><div class="mono">Question</div><h3>D’où vient cette opposition ?</h3><p>Une partie du phénomène peut dépendre de la précision avec laquelle chaque modalité fournit un début, une fin et une durée perceptifs.</p></div><div class="card dark"><div class="mono">Étape suivante</div><h3>SOFT, puis TWIXOLF</h3><p>SOFT mesure directement onset, offset et durée dans chaque modalité. TWIXOLF pourra ensuite transposer la liaison temporelle à l’olfaction sur cette base.</p></div></div>'''},
 {'kicker':'TWIXAV - Transition','title':'TWIXAV - from the result to the mechanistic question','lead':'The audiovisual benchmark shows that a given asynchrony is not processed independently of stimulus temporal properties. The next step is to determine where modality-specific limits arise.',
  'content':'''<div class="grid three"><div class="card"><div class="mono">Result</div><h3>The TBW is not fixed</h3><p>Its width varies with duration, while PSS and asymmetry remain relatively stable in this pre-test.</p></div><div class="card"><div class="mono">Question</div><h3>Where does this contrast come from?</h3><p>Part of the phenomenon may depend on how precisely each modality provides perceptual onset, offset and duration.</p></div><div class="card dark"><div class="mono">Next step</div><h3>SOFT, then TWIXOLF</h3><p>SOFT directly measures onset, offset and duration in each modality. TWIXOLF can then translate temporal binding to olfaction on that basis.</p></div></div>'''})

# 24 - Remove obsolete consolidation block.
set_lang(24,
 {'content':'''<div class="grid three"><div class="card"><div class="mono">Acquis</div><h3>Un référentiel temporel exploitable</h3><p>Le paradigme audiovisuel fournit une TBW sensible à la durée et des indicateurs individuels utilisables comme benchmark.</p></div><div class="card"><div class="mono">Limite</div><h3>Le résultat ne dit pas encore pourquoi</h3><p>La TBW agrège les latences et incertitudes propres aux deux modalités et ne permet pas, à elle seule, d’isoler onset, offset ou durée perçus.</p></div><div class="card dark"><div class="mono">Décision</div><h3>Mesurer avant de transposer</h3><p>SOFT caractérise d’abord les limites temporelles élémentaires, puis TWIXOLF teste la liaison temporelle lorsque l’olfaction est impliquée.</p></div></div>'''},
 {'content':'''<div class="grid three"><div class="card"><div class="mono">Acquired</div><h3>A usable temporal benchmark</h3><p>The audiovisual paradigm provides a duration-sensitive TBW and individual metrics usable as a benchmark.</p></div><div class="card"><div class="mono">Limit</div><h3>The result does not yet explain why</h3><p>The TBW aggregates modality-specific latencies and uncertainties and cannot by itself isolate perceived onset, offset or duration.</p></div><div class="card dark"><div class="mono">Decision</div><h3>Measure before translating</h3><p>SOFT first characterizes elementary temporal limits, then TWIXOLF tests temporal binding when olfaction is involved.</p></div></div>'''})

# 26 - VIBEX introduction without announcing OASIS prematurely.
set_lang(26,
 {'title':'VIBEX - établir une référence visuelle de Boundary Extension','lead':'VIBEX vérifie d’abord le phénomène visuel et les facteurs qui le modulent, avant toute manipulation olfactive.',
  'content':'''<div class="grid three"><div class="card"><div class="mono">Phénomène</div><h3>Boundary Extension</h3><p>La mémoire d’une scène peut inclure des informations spatiales au-delà de ses limites réellement présentées, révélant une représentation constructive de l’espace.</p></div><div class="card"><div class="mono">Référence</div><h3>Une base visuelle contrôlée</h3><p>Le paradigme doit produire un effet stable sans contexte olfactif pour pouvoir servir ensuite de référentiel expérimental.</p></div><div class="card dark"><div class="mono">Facteur à caractériser</div><h3>La taille des images</h3><p>Elle constitue à la fois un contrôle méthodologique de robustesse et une variable théorique susceptible de modifier l’étendue spatiale reconstruite.</p></div></div>'''},
 {'title':'VIBEX - establishing a visual Boundary Extension benchmark','lead':'VIBEX first verifies the visual phenomenon and the factors that modulate it, before any olfactory manipulation.',
  'content':'''<div class="grid three"><div class="card"><div class="mono">Phenomenon</div><h3>Boundary Extension</h3><p>Scene memory can include spatial information beyond the boundaries actually presented, revealing constructive spatial representation.</p></div><div class="card"><div class="mono">Reference</div><h3>A controlled visual baseline</h3><p>The paradigm must produce a stable effect without olfactory context before it can serve as an experimental benchmark.</p></div><div class="card dark"><div class="mono">Factor to characterize</div><h3>Image size</h3><p>It is both a methodological robustness control and a theoretical variable that may alter reconstructed spatial extent.</p></div></div>'''})

# 27 - Clarify LL/SS/LS/SL and the double role of image size; preserve the study/demo components.
for key,is_en in [('_fr',False),('_en',True)]:
    h=slides[26].get(key) or {}
    c=h.get('content','')
    if is_en:
        c=c.replace('Comparison of scenes with LL, SS, LS and SL conditions, several sizes and same / different judgments.','Four framing transitions: LL (wide-wide), SS (close-close), LS (wide-close) and SL (close-wide), crossed with three display sizes and an identical / different judgment.')
        c=c.replace('Scene memory produces a systematic boundary bias; its magnitude and direction depend on image properties and framing.','Scene memory should produce a systematic boundary bias. Image size is tested both as a robustness control and as a theoretically meaningful spatial factor.')
    else:
        c=c.replace('Comparaison de scènes avec conditions LL, SS, LS et SL, plusieurs tailles et jugement identique / différent.','Quatre transitions de cadrage : LL (large-large), SS (serré-serré), LS (large-serré) et SL (serré-large), croisées avec trois tailles d’affichage et un jugement identique / différent.')
        c=c.replace("La mémoire de scène produit un biais systématique des limites; son amplitude et sa direction dépendent des propriétés de l'image et du cadrage.","La mémoire de scène devrait produire un biais systématique des limites. La taille est testée à la fois comme contrôle de robustesse et comme facteur spatial théoriquement pertinent.")
    h['content']=c; slides[26][key]=h
slides[26].update(slides[26].get('_fr') or {})

# 29 - Make the double interpretation of size explicit.
for key,is_en in [('_fr',False),('_en',True)]:
    h=slides[28].get(key) or {}
    c=h.get('content','')
    if is_en:
        c=c.replace('<strong>Reading:</strong>','<strong>Twofold interpretation:</strong> methodological - verify that the framing effect is not tied to one display size; theoretical - test whether reconstructed spatial extent depends on the visual extent of the scene. <strong>Result:</strong>')
    else:
        c=c.replace('<strong>Lecture :</strong>','<strong>Double intérêt :</strong> méthodologique - vérifier que l’effet de cadrage ne dépend pas d’une seule taille d’affichage; théorique - tester si l’étendue spatiale reconstruite dépend de l’étendue visuelle de la scène. <strong>Résultat :</strong>')
    h['content']=c; slides[28][key]=h
slides[28].update(slides[28].get('_fr') or {})

# 31 - Take-home message and requested wording.
set_lang(31,
 {'title':'VIBEX - ce que l’on retient avant la suite olfactive','lead':'Le prétest remplit son rôle de référence : la signature de Boundary Extension est mesurable, la taille module son amplitude et les principaux contrôles méthodologiques sont identifiés.',
  'content':'''<div class="grid three"><div class="card"><div class="mono">Acquis</div><h3>Une asymétrie robuste</h3><p>La différence SL-LS fournit une signature comportementale nette du changement de cadrage.</p></div><div class="card"><div class="mono">Contrôles</div><h3>Taille et regard</h3><p>La taille doit rester explicitement contrôlée et le mouvement oculaire maîtrisé afin d’éviter qu’un changement de stratégie visuelle ne soit confondu avec l’effet spatial recherché.</p></div><div class="card dark"><div class="mono">Suite</div><h3>Introduire l’olfaction</h3><p>Une fois cette référence stabilisée, OASIS peut tester directement si un contexte olfactif modifie la représentation spatiale mémorisée.</p></div></div>'''},
 {'title':'VIBEX - what to retain before the olfactory step','lead':'The pre-test fulfills its role as a benchmark: the Boundary Extension signature is measurable, size modulates its magnitude and the main methodological controls are identified.',
  'content':'''<div class="grid three"><div class="card"><div class="mono">Acquired</div><h3>A robust asymmetry</h3><p>The SL-LS difference provides a clear behavioral signature of framing change.</p></div><div class="card"><div class="mono">Controls</div><h3>Size and gaze</h3><p>Image size must remain explicitly controlled and eye movement kept under control so that a change in visual strategy is not confused with the spatial effect of interest.</p></div><div class="card dark"><div class="mono">Next</div><h3>Introduce olfaction</h3><p>Once this benchmark is stabilized, OASIS can directly test whether olfactory context changes remembered spatial representation.</p></div></div>'''})

# 50 - Requested three-paper strategy, same v16-pubs DA.
set_lang(50,
 {'title':'Publications - stratégie en trois articles','lead':'La valorisation est structurée autour de trois ensembles cohérents, chacun reliant les études qui répondent à une même question.',
  'content':'''<div class="v16-pubs"><article data-study="TWIXAV"><span>1</span><h3>TWIXAV + TWIXOLF</h3><p>Fenêtre temporelle de référence puis transposition à une situation impliquant l’olfaction.</p></article><article data-study="VIBEX"><span>2</span><h3>VIBEX + OASIS</h3><p>Référence visuelle de Boundary Extension puis test de l’influence olfactive sur la représentation spatiale.</p></article><article data-study="SOFT"><span>3</span><h3>SOFT</h3><p>Article mécanistique sur onset, offset et durée perçus en audition, vision et olfaction.</p></article></div><div class="v16-callout"><strong>Principe :</strong> engager la rédaction lorsqu’un ensemble de données est exploitable, avec une cible d’environ six mois entre démarrage de la rédaction et soumission lorsque le calendrier le permet.</div>'''},
 {'title':'Publications - three-paper strategy','lead':'Dissemination is structured around three coherent sets, each linking studies that answer the same question.',
  'content':'''<div class="v16-pubs"><article data-study="TWIXAV"><span>1</span><h3>TWIXAV + TWIXOLF</h3><p>Reference temporal window followed by translation to a situation involving olfaction.</p></article><article data-study="VIBEX"><span>2</span><h3>VIBEX + OASIS</h3><p>Visual Boundary Extension benchmark followed by a test of olfactory influence on spatial representation.</p></article><article data-study="SOFT"><span>3</span><h3>SOFT</h3><p>Mechanistic paper on perceived onset, offset and duration in audition, vision and olfaction.</p></article></div><div class="v16-callout"><strong>Principle:</strong> start writing once a usable data set is available, targeting roughly six months from writing start to submission when the schedule allows.</div>'''})

# 52 - Main extension map: SOLAR is Axis 1; SORBET/COBEX deferred to appendices.
set_lang(52,
 {'lead':'Après les études prioritaires, trois extensions restent envisageables selon les résultats, le temps disponible et la faisabilité.',
  'content':'<div class="v16-extension-map"><article data-study="SOLAR"><b>Axe 1</b><h3>SOLAR</h3><p>Attention spatiale olfactive - complémentaire.</p></article><article data-study="BRAUD"><b>Axe 2</b><h3>BRAUD</h3><p>Restriction auditive - exploratoire.</p></article><article data-study="BRAUDOLF"><b>Axe 2</b><h3>BRAUDOLF</h3><p>Audition + olfaction - exploratoire.</p></article></div><div class="v16-callout"><strong>Condition :</strong> ces études ne sont lancées que si les études noyaux sont suffisamment avancées et si le calendrier doctoral reste soutenable.</div>'},
 {'lead':'After the priority studies, three extensions remain possible depending on results, available time and feasibility.',
  'content':'<div class="v16-extension-map"><article data-study="SOLAR"><b>Axis 1</b><h3>SOLAR</h3><p>Olfactory spatial attention - complementary.</p></article><article data-study="BRAUD"><b>Axis 2</b><h3>BRAUD</h3><p>Auditory restriction - exploratory.</p></article><article data-study="BRAUDOLF"><b>Axis 2</b><h3>BRAUDOLF</h3><p>Audition + olfaction - exploratory.</p></article></div><div class="v16-callout"><strong>Condition:</strong> these studies are launched only if core studies are sufficiently advanced and the doctoral schedule remains sustainable.</div>'})

# 54 - SOLAR belongs to Axis 1.
for h in [slides[53],slides[53].get('_fr') or {},slides[53].get('_en') or {}]:
    if 'kicker' in h:
        h['kicker']=h['kicker'].replace('Axe 2','Axe 1').replace('Axis 2','Axis 1')
slides[53].update(slides[53].get('_fr') or {})

# 59 - Keep the existing retroplanning component but update only content and dates.
set_lang(59,
 {'title':'Rétroplanning des études et de la thèse','lead':'Le calendrier place les études noyaux en priorité, concentre les extensions conditionnelles en 2027 et réserve 2028 à la convergence des analyses, articles et rédaction.',
  'content':'''<div class="v16-retro"><div class="v16-periods"><span>Sept-Déc 2026</span><span>Jan-Juin 2027</span><span>Juil-Déc 2027</span><span>2028</span></div><section><h3>Axe 1 - limites spatio-temporelles</h3><div class="lane core"><b>Planifiées</b><article data-study="SOFT"><strong>SOFT</strong></article><article data-study="TWIXOLF"><strong>TWIXOLF</strong></article><article data-study="SOLAR"><strong>SOLAR*</strong></article><i></i></div></section><section><h3>Axe 2 - influence olfactive</h3><div class="lane core"><b>Planifiées / conditionnelles</b><i></i><article data-study="OASIS"><strong>OASIS</strong></article><article class="stack"><span data-study="BRAUD"><strong>BRAUD*</strong></span><span data-study="BRAUDOLF"><strong>BRAUDOLF*</strong></span></article><i></i></div></section></div><div class="v16-callout"><strong>NOUS SOMMES ICI :</strong> septembre 2026 - développement puis collecte SOFT. *SOLAR, BRAUD et BRAUDOLF : juillet-décembre 2027 uniquement si faisables. Rédaction principale de la thèse : mars-octobre 2028 - soumission visée en octobre 2028 - soutenance visée en décembre 2028, soit environ deux mois après la soumission.</div>'''},
 {'title':'Study and thesis timeline','lead':'The schedule prioritizes core studies, concentrates conditional extensions in 2027 and reserves 2028 for convergence of analyses, papers and thesis writing.',
  'content':'''<div class="v16-retro"><div class="v16-periods"><span>Sep-Dec 2026</span><span>Jan-Jun 2027</span><span>Jul-Dec 2027</span><span>2028</span></div><section><h3>Axis 1 - spatiotemporal limits</h3><div class="lane core"><b>Planned</b><article data-study="SOFT"><strong>SOFT</strong></article><article data-study="TWIXOLF"><strong>TWIXOLF</strong></article><article data-study="SOLAR"><strong>SOLAR*</strong></article><i></i></div></section><section><h3>Axis 2 - olfactory influence</h3><div class="lane core"><b>Planned / conditional</b><i></i><article data-study="OASIS"><strong>OASIS</strong></article><article class="stack"><span data-study="BRAUD"><strong>BRAUD*</strong></span><span data-study="BRAUDOLF"><strong>BRAUDOLF*</strong></span></article><i></i></div></section></div><div class="v16-callout"><strong>WE ARE HERE:</strong> September 2026 - SOFT development then data collection. *SOLAR, BRAUD and BRAUDOLF: July-December 2027 only if feasible. Main thesis writing: March-October 2028 - target submission October 2028 - target defense December 2028, about two months after submission.</div>'''})

# 60 - Reuse the saved 3-card summary for the requested dissemination calendar.
set_lang(60,
 {'section':'Calendrier','kicker':'Valorisation et médiation','title':'Communications envisagées','lead':'La valorisation accompagne les collectes, avec une distinction explicite entre communication scientifique, médiation et événements conditionnels.',
  'content':'''<div class="v16-summary"><article><h3>2026</h3><p><strong>JDD 2026</strong> - réalisé. <strong>Nuit des Chercheurs 2026</strong> - valorisation / médiation scientifique.</p></article><article><h3>2027</h3><p><strong>Forum des Jeunes Chercheurs</strong> - <strong>JDD</strong> - <strong>ECRO</strong> - <strong>GDR O3</strong>. <strong>Expérimentarium 2027</strong> est identifié comme une action de médiation scientifique.</p></article><article><h3>2028</h3><p><strong>FJC</strong> - <strong>JDD</strong> - <strong>ISOT 2028</strong> uniquement si le financement et l’avancement du projet le permettent.</p></article></div>'''},
 {'section':'Timeline','kicker':'Dissemination and outreach','title':'Planned communications','lead':'Dissemination accompanies data collection, with an explicit distinction between scientific communication, outreach and conditional events.',
  'content':'''<div class="v16-summary"><article><h3>2026</h3><p><strong>JDD 2026</strong> - completed. <strong>Researchers’ Night 2026</strong> - scientific outreach.</p></article><article><h3>2027</h3><p><strong>Young Researchers Forum</strong> - <strong>JDD</strong> - <strong>ECRO</strong> - <strong>GDR O3</strong>. <strong>Expérimentarium 2027</strong> is explicitly an outreach activity.</p></article><article><h3>2028</h3><p><strong>FJC</strong> - <strong>JDD</strong> - <strong>ISOT 2028</strong> only if funding and project progress allow.</p></article></div>'''})

# 61 - Discuss only active extensions and three-paper strategy.
set_lang(61,
 {'content':'''<div class="v16-decisions"><article><b>1</b><h3>SOFT</h3><p>Durée maximale, EEG / physiologie et critères de simplification si nécessaire.</p></article><article><b>2</b><h3>Ordre des collectes</h3><p>Valider SOFT -> OASIS -> TWIXOLF et le niveau de chevauchement analyse / collecte.</p></article><article><b>3</b><h3>Extensions</h3><p>Définir les critères de lancement de SOLAR, BRAUD et BRAUDOLF.</p></article><article><b>4</b><h3>Publications</h3><p>Arbitrer la stratégie en trois articles : TWIXAV + TWIXOLF, VIBEX + OASIS, puis SOFT.</p></article><article><b>5</b><h3>Matériel</h3><p>Sécuriser le PC expérimental, les solutions de secours et les configurations stables.</p></article><article><b>6</b><h3>Charge doctorale</h3><p>Maintenir un calendrier soutenable entre recherche, enseignement, formation et diffusion.</p></article></div>'''},
 {'content':'''<div class="v16-decisions"><article><b>1</b><h3>SOFT</h3><p>Maximum duration, EEG / physiology and simplification criteria if needed.</p></article><article><b>2</b><h3>Collection order</h3><p>Validate SOFT -> OASIS -> TWIXOLF and the level of overlap between analysis and collection.</p></article><article><b>3</b><h3>Extensions</h3><p>Define launch criteria for SOLAR, BRAUD and BRAUDOLF.</p></article><article><b>4</b><h3>Publications</h3><p>Discuss the three-paper strategy: TWIXAV + TWIXOLF, VIBEX + OASIS, then SOFT.</p></article><article><b>5</b><h3>Equipment</h3><p>Secure the experimental PC, backup solutions and stable configurations.</p></article><article><b>6</b><h3>Doctoral workload</h3><p>Maintain a sustainable schedule across research, teaching, training and dissemination.</p></article></div>'''})

# 62 - Bibliography: append the four requested sources to the existing bibliography DA.
refs_fr='''<p>Occelli, V., et al. (2023). <em>Is Sight for Space and Sound for Time? Different Asymmetry of Spatiotemporal Interferences in Vision and Audition.</em> SSRN. https://doi.org/10.2139/ssrn.4524392</p><p>Capizzi, M., Chica, A. B., Lupiáñez, J., & Charras, P. (2023). Attention to space and time: Independent or interactive systems? A narrative review. <em>Psychonomic Bulletin & Review, 30</em>, 2030-2048.</p><p>Di Stefano, N., & Spence, C. (2025). Perceiving temporal structure within and between the senses: A multisensory/crossmodal perspective. <em>Attention, Perception, & Psychophysics, 87</em>, 1811-1838.</p><p>Ampollini, S., Ardizzi, M., Ferroni, F., & Cigala, A. (2024). Synchrony perception across senses: A systematic review of temporal binding window changes from infancy to adolescence. <em>Neuroscience & Biobehavioral Reviews, 162</em>, 105711.</p>'''
for key in ['_fr','_en']:
    h=slides[61].get(key) or {}
    c=h.get('content','')
    if 'Occelli' not in c:
        c=c.replace('</div>',refs_fr+'</div>',1)
    h['content']=c; slides[61][key]=h
slides[61].update(slides[61].get('_fr') or {})

# 53 and 55 become hidden deferred-study appendices, not part of the main narrative.
for idx in [53,55]:
    s=slides[idx-1]
    s['appendix']=True; s['chapter']='Annexes'
    for key,is_en in [('_fr',False),('_en',True)]:
        h=s.get(key) or {}
        h['section']='Appendices' if is_en else 'Annexes'
        h['kicker']='Deferred study' if is_en else 'Étude différée'
        h['notes']='Kept as a hidden appendix for committee questions.' if is_en else 'Conservée en annexe masquée pour les questions du comité.'
        s[key]=h
    s.update(s.get('_fr') or {})

# Apply the user's simple-hyphen preference to slide text only.
for s in slides:
    for h in [s,s.get('_fr') or {},s.get('_en') or {}]:
        for k in ['title','lead','content','notes','kicker','section']:
            if isinstance(h.get(k),str):
                h[k]=h[k].replace('—','-').replace('–','-')
    if s.get('_fr'): s.update(s['_fr'])

# Reorder so all 60 main slides precede the four hidden appendices. This changes no styling.
main=[]; deferred=[]; bibliography=[]
for i,s in enumerate(slides,1):
    if i in (53,55): deferred.append(s)
    elif i in (62,63): bibliography.append(s)
    elif not s.get('appendix'): main.append(s)
    else: bibliography.append(s)
# Saved thanks slide is a main slide and remains last in main through original order.
slides=main+deferred+bibliography

if len(slides)!=64 or sum(not s.get('appendix') for s in slides)!=60 or sum(bool(s.get('appendix')) for s in slides)!=4:
    raise RuntimeError('Unexpected main/appendix counts')
if not all(not s.get('appendix') for s in slides[:60]) or not all(s.get('appendix') for s in slides[60:]):
    raise RuntimeError('Appendices are not grouped at the end')

newjson=json.dumps(slides,ensure_ascii=False,separators=(',',':'))
text=source[:st]+newjson+source[en:]

# Manual VIBEX demo: modify behavior only, using the EXISTING demo markup classes and CSS.
# No new CSS or design component is introduced.
pat=re.compile(r'function vibexMarkup\(\)\{.*?function wireVibex\(\)\{.*?\}\n',re.S)
manual=r'''function vibexMarkup(){const E=en();return `<div class="demo-head"><div><span class="demo-acronym">VIBEX</span><h2 id="studyDemoTitle">${E?'Visual Boundary Extension trial':'Essai de Boundary Extension visuelle'}</h2><p>${E?'Use Next to inspect each step of the saved experimental sequence.':'Utilisez Suivant pour parcourir manuellement chaque étape de la séquence expérimentale.'}</p></div></div><div class="demo-meta"><span>Fixation 300 ms</span><span>Image 1 - 200 ms</span><span>${E?'Mask - 1000 ms':'Masque - 1000 ms'}</span><span>Image 2 - 200 ms</span></div><div class="demo-workspace"><div><div class="demo-screen"><div class="demo-status"><span id="vibReady">${E?'Ready':'Prêt'}</span><span id="vibEventStatus"></span></div><div class="demo-stage" id="vibStage"><div style="font-weight:900">${E?'Click Next to begin':'Cliquez sur Suivant pour commencer'}</div></div></div><div class="demo-progress"><i id="vibProgress"></i></div></div><aside class="demo-side"><div class="demo-side-card"><b>${E?'Four framing conditions':'Quatre conditions de cadrage'}</b><p>LL - SS - LS - SL</p></div><div class="demo-side-card"><b>${E?'Three image sizes':'Trois tailles d’image'}</b><p>${E?'Small - medium - large':'Petite - moyenne - grande'}</p></div><div class="demo-response"><button class="demo-primary" id="vibNext" data-vibex-next>${E?'Next':'Suivant'}</button><button class="secondary" id="vibReset" data-vibex-reset>${E?'Restart':'Recommencer'}</button></div></aside></div>`}
  const vibImage=(src,alt)=>`<div class="vibex-frame"><img src="${src}" alt="${alt}"></div>`;
  function wireVibex(){let step=-1;const stage=document.getElementById('vibStage'),status=document.getElementById('vibEventStatus'),progress=document.getElementById('vibProgress'),E=en();const paint=()=>{if(step<0){stage.innerHTML=`<div style="font-weight:900">${E?'Click Next to begin':'Cliquez sur Suivant pour commencer'}</div>`;status.textContent='';progress.style.width='0%';return}if(step===0){stage.innerHTML='<div class="demo-fix">+</div>';status.textContent='Fixation - 300 ms';progress.style.width='15%';return}if(step===1){stage.innerHTML=vibImage('assets/demo/image_S_16.jpg',E?'Image S 16 - close framing':'image_S_16 - cadrage serré');status.textContent='Image 1 - 200 ms';progress.style.width='35%';return}if(step===2){stage.innerHTML=vibImage('assets/demo/Masque_SCR.webp',E?'Visual noise mask':'Masque visuel');status.textContent=E?'Mask - 1000 ms':'Masque - 1000 ms';progress.style.width='60%';return}if(step===3){stage.innerHTML=vibImage('assets/demo/image_L_16.jpg',E?'Image L 16 - wide framing':'image_L_16 - cadrage large');status.textContent='Image 2 - 200 ms';progress.style.width='82%';return}stage.innerHTML=`<div class="demo-response"><button data-vib-answer="same">${E?'Identical':'Identique'}</button><button class="secondary" data-vib-answer="different">${E?'Different':'Différent'}</button></div>`;status.textContent=E?'Framing judgment':'Jugement du cadrage';progress.style.width='100%'};document.getElementById('vibNext')?.addEventListener('click',()=>{step=Math.min(4,step+1);paint()});document.getElementById('vibReset')?.addEventListener('click',()=>{step=-1;paint()});stage?.addEventListener('click',x=>{if(x.target.closest('[data-vib-answer]')){stage.innerHTML=`<div style="font-weight:900">${E?'Response recorded':'Réponse enregistrée'}</div>`;status.textContent=E?'Trial complete':'Essai terminé'}});paint()}
'''
text,n=pat.subn(manual,text,1)
if n!=1:
    raise RuntimeError('Could not replace saved VIBEX demo runtime')

# Repair the saved apparatus script's literal newline escapes only; this is a runtime fix, not a DA change.
am=re.search(r'(<script id="apparatusPopupScript">)(.*?)(</script>)',text,re.S)
if am:
    body=am.group(2).replace('\\n','\n')
    text=text[:am.start()]+am.group(1)+body+am.group(3)+text[am.end():]

# Hard guarantee: CSS/DA must be byte-identical to the saved version.
styles_saved=re.findall(r'<style(?:\s[^>]*)?>.*?</style>',source,re.S|re.I)
styles_new=re.findall(r'<style(?:\s[^>]*)?>.*?</style>',text,re.S|re.I)
if styles_saved!=styles_new:
    raise RuntimeError('Visual DA/CSS changed')

# Requested invariants.
for q in ['Maître de conférences HDR','assets/logos/logo_docc.png','Occelli et al., 2023','Capizzi et al., 2023','Di Stefano & Spence, 2025','Ampollini et al., 2024','Less space, less time',AX1_FR,AX2_FR,'Rekow et al. (2022)','Baccarani & Brochard (2024)','mouvement oculaire maîtrisé','data-vibex-next','Expérimentarium 2027','ISOT 2028','NOUS SOMMES ICI','mars-octobre 2028','octobre 2028','décembre 2028']:
    if q not in text:
        raise RuntimeError(f'Missing requested content: {q}')
if 'À consolider' in ' '.join(s.get('content','') for s in slides[:60]):
    raise RuntimeError('Obsolete TWIXAV consolidation remains')
# F-values removed specifically from the fused TWIXAV result slide.
tw=[s for s in slides[:60] if s.get('study')=='TWIXAV' and 'Temporal Binding Window dépend' in s.get('title','')]
if len(tw)!=1 or 'F(' in tw[0].get('content',''):
    raise RuntimeError('TWIXAV fused result check failed')
if any('SORBET' in (s.get('title','')+' '+s.get('content','')) or 'COBEX' in (s.get('title','')+' '+s.get('content','')) for s in slides[:60]):
    raise RuntimeError('Deferred studies remain in main path')
if not any(s.get('study')=='SOLAR' and ('Axe 1' in (s.get('kicker','')+s.get('content',''))) for s in slides[:60]):
    raise RuntimeError('SOLAR not moved to Axis 1')

OUT.write_text(text,encoding='utf-8')
print('CONTENT_ONLY_REAPPLY_OK')
print('Slides',len(slides),'main',sum(not s.get('appendix') for s in slides),'appendix',sum(bool(s.get('appendix')) for s in slides))
print('Backup SHA256',hashlib.sha256(BACKUP.read_bytes()).hexdigest())
print('CSS blocks unchanged',len(styles_new))
