import os,json,glob,math
from PIL import Image
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; D=os.path.join(ROOT,'comparison','hero_grid')
meta=json.load(open(os.path.join(D,'grid.json')))
# Final-master hero crop measured from supplied 1408x1056 board.
# Vehicle silhouette spans approx x=8..1394, y=15..570 in the main image.
target_ratio=(1394-8)/(570-15)
target_center=((8+1394)/2/1408,(15+570)/2/620)
rows=[]
for c in meta['configs']:
 im=Image.open(os.path.join(D,c['file'])).convert('RGB');p=im.load();xs=[];ys=[]
 for y in range(im.height):
  for x in range(im.width):
   r,g,b=p[x,y]
   # orange model on white background
   if r>120 and r>g*1.35 and r>b*1.5:
    xs.append(x);ys.append(y)
 if not xs:continue
 w=max(xs)-min(xs)+1;h=max(ys)-min(ys)+1;ratio=w/h;cx=(min(xs)+max(xs))/2/im.width;cy=(min(ys)+max(ys))/2/im.height
 score=abs(math.log(max(.01,ratio)/target_ratio))+0.25*abs(cy-target_center[1])+0.10*abs(cx-.5)
 rows.append({**c,'bbox':[min(xs),min(ys),max(xs),max(ys)],'ratio':ratio,'score':score})
rows.sort(key=lambda r:r['score']);json.dump(rows,open(os.path.join(D,'scores.json'),'w'),indent=2)
b=rows[0];open(os.path.join(D,'best_camera.json'),'w').write(json.dumps(b,indent=2));print('BEST_CAMERA',b)