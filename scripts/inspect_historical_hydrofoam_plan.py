from pathlib import Path
import pymupdf,json
root=Path(__file__).resolve().parents[1]
folder=root/'reference'/'historical_hydrofoam'
report=[]
for p in sorted(folder.glob('*.pdf')):
 try:
  doc=pymupdf.open(p)
  row={'file':p.name,'pages':len(doc),'page_sizes_mm':[[round(pg.rect.width*25.4/72,1),round(pg.rect.height*25.4/72,1)] for pg in doc], 'first_page_text':doc[0].get_text()[:350]}
  if '21page' in p.name:
   out=root/'renders'/'historical_plan';out.mkdir(parents=True,exist_ok=True)
   doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(str(out/'plan_page_01.png'))
  report.append(row)
 except Exception as e:report.append({'file':p.name,'error':str(e)})
(root/'docs'/'HISTORICAL_HYDROFOAM_PLAN_INSPECTION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2)[:1800])
