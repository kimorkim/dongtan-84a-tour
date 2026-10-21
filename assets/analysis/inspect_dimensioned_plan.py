from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'pdf_deps'))
import fitz
from PIL import Image

root=Path(__file__).resolve().parents[2]
doc=fitz.open(root/'references/drawings/original/84a 평면도.pdf')
print('PAGES',len(doc))
for i,page in enumerate(doc):
    page.set_rotation(90)
    print('PAGE',i+1,'SIZE',page.rect)
    print(page.get_text())
    page.get_pixmap(matrix=fitz.Matrix(4,4)).save(root/f'assets/analysis/dimensioned_plan_{i+1}.png')
    im=Image.open(root/f'assets/analysis/dimensioned_plan_{i+1}.png')
    w,h=im.size
    im.crop((int(w*.145),int(h*.48),int(w*.52),int(h*.84))).save(root/'assets/analysis/dimensioned_bedrooms.png')
