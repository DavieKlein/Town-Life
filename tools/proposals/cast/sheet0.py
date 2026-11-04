from PIL import Image
import sys
names="Female_Alternative Female_Casual Female_Dress Female_TankTop Male_Casual Male_LongSleeve Male_Shirt Male_Suit".split()
S=2
W=Image.new("RGBA",(len(names)*64*3,128*3),(120,130,120,255))
for i,n in enumerate(names):
    im=Image.open(f"base/{n}/s_0.png").convert("RGBA").resize((192,384),Image.LANCZOS)
    W.alpha_composite(im,(i*192,0))
W.convert("RGB").save("base_sheet.png")
