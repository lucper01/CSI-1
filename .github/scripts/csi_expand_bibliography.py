from pathlib import Path
import json
import hashlib

p = Path('index.html')
save = Path('index_save.html')
before_save = hashlib.sha256(save.read_bytes()).hexdigest()
text = p.read_text(encoding='utf-8')

marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

def bib(items):
    return '<div class="v16-biblio dense-biblio">' + ''.join(f'<p>{x}</p>' for x in items) + '</div>'

axis1 = [
    'Occelli, V., et al. (2023). Is Sight for Space and Sound for Time? Different Asymmetry of Spatiotemporal Interferences in Vision and Audition. <em>SSRN Electronic Journal</em>.',
    'Capizzi, M., Chica, A. B., Lupiáñez, J., & Charras, P. (2023). Attention to space and time: Independent or interactive systems? A narrative review. <em>Psychonomic Bulletin & Review, 30</em>, 2030-2048.',
    'Di Stefano, N., & Spence, C. (2025). Perceiving temporal structure within and between the senses: A multisensory/crossmodal perspective. <em>Attention, Perception, & Psychophysics, 87</em>, 1811-1838.',
    'Ampollini, S., Ardizzi, M., Ferroni, F., & Cigala, A. (2024). Synchrony perception across senses: A systematic review of temporal binding window changes from infancy to adolescence. <em>Neuroscience & Biobehavioral Reviews, 162</em>, 105711.',
    'Stein, B. E., & Stanford, T. R. (2008). Multisensory integration: Current issues from the perspective of the single neuron. <em>Nature Reviews Neuroscience, 9</em>, 255-266.',
    'Vroomen, J., & Keetels, M. (2010). Perception of intersensory synchrony: A tutorial review. <em>Attention, Perception, & Psychophysics, 72</em>, 871-884.',
    'Powers, A. R., Hillock, A. R., & Wallace, M. T. (2009). Perceptual training narrows the temporal window of multisensory binding. <em>Journal of Neuroscience, 29</em>, 12265-12274.',
    'Stevenson, R. A., Zemtsov, R. K., & Wallace, M. T. (2012). Individual differences in the multisensory temporal binding window predict susceptibility to audiovisual illusions. <em>Journal of Experimental Psychology: Human Perception and Performance, 38</em>, 1517-1529.',
    'Körding, K. P., et al. (2007). Causal inference in multisensory perception. <em>PLOS ONE, 2</em>, e943.',
    'Gotow, N., & Kobayakawa, T. (2017). Simultaneity judgment using olfactory-visual, visual-gustatory, and olfactory-gustatory combinations. <em>PLOS ONE, 12</em>, e0174958.',
    'Mainland, J., & Sobel, N. (2006). The sniff is part of the olfactory percept. <em>Chemical Senses, 31</em>, 181-196.',
    'Sela, L., & Sobel, N. (2010). Human olfaction: A constant state of change-blindness. <em>Experimental Brain Research, 205</em>, 13-29.',
    'Sobel, N., et al. (1998). Sniffing and smelling: Separate subsystems in the human olfactory cortex. <em>Nature, 392</em>, 282-286.',
    'Kepecs, A., Uchida, N., & Mainen, Z. F. (2006). The sniff as a unit of olfactory processing. <em>Chemical Senses, 31</em>, 167-179.',
    'Uchida, N., Kepecs, A., & Mainen, Z. F. (2006). Seeing at a glance, smelling in a whiff: Rapid forms of perceptual decision making. <em>Nature Reviews Neuroscience, 7</em>, 485-491.',
    'Zhou, G., et al. (2019). Human olfactory-auditory integration requires phase synchrony between sensory cortices. <em>Nature Communications, 10</em>, 1168.',
    'Crisinel, A.-S., & Spence, C. (2012). A fruity note: Crossmodal associations between odors and musical notes. <em>Chemical Senses, 37</em>, 151-158.',
    'Baccarani, A., & Brochard, R. (2024). Relaxing and stimulating ambient odors influence preferences for musical tempo. <em>Musicae Scientiae, 28</em>, 273-286.'
]

