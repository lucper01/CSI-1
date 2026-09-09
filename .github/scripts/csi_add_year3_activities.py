from pathlib import Path
import json
import re
import hashlib

index = Path('index.html')
save = Path('index_save.html')
save_before = hashlib.sha256(save.read_bytes()).hexdigest()
text = index.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
slides, rel_end = json.JSONDecoder().raw_decode(text[start:])
end = start + rel_end

# Insert one first Year 3 slide immediately after the current Year 2 activities slide.
if not any(s.get('title') == 'Activités doctorales prévues - 2027-2028' for s in slides):
    matches = [i for i, s in enumerate(slides) if s.get('title') == 'Activités doctorales prévues - 2026-2027']
    assert len(matches) == 1, [slides[i].get('title') for i in matches]
    insert_at = matches[0] + 1

    fr_content = (
        '<div class="v16-activity">'
        '<article><b>À confirmer</b><h3>Enseignement</h3>'
        '<p>Volume à confirmer, avec une préférence pour des enseignements en statistiques si cela peut être intégré à la charge pédagogique.</p></article>'
        '<article><b>DocAdoct</b><h3>Formation doctorale</h3>'
        '<p>Dernière formation de fin de thèse, d’environ 1 h 45 à 2 h, consacrée à la préparation de la soutenance, au dépôt légal et à la diffusion de la thèse.</p>'
        '<small>Démarches administratives - plagiat - droit d’auteur - propriété intellectuelle - archivage - obligations juridiques.</small></article>'
        '<article><b>1 M1 ?</b><h3>Encadrement</h3>'
        '<p>Encadrement probable d’un seul mémoire de Master 1, afin de ne pas surcharger l’année et de soutenir les passations des extensions possibles.</p>'
        '<div class="v16-tool-pills"><span>SOLAR</span><span>BRAUD</span><span>BRAUDOLF</span></div></article>'
        '<article class="tools"><b>3 communications envisagées</b><h3>Communications scientifiques</h3>'
        '<div class="v16-tool-pills"><span>FJC 2028</span><span>JDD 2028</span><span>ISOT 2028 si financement</span></div></article>'
        '</div>'
    )
    en_content = (
        '<div class="v16-activity">'
        '<article><b>To be confirmed</b><h3>Teaching</h3>'
        '<p>Teaching volume to be confirmed, with a preference for statistics courses if this can be integrated into the teaching load.</p></article>'
        '<article><b>DocAdoct</b><h3>Doctoral training</h3>'
        '<p>Final thesis-stage training session, approximately 1 h 45 to 2 h, focused on preparing the defense, legal deposit and thesis dissemination.</p>'
        '<small>Administrative steps - plagiarism - copyright - intellectual property - archiving - legal obligations.</small></article>'
        '<article><b>1 M1?</b><h3>Supervision</h3>'
        '<p>Probably one Master 1 thesis supervision, to avoid overloading the year and to support data collection for possible extensions.</p>'
        '<div class="v16-tool-pills"><span>SOLAR</span><span>BRAUD</span><span>BRAUDOLF</span></div></article>'
        '<article class="tools"><b>3 planned talks</b><h3>Scientific communications</h3>'
        '<div class="v16-tool-pills"><span>FJC 2028</span><span>JDD 2028</span><span>ISOT 2028 if funded</span></div></article>'
        '</div>'
    )

    slide = {
        'chapter': 'Troisième année',
        'study': '',
        'appendix': False,
        '_fr': {
            'section': 'Troisième année',
            'kicker': 'Activités doctorales à venir',
            'title': 'Activités doctorales prévues - 2027-2028',
            'lead': 'La troisième année sera centrée sur la finalisation expérimentale, la valorisation scientifique et la préparation de la fin de thèse.',
            'content': fr_content,
            'notes': 'Présenter cette diapositive comme une première projection, avec plusieurs éléments encore à confirmer.'
        },
        '_en': {
            'section': 'Year 3',
            'kicker': 'Upcoming doctoral activities',
            'title': 'Planned doctoral activities - 2027-2028',
            'lead': 'Year 3 will focus on experimental completion, scientific dissemination and preparation for the end of the PhD.',
            'content': en_content,
            'notes': 'Present this slide as an initial projection, with several elements still to be confirmed.'
        },
        'section': 'Troisième année',
        'kicker': 'Activités doctorales à venir',
        'title': 'Activités doctorales prévues - 2027-2028',
        'lead': 'La troisième année sera centrée sur la finalisation expérimentale, la valorisation scientifique et la préparation de la fin de thèse.',
        'content': fr_content,
        'notes': 'Présenter cette diapositive comme une première projection, avec plusieurs éléments encore à confirmer.'
    }
    slides.insert(insert_at, slide)

