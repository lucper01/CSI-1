from pathlib import Path
import json

path=Path('index.html')
text=path.read_text(encoding='utf-8')
marker='const slides = ['
mi=text.find(marker)
if mi<0:
    raise SystemExit('slides array marker not found')
arr_start=mi+len(marker)

# Locate closing ] of slides array while respecting strings and nesting.
in_str=False
esc=False
depth_obj=0
depth_arr=0
end=None
for i,ch in enumerate(text[arr_start:], start=arr_start):
    if in_str:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch=='"': in_str=False
        continue
    if ch=='"': in_str=True; continue
    if ch=='{': depth_obj+=1
    elif ch=='}': depth_obj-=1
    elif ch=='[': depth_arr+=1
    elif ch==']':
        if depth_obj==0 and depth_arr==0:
            end=i
            break
        depth_arr-=1
if end is None:
    raise SystemExit('slides array closing bracket not found')

content=text[arr_start:end]
# Extract exact top-level object strings.
objs=[]
in_str=False; esc=False; depth=0; start=None
for i,ch in enumerate(content):
    if in_str:
        if esc: esc=False
        elif ch=='\\': esc=True
        elif ch=='"': in_str=False
        continue
    if ch=='"': in_str=True; continue
    if ch=='{':
        if depth==0: start=i
        depth+=1
    elif ch=='}':
        depth-=1
        if depth==0 and start is not None:
            objs.append(content[start:i+1])
            start=None
if len(objs)<26:
    raise SystemExit(f'Only {len(objs)} slides found')

parsed=[json.loads(o) for o in objs]
before=[parsed[i].get('title','') for i in (23,24,25)]
moved_obj=objs.pop(23)
moved_parsed=parsed.pop(23)
objs.insert(24,moved_obj)
parsed.insert(24,moved_parsed)

after=[parsed[i].get('title','') for i in (23,24,25)]
if after[0] != before[1] or after[1] != before[0] or after[2] != before[2]:
    raise SystemExit(f'Unexpected order after move: before={before!r} after={after!r}')

# Rebuild only the array body, keeping slide objects byte-for-byte.
new_content='\n  '+',\n  '.join(objs)+'\n'
new_text=text[:arr_start]+new_content+text[end:]
path.write_text(new_text, encoding='utf-8')
print('Moved old slide 24 between old slides 25 and 26')
print('Before:', before)
print('After :', after)
