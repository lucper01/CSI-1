from pathlib import Path
import json

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'const slides = '
start = text.index(marker) + len(marker)
arr, end_rel = json.JSONDecoder().raw_decode(text[start:])

before = [arr[i]['title'] for i in (10,11,12,13)]
slide12 = arr.pop(11)
arr.insert(12, slide12)
after = [arr[i]['title'] for i in (10,11,12,13)]

new_arr = json.dumps(arr, ensure_ascii=False, indent=2)
text = text[:start] + new_arr + text[start + end_rel:]
path.write_text(text, encoding='utf-8')

print('Before slides 11-14:', before)
print('After slides 11-14:', after)
print('Moved original slide 12 between original slides 13 and 14')