axis2 = [
    'Intraub, H., & Richardson, M. (1989). Wide-angle memories of close-up scenes. <em>Journal of Experimental Psychology: Learning, Memory, and Cognition, 15</em>, 179-187.',
    'Intraub, H. (2012). Rethinking visual scene perception. <em>WIREs Cognitive Science, 3</em>, 117-127.',
    'Bainbridge, W. A., & Baker, C. I. (2020). Boundaries extend and contract in scene memory depending on image properties. <em>Current Biology, 30</em>, 537-543.e3.',
    'Park, J., Josephs, E., & Konkle, T. (2024). Systematic transition from boundary extension to contraction along an object-to-scene continuum. <em>Journal of Vision, 24</em>, 9.',
    'Rekow, D., Baudouin, J.-Y., Durand, K., & Leleu, A. (2022). Smell what you hardly see: Odors assist visual categorization in the human brain. <em>NeuroImage, 255</em>, 119181.',
    'Hörberg, T., et al. (2020). Olfactory influences on visual categorization: Behavioral and ERP evidence. <em>Cerebral Cortex, 30</em>, 4220-4237.',
    'Seo, H.-S., Roidl, E., Müller, F., & Negoias, S. (2010). Odors enhance visual attention to congruent objects. <em>Appetite, 54</em>, 544-549.',
    'Zhou, W., Jiang, Y., He, S., & Chen, D. (2010). Olfaction modulates visual perception in binocular rivalry. <em>Current Biology, 20</em>, 1356-1358.',
    'Gottfried, J. A., & Dolan, R. J. (2003). The nose smells what the eye sees: Crossmodal visual facilitation of human olfactory perception. <em>Neuron, 39</em>, 375-386.',
    'Gottfried, J. A. (2010). Central mechanisms of odour object perception. <em>Nature Reviews Neuroscience, 11</em>, 628-641.',
    'Porter, J., et al. (2007). Mechanisms of scent-tracking in humans. <em>Nature Neuroscience, 10</em>, 27-29.',
    'Middlebrooks, J. C., & Green, D. M. (1991). Sound localization by human listeners. <em>Annual Review of Psychology, 42</em>, 135-159.',
    'Crisinel, A.-S., & Spence, C. (2012). A fruity note: Crossmodal associations between odors and musical notes. <em>Chemical Senses, 37</em>, 151-158.',
    'Zhou, G., et al. (2019). Human olfactory-auditory integration requires phase synchrony between sensory cortices. <em>Nature Communications, 10</em>, 1168.',
    'Baccarani, A., & Brochard, R. (2024). Relaxing and stimulating ambient odors influence preferences for musical tempo. <em>Musicae Scientiae, 28</em>, 273-286.'
]

found1 = found2 = False
for s in slides:
    if not s.get('appendix'):
        continue
    if s.get('_fr', {}).get('title') == 'Axe 1 - temps et multisensorialité':
        fr = bib(axis1)
        s['_fr']['lead'] = 'Références citées ou mobilisées dans la présentation.'
        s['_fr']['content'] = fr
        s['_en']['lead'] = 'References cited or mobilized throughout the presentation.'
        s['_en']['content'] = fr
        s['lead'] = s['_fr']['lead']
        s['content'] = fr
        found1 = True
    if s.get('_fr', {}).get('title') == 'Axe 2 - espace et scènes':
        fr = bib(axis2)
        s['_fr']['lead'] = 'Références citées ou mobilisées dans la présentation.'
        s['_fr']['content'] = fr
        s['_en']['lead'] = 'References cited or mobilized throughout the presentation.'
        s['_en']['content'] = fr
        s['lead'] = s['_fr']['lead']
        s['content'] = fr
        found2 = True

assert found1 and found2
new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

css = '''
/* CSI_DENSE_BIBLIO */
.v16-biblio.dense-biblio { gap: 7px !important; }
.v16-biblio.dense-biblio p {
  padding: 8px 10px !important;
  border-radius: 13px !important;
  font-size: .68rem !important;
  line-height: 1.28 !important;
}
@media (max-width: 1050px) {
  .v16-biblio.dense-biblio p { font-size: .64rem !important; }
}
'''
if 'CSI_DENSE_BIBLIO' not in text:
    pos = text.rfind('</style>')
    assert pos != -1
    text = text[:pos] + css + text[pos:]

p.write_text(text, encoding='utf-8')
out = p.read_text(encoding='utf-8')
assert 'Occelli, V., et al. (2023)' in out
assert 'Di Stefano, N., & Spence, C. (2025)' in out
assert 'Ampollini, S., Ardizzi, M., Ferroni, F., & Cigala, A. (2024)' in out
assert 'Rekow, D., Baudouin, J.-Y., Durand, K., & Leleu, A. (2022)' in out
assert 'CSI_DENSE_BIBLIO' in out
assert hashlib.sha256(save.read_bytes()).hexdigest() == before_save
