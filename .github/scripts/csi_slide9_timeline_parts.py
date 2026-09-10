from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

replacements = {
    "Sela et Sobel (2010) décrivent une modalité dont les contraintes spatiales et temporelles diffèrent fortement de celles de la vision et de l’audition. La thèse transforme cette opposition en question expérimentale.":
    "Sela et Sobel (2010) décrivent une modalité présentant des spécificités spatiales et temporelles qui la distinguent fortement de la vision et de l’audition. La thèse transforme cette opposition en question expérimentale.",
    "Ces contraintes abolissent-elles la structuration spatio-temporelle, ou modifient-elles surtout la manière dont elle devient disponible à la perception et à l’attention ?":
    "Ces spécificités empêchent-elles la structuration spatio-temporelle, ou modifient-elles surtout la manière dont elle devient disponible à la perception et à l’attention ?",
    "Sela and Sobel (2010) describe a modality whose spatial and temporal constraints differ markedly from those of vision and audition. The thesis turns this asymmetry into an experimental question.":
    "Sela and Sobel (2010) describe a modality with distinctive spatial and temporal specificities that set it apart from vision and audition. The thesis turns this opposition into an experimental question.",
    "The constraint to test": "The specificity to test",
    "Do these constraints abolish spatio-temporal organization, or do they change how it becomes available to perception and attention?":
    "Do these specificities prevent spatio-temporal organization, or do they mainly change how it becomes available to perception and attention?",
}

for old, new in replacements.items():
    count = text.count(old)
    if count == 0:
        raise SystemExit(f'Missing expected slide 9 text: {old}')
    text = text.replace(old, new)
    print(f'Replaced {count} occurrence(s): {old[:70]}')

pattern = re.compile(
    r"// CSI_LOCAL_PART_TIMELINE\s*function partTimelineFor\(index\)\{.*?\n\}\nfunction renderPartTimeline\(index\)\{",
    re.S,
)
new_timeline = r'''// CSI_LOCAL_PART_TIMELINE
function partTimelineFor(index){
  const E=document.documentElement.lang==='en';
  const steps=E
    ? ['CONTEXT','ARCHITECTURE','YEAR 1','YEAR 2','YEAR 3','PLANNING']
    : ['CONTEXTE','ARCHITECTURE','ANNÉE 1','ANNÉE 2','ANNÉE 3','PLANIFICATION'];
  const starts=[];
  slides.forEach((s,i)=>{
    const localized=E?(s._en&&s._en.content):(s._fr&&s._fr.content);
    const source=String(localized||s.content||'');
    const m=source.match(/section-divider-number[^>]*>(?:PARTIE|PART)\s+([1-6])</i);
    if(m) starts[Number(m[1])-1]=i;
  });
  let active=0;
  for(let j=0;j<steps.length;j++){
    if(Number.isInteger(starts[j]) && index>=starts[j]) active=j;
  }
  return {steps,active};
}
function renderPartTimeline(index){'''
text, count = pattern.subn(new_timeline, text, count=1)
if count != 1:
    raise SystemExit(f'Expected one partTimelineFor block, found {count}')

# Core validation of requested semantics.
assert 'Ces contraintes abolissent-elles' not in text
assert 'Ces spécificités empêchent-elles' in text
assert "['CONTEXTE','ARCHITECTURE','ANNÉE 1','ANNÉE 2','ANNÉE 3','PLANIFICATION']" in text

path.write_text(text, encoding='utf-8')
print('Slide 9 and six-part footer timeline updated.')