new_json = json.dumps(slides, ensure_ascii=False, separators=(',', ':'))
text = text[:start] + new_json + text[end:]

# Shift the local part timeline after insertion and add a small Year 3 local marker.
fn_start = text.index('function partTimelineFor(index){')
fn_end = text.index('\nfunction renderPartTimeline', fn_start)
fn = text[fn_start:fn_end]

old_year2 = """if(n>=34&&n<=43){\n    const steps=E\n      ? ['PRIORITIES','SOFT','OASIS','TWIXOLF','ACTIVITIES','PUBLICATIONS']\n      : ['PRIORITÉS','SOFT','OASIS','TWIXOLF','ACTIVITÉS','PUBLICATIONS'];\n    let active=0;\n    if(n>=36&&n<=37) active=1;\n    else if(n>=38&&n<=39) active=2;\n    else if(n>=40&&n<=41) active=3;\n    else if(n===42) active=4;\n    else if(n===43) active=5;\n    return {steps,active};\n  }"""
new_year2 = """if((n>=34&&n<=42)||n===44){\n    const steps=E\n      ? ['PRIORITIES','SOFT','OASIS','TWIXOLF','ACTIVITIES','PUBLICATIONS']\n      : ['PRIORITÉS','SOFT','OASIS','TWIXOLF','ACTIVITÉS','PUBLICATIONS'];\n    let active=0;\n    if(n>=36&&n<=37) active=1;\n    else if(n>=38&&n<=39) active=2;\n    else if(n>=40&&n<=41) active=3;\n    else if(n===42) active=4;\n    else if(n===44) active=5;\n    return {steps,active};\n  }\n  if(n===43){\n    return {steps:E?['YEAR 3']:['ANNÉE 3'],active:0};\n  }"""
assert old_year2 in fn or new_year2 in fn
fn = fn.replace(old_year2, new_year2)

old_ext = """if(n>=44&&n<=50){\n    const steps=E\n      ? ['OVERVIEW','SORBET','SOLAR','COBEX','BRAUD','BRAUDOLF']\n      : ['VUE D\\'ENSEMBLE','SORBET','SOLAR','COBEX','BRAUD','BRAUDOLF'];\n    const active=n<=45?0:n-46;\n    return {steps,active};\n  }"""
new_ext = """if(n>=45&&n<=51){\n    const steps=E\n      ? ['OVERVIEW','SORBET','SOLAR','COBEX','BRAUD','BRAUDOLF']\n      : ['VUE D\\'ENSEMBLE','SORBET','SOLAR','COBEX','BRAUD','BRAUDOLF'];\n    const active=n<=46?0:n-47;\n    return {steps,active};\n  }"""
assert old_ext in fn or new_ext in fn
fn = fn.replace(old_ext, new_ext)
fn = fn.replace('if(n>=51&&n<=53){\n    return {steps:E?[\'GLOBAL\',\'STUDIES\',\'DEFENSE\']:[\'GLOBAL\',\'ÉTUDES\',\'SOUTENANCE\'],active:n-52};\n  }',
                'if(n>=52&&n<=54){\n    return {steps:E?[\'GLOBAL\',\'STUDIES\',\'DEFENSE\']:[\'GLOBAL\',\'ÉTUDES\',\'SOUTENANCE\'],active:n-53};\n  }')
fn = fn.replace('if(n>=54&&n<=56){\n    return {steps:E?[\'SUMMARY\',\'DISCUSSION\',\'THANK YOU\']:[\'BILAN\',\'DISCUSSION\',\'MERCI\'],active:n-55};\n  }',
                'if(n>=55&&n<=57){\n    return {steps:E?[\'SUMMARY\',\'DISCUSSION\',\'THANK YOU\']:[\'BILAN\',\'DISCUSSION\',\'MERCI\'],active:n-56};\n  }')

text = text[:fn_start] + fn + text[fn_end:]

assert 'Activités doctorales prévues - 2027-2028' in text
assert '<b>DocAdoct</b><h3>Formation doctorale</h3>' in text
assert 'statistiques' in text
assert 'FJC 2028' in text and 'JDD 2028' in text and 'ISOT 2028 si financement' in text
assert hashlib.sha256(save.read_bytes()).hexdigest() == save_before

index.write_text(text, encoding='utf-8')
