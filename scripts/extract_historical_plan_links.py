import pymupdf
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'reference/historical_hydrofoam/hydrofoam_build_article.pdf'
d=pymupdf.open(p)
for i,page in enumerate(d):
 t=page.get_text()
 print('PAGE',i+1,'chars',len(t),'images',len(page.get_images()))
 for l in page.get_links():
  uri=l.get('uri','')
  if uri and any(k in uri.lower() for k in ('plan','hydro','pdf','zip','depron')):print('LINK',uri)
