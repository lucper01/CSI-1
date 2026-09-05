from pathlib import Path
import base64
import gzip
import json
import re
import subprocess

CORE = 'e3ec47385a42f318469eb06f72cf659f07fcdeae'
HIST = '101eac6c39fa9ab1c236b9203e0c77e56eda498c'

CORE_FILES = [
    'csi-v11-core.js',
    'csi-v11-doctoral.js',
    'csi-v11-ui.js',
    'csi-v11-enfix.js',
    'csi-v11-polish.js',
    'csi-v11-clean.js',
    'csi-v12.js',
    'csi-v13.js',
]


def git_show(ref, path):
    return subprocess.check_output(
        ['git', 'show', f'{ref}:{path}'],
        text=True,
        encoding='utf-8',
    )


def js_string(value):
    return (
        json.dumps(value, ensure_ascii=False)
        .replace('</script>', '<\\/script>')
        .replace('</SCRIPT>', '<\\/SCRIPT>')
    )


base_html = git_show(CORE, 'presentation-base.html')
scripts = [git_show(CORE, name) for name in CORE_FILES]
scripts.extend([
    git_show(HIST, 'csi-v14.js'),
    git_show(HIST, 'csi-v15.js'),
])

packed = ''.join(
    Path(f'csi-v16.{i}.b64').read_text(encoding='utf-8').strip()
    for i in range(1, 5)
)
v16 = gzip.decompress(base64.b64decode(packed)).decode('utf-8')
scripts.append(v16)
scripts.append(git_show(HIST, 'csi-v17.js'))
scripts.append(Path('csi-v17-csi1.js').read_text(encoding='utf-8'))

current_shell = Path('presentation.html').read_text(encoding='utf-8')
shell_prefix = current_shell.split('  <script>', 1)[0]
shell_prefix = shell_prefix.replace('CSI-1 - base V17', 'CSI-1 - version autonome')
shell_prefix = shell_prefix.replace(
    'Chargement de la version intermédiaire avec identité visuelle par étude, puis application des corrections CSI.',
    'Chargement de la présentation autonome avec identité visuelle par étude.',
)

match = re.search(
    r'(    function forceFrenchAndCleanHeader\(\)\{.*?)(?=\n    async function start\(\))',
    current_shell,
    flags=re.S,
)
if not match:
    raise RuntimeError('Fonctions d’intégration V17 introuvables.')
integration_functions = match.group(1)

script_literals = ',\n      '.join(js_string(s) for s in scripts)

standalone_script = f'''  <script>
  (()=>{{
    const frame=document.getElementById('presentation'),boot=document.getElementById('boot'),err=document.getElementById('bootError');
{integration_functions}

    const base={js_string(base_html)};
    const bundled=[
      {script_literals}
    ];

    async function start(){{
      try{{
        localStorage.setItem('csi-lang','fr');
        bundled.forEach((code,i)=>{{
          try{{(0,eval)(code+"\\n//# sourceURL=standalone-csi-"+(i+1)+".js")}}
          catch(e){{throw new Error(`script ${{i+1}}: ${{e.message}}`)}}
        }});
        frame.addEventListener('load',()=>{{
          forceFrenchAndCleanHeader();
          const d=frame.contentDocument;
          if(d&&d.body){{
            const observer=new MutationObserver(()=>forceFrenchAndCleanHeader());
            observer.observe(d.body,{{childList:true,subtree:true}});
          }}
          setTimeout(forceFrenchAndCleanHeader,450);
          setTimeout(forceFrenchAndCleanHeader,1000);
          setTimeout(forceFrenchAndCleanHeader,1800);
          setTimeout(integrateProjectSheets,900);
          setTimeout(integrateProjectSheets,1600);
          setTimeout(integrateProjectSheets,2600);
          setTimeout(()=>boot.classList.add('hidden'),900);
        }},{{once:true}});
        frame.srcdoc=base;
      }}catch(e){{
        console.error(e);
        err.style.display='block';
        err.textContent='Impossible de charger la présentation.\\n'+e.message;
        const bar=document.querySelector('.bar');
        if(bar)bar.style.display='none';
      }}
    }}
    start();
  }})();
  </script>
</body>
</html>
'''

Path('index.html').write_text(shell_prefix + standalone_script, encoding='utf-8')

for name in [
    'presentation.html',
    'csi-v17-csi1.js',
    'csi-v16.1.b64',
    'csi-v16.2.b64',
    'csi-v16.3.b64',
    'csi-v16.4.b64',
    'notes.html',
    'questions.html',
]:
    path = Path(name)
    if path.exists():
        path.unlink()

Path('README.md').write_text(
    '# CSI-1 - Luc Perroquin\n\n'
    'Support du premier Comité de Suivi Individuel.\n\n'
    '## Architecture\n\n'
    '- `index.html` contient à lui seul toute la présentation et tout son code.\n'
    '- `affiches/` contient uniquement les fiches projets PDF ouvertes depuis les slides.\n'
    '- `assets/` contient les rares ressources média utilisées par la présentation.\n\n'
    'Il n’existe plus de versions parallèles, de loaders JavaScript, de fragments compressés ou de pages de présentation dupliquées.\n\n'
    'Présentation : https://lucper01.github.io/CSI-1/\n',
    encoding='utf-8',
)
