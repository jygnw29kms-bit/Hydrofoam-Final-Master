import os, sys
from PIL import Image, ImageChops, ImageFilter
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
ver=sys.argv[1]
out=os.path.join(ROOT,'comparison',ver); os.makedirs(out,exist_ok=True)
TROOT=os.path.join(ROOT,'reference')

def norm(m,size=(1200,600)):
    b=m.getbbox()
    if not b: raise RuntimeError('empty mask')
    c=m.crop(b)
    c.thumbnail((size[0]-20,size[1]-20),Image.Resampling.LANCZOS)
    o=Image.new('L',size,0); o.paste(c,((size[0]-c.width)//2,(size[1]-c.height)//2)); return o

def model_mask(path):
    im=Image.open(path).convert('RGB'); p=im.load(); m=Image.new('L',im.size,0); q=m.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b=p[x,y]
            if r>g*1.22 and r>b*1.30 and r>80: q[x,y]=255
    return m.filter(ImageFilter.MedianFilter(3))

def target(path):
    im=Image.open(path).convert('L')
    return im.point(lambda x:255 if x>127 else 0)

def score(t,m,name):
    t=norm(t); m=norm(m)
    inter=ImageChops.multiply(t,m); union=ImageChops.lighter(t,m)
    ia=sum(inter.getdata())/255.0; ua=sum(union.getdata())/255.0
    iou=ia/ua if ua else 0
    ov=Image.new('RGB',t.size,(25,25,25)); op=ov.load(); tp=t.load(); mp=m.load()
    for y in range(t.height):
        for x in range(t.width):
            a=tp[x,y]>127; b=mp[x,y]>127
            op[x,y]=(245,220,30) if a and b else ((40,220,80) if a else ((240,55,55) if b else (25,25,25)))
    ov.save(os.path.join(out,name+'_overlay.png'))
    return iou
rt=os.path.join(ROOT,'renders',ver,'assembled_top.png'); rs=os.path.join(ROOT,'renders',ver,'assembled_side.png')
iot=score(target(os.path.join(TROOT,'final_master_top_mask_v3.png')),model_mask(rt),'top')
ios=score(target(os.path.join(TROOT,'final_master_side_mask_v3.png')),model_mask(rs),'side')
mean=(iot+ios)/2
open(os.path.join(out,'score.txt'),'w').write(f'top_iou={iot:.6f}\nside_iou={ios:.6f}\nmean_iou={mean:.6f}\n')
print(f'{ver} TOP={iot:.4f} SIDE={ios:.4f} MEAN={mean:.4f}')

