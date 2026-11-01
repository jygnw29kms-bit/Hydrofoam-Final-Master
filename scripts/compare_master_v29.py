import os, glob, sys
from PIL import Image, ImageOps, ImageChops, ImageEnhance, ImageFilter
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
refs=glob.glob(os.path.join(ROOT,'reference','final_master_1408x1056*'))
if not refs:
 print('NO_MASTER_ON_JENS'); sys.exit(2)
master=Image.open(refs[0]).convert('RGB')
out=os.path.join(ROOT,'comparison','v29'); os.makedirs(out,exist_ok=True)
# Orthographic panels in supplied master sheet.
top=master.crop((0,620,515,1056)).rotate(90,expand=True)
side=master.crop((500,610,1408,860))
top.save(os.path.join(out,'master_top_crop.png')); side.save(os.path.join(out,'master_side_crop.png'))

def target_mask(im):
    # background is near-white; retain gray/orange/dark aircraft pixels
    pix=im.load(); m=Image.new('L',im.size,0); mp=m.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b=pix[x,y]; mx=max(r,g,b); mn=min(r,g,b)
            sat=mx-mn
            # ignore pure/near-white panel background, keep aircraft incl. light gray
            if (r+g+b)/3 < 238 or sat>18:
                mp[x,y]=255
    # remove isolated photo artifacts by median filter
    return m.filter(ImageFilter.MedianFilter(5))

def model_mask(im):
    im=im.convert('RGB'); p=im.load(); m=Image.new('L',im.size,0); q=m.load()
    # workbench bg is dark gray, aircraft is orange; saturation isolates it
    for y in range(im.height):
        for x in range(im.width):
            r,g,b=p[x,y];
            if r > g*1.25 and r > b*1.35 and r>90: q[x,y]=255
    return m.filter(ImageFilter.MedianFilter(3))

def bbox_nonzero(m):
    b=m.getbbox();
    if not b: raise RuntimeError('empty mask')
    return b

def norm(m,size=(1200,600)):
    b=bbox_nonzero(m); c=m.crop(b)
    # preserve aspect and center
    c.thumbnail((size[0]-20,size[1]-20),Image.Resampling.LANCZOS)
    out=Image.new('L',size,0); out.paste(c,((size[0]-c.width)//2,(size[1]-c.height)//2)); return out

def score(target,model,name):
    t=norm(target); m=norm(model)
    inter=ImageChops.multiply(t,m)
    # union = max
    union=ImageChops.lighter(t,m)
    ia=sum(inter.getdata())/255.0; ua=sum(union.getdata())/255.0
    iou=ia/ua if ua else 0
    # overlay: target green, model red, overlap yellow
    ov=Image.new('RGB',t.size,(25,25,25)); op=ov.load(); tp=t.load(); mp=m.load()
    for y in range(t.height):
        for x in range(t.width):
            a=tp[x,y]>127; b=mp[x,y]>127
            if a and b: op[x,y]=(245,220,30)
            elif a: op[x,y]=(40,220,80)
            elif b: op[x,y]=(240,55,55)
    ov.save(os.path.join(out,name+'_overlay.png'))
    return iou
mt=target_mask(top); ms=target_mask(side)
rt=Image.open(os.path.join(ROOT,'renders','v29','assembled_top.png'))
rs=Image.open(os.path.join(ROOT,'renders','v29','assembled_side.png'))
iot=score(mt,model_mask(rt),'top'); ios=score(ms,model_mask(rs),'side')
with open(os.path.join(out,'score.txt'),'w') as f:
 f.write(f'top_iou={iot:.6f}\nside_iou={ios:.6f}\nmean_iou={(iot+ios)/2:.6f}\n')
print(f'TOP_IOU={iot:.4f} SIDE_IOU={ios:.4f} MEAN={(iot+ios)/2:.4f}')








