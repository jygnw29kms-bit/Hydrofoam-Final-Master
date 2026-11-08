from pathlib import Path
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
p=R/'README.md'
data=p.read_text(encoding='utf-8')
flag='## EINZIGER VERBINDLICHER FINAL MASTER'
if flag not in data:
 prefix='''## EINZIGER VERBINDLICHER FINAL MASTER\n\n![Original-Final-Master, unveraendert](reference/FINAL_MASTER_ORIGINAL.jpeg)\n\n**Dieses Originalbild ist die einzige verbindliche Designvorlage.** Keine CAD-Visualisierung, keine automatisch generierten Bilder und keine aelteren Silhouettenmasken ersetzen es.\n\n[Master-Sperre mit Pruefsumme und Merkmalen](docs/FINAL_MASTER_LOCK.md) | [Original als JPEG](reference/FINAL_MASTER_ORIGINAL.jpeg)\n\n**SHA-256:** `a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd`\n\n---\n\n'''
 idx=data.find('\n')
 data=data[:idx+1]+'\n'+prefix+data[idx+1:]
 p.write_text(data,encoding='utf-8',newline='\n')
print('README_MASTER_PRESENT',flag in p.read_text(encoding='utf-8'))
