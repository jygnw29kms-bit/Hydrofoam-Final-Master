from pathlib import Path
import pymupdf,json
root=Path(__file__).resolve().parents[1]
p=root/'reference/historical_hydrofoam/hydrofoam_build_article.pdf'
out=root/'renders/historical_plan';out.mkdir(parents=True,exist_ok=True)
d=pymupdf.open(p)
rows=[]
for i,page in enumerate(d):
 text=page.get_text()
 rows.append({'page':i+1,'text_excerpt':text[:500]})
 page.get_pixmap(matrix=pymupdf.Matrix(1.35,1.35),alpha=False).save(str(out/f'construction_page_{i+1:02d}.png'))
(root/'docs/HISTORICAL_HYDROFOAM_PAGE_INDEX.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
print('EXTRACTED',len(rows),'construction pages')
