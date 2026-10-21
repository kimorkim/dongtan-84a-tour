from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[2]
im=Image.open(root/'assets/analysis/dimensioned_plan_1.png')
w,h=im.size
print('FULL IMAGE',w,h)
im.crop((1150,1350,1710,1770)).resize((1120,840)).save(root/'assets/analysis/dimension_small_rooms_detail.png')
gray=im.convert('L')
for x in (1200,1250,1330,1400,1460,1550,1650):
    lines=[y for y in range(1650,1750) if gray.getpixel((x,y))<150]
    groups=[]
    for y in lines:
        if not groups or y-groups[-1][-1]>1: groups.append([y])
        else: groups[-1].append(y)
    print('front profile',x,[(min(g),max(g)) for g in groups])
for name,rect in {'north':(.45,.17,.78,.56),'south':(.33,.53,.78,.85),
                  'west_vertical':(.15,.27,.39,.75),'east_vertical':(.60,.27,.79,.75)}.items():
    im.crop(tuple(int(a*(w if i%2==0 else h)) for i,a in enumerate(rect))).save(root/f'assets/analysis/dimension_{name}.png')
for name in ('east_vertical','west_vertical'):
    crop=Image.open(root/f'assets/analysis/dimension_{name}.png').convert('L')
    cw,ch=crop.size
    # Long horizontal extensions identify the dimension-chain endpoints.
    for a,b in ((int(cw*.82),int(cw*.90)),(int(cw*.07),int(cw*.15))):
        values=[sum(crop.getpixel((x,y))<140 for x in range(a,b)) for y in range(ch)]
        lines=[y for y,n in enumerate(values) if n>(b-a)*.7]
        groups=[]
        for y in lines:
            if not groups or y-groups[-1][-1]>2: groups.append([y])
            else: groups[-1].append(y)
        print(name,a,b,[round(sum(g)/len(g),1) for g in groups])
