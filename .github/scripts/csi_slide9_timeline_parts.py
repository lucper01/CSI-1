from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

# Slide 9 - replace the idea of constraints/abolition with specificities/prevention.
fr_old_lead = "Sela et Sobel (2010) décrivent une modalité dont les contraintes spatiales et temporelles diffèrent fortement de celles de la vision et de l’audition. La thèse transforme cette opposition en question expérimentale."
fr_new_lead = "Sela et Sobel (2010) décrivent une modalité présentant des spécificités spatiales et temporelles qui la distinguent fortement de la vision et de l’audition. La thèse transforme cette opposition en question expérimentale."
fr_old_question = "Ces contraintes abolissent-elles la structuration spatio-temporelle, ou modifient-elles surtout la manière dont elle devient disponible à la perception et à l’attention ?"
fr_new_question = "Ces spécificités empêchent-elles la structuration spatio-temporelle, ou modifient-elles surtout la manière dont elle devient disponible à la perception et à l’attention ?"

en_old_lead = "Sela and Sobel (2010) describe a modality whose spatial and temporal constraints differ markedly from those of vision and audition. The thesis turns this asymmetry into an experimental question."
en_new_lead = "Sela and Sobel (2010) describe a modality with distinctive spatial and temporal specificities that set it apart from vision and audition. The thesis turns this opposition into an experimental question."
en_old_question = "Do these constraints abolish spatio-temporal organization, or do they change how it becomes available to perception and attention?"
en_new_question = "Do these specificities prevent spatio-temporal organization, or do they mainly change how it becomes available to perception and attention?"

pairs = [
    (fr_old_lead, fr_new_lead),
    (fr_old_question, fr_new_question),
    (en_old_lead, en_new_lead),
    ("The constraint to test", "The specificity to test"),
    (en_old_question, en_new_question),
]
for old, new in pairs:
    count = text.count(old)
    if count:
        text = text.replace(old, new)
        print(f'Replaced {count} occurrence(s): {old[:72]}')
    elif new in text:
        print(f'Already updated: {new[:72]}')
    else:
        raise SystemExit(f'Could not locate expected slide 9 wording: {old}')

# Footer timeline - use the six actual PARTIE divider slides as the source of truth.
marker = '// CSI_LOCAL_PART_TIMELINE'
render_sig = 'function renderPartTimeline(index){'
start = text.find(marker)
end = text.find(render_sig, start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate existing part timeline block')

new_func = """// CSI_LOCAL_PART_TIMELINE
function partTimelineFor(index){
  const E=document.documentElement.lang==='en';
  const steps=E
    ? ['CONTEXT','ARCHITECTURE','YEAR 1','YEAR 2','YEAR 3','PLANNING']
    : ['CONTEXTE','ARCHITECTURE','ANNÉE 1','ANNÉE 2','ANNÉE 3','PLANIFICATION'];
  const starts=[];
  slides.forEach((s,i)=>{
    const localized=E?(s._en&&s._en.content):(s._fr&&s._fr.content);
    const source=String(localized||s.content||'');
    const m=source.match(/section-divider-number[^>]*>(?:PARTIE|PART)\\s+([1-6])</i);
    if(m) starts[Number(m[1])-1]=i;
  });
  let active=0;
  for(let j=0;j<steps.length;j++){
    if(Number.isInteger(starts[j]) && index>=starts[j]) active=j;
  }
  return {steps,active};
}
"""
text = text[:start] + new_func + text[end:]

if 'Ces contraintes abolissent-elles' in text:
    raise SystemExit('Old French wording still present')
if 'Ces spécificités empêchent-elles' not in text:
    raise SystemExit('New French wording missing')
if "['CONTEXTE','ARCHITECTURE','ANNÉE 1','ANNÉE 2','ANNÉE 3','PLANIFICATION']" not in text:
    raise SystemExit('Six-part French timeline missing')
if text.count('section-divider-number') < 6:
    raise SystemExit('Expected at least six section divider markers')

path.write_text(text, encoding='utf-8')
print('Slide 9 and six-part footer timeline updated.')
