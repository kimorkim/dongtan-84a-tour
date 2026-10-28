"""Extract photo detail while removing panorama lighting/colour casts for Q24."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np
root=Path(__file__).resolve().parent.parent
image=Image.open(root/'references/modelhouse/vr84a/011_r.jpg').convert('RGB')
# Clear tile interior: no labels, fittings or photographed grout.
patch=image.crop((640,400,1100,620)).resize((1024,512),Image.Resampling.LANCZOS).convert('L')
detail=np.asarray(patch,dtype=float)-np.asarray(patch.filter(ImageFilter.GaussianBlur(24)),dtype=float)
albedo=np.clip(np.array([184.,182.,177.])[None,None,:]+detail[:,:,None]*.65,0,255).astype('uint8')
out=root/'assets/textures_export/q24_tile_albedo.png'
Image.fromarray(albedo).save(out)
print('Prepared neutral photo-detail tile:',out)
