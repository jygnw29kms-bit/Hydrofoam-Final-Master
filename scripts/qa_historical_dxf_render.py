from PIL import Image
from collections import Counter
from pathlib import Path
p=Path('renders/historical_dxf/dxf_cut_parts_layout.png');im=Image.open(p).convert('RGB');counts=Counter(im.getdata())
print('IMAGE',im.size,'COLORS',len(counts),'MOST_COMMON',counts.most_common(5))
# Background is dark (about 59); verify a sizeable high-contrast light foreground.
foreground=sum(v for (r,g,b),v in counts.items() if min(r,g,b)>=110)
ratio=foreground/(im.width*im.height)
print('VISIBLE_FOREGROUND_PIXELS',foreground,'RATIO',round(ratio,5))
assert ratio>.03,'RENDER APPEARS EMPTY OR TOO LOW CONTRAST'
print('PASS: model outlines are actually visible in the rendered PNG')
