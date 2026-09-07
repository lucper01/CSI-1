from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='Rekow, D., Baudouin, J.-Y., Durand, K., & Leleu, A. (2022). Smell what you hardly see. <em>NeuroImage, 255</em>, 119181.'
new='Porter, J., Craven, B., Khan, R. M., Chang, S.-J., Kang, I., Judkewitz, B., Volpe, J., Settles, G., & Sobel, N. (2007). Mechanisms of scent-tracking in humans. <em>Nature Neuroscience, 10</em>, 27-29.'
count=s.count(old)
assert count==3, f'expected 3 full Rekow appendix citations, found {count}'
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
assert old not in s
assert s.count(new)==3
print('OK - Axis 2 appendix reference replaced')
