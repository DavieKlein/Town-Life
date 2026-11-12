"""s75: 128 px dialogue portraits (neutral + happy) for the speaking new residents, made with the REAL painter tools/portraits (no game file touched).
  python3 res_portraits.py OUT_PNG [chars]"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PT = os.path.abspath(os.path.join(HERE, "..", "..", "portraits"))
sys.path.insert(0, HERE)
sys.path.insert(0, PT)
import chars  # noqa: E402
import portraits  # noqa: E402
from pt import downsample, hexc  # noqa: E402

CH = {
    "ines": dict(kind="ines", fw=1.04, jaw=1.1, chin=97, fem=True, eye_w=1.12, iris_r=4.7, brow_w=1.9, rosy=True,
                 skin=["4a2a1c", "7a4a30", "9a6240", "b87c54", "d09a70"], blush="c8604c", lip=["7a2a30", "a4444c", "50181e"],
                 iris=["1e1208", "3e2814", "70502c"], hair=["0c0806", "1c1410", "30241c", "4a3a2e"], brow_col="140c08",
                 cloth=["a8601a", "e2982c", "f4b84c", "ffd88c"], collar=["24487c", "3b6fb0", "5c92d0", "94bce8"],
                 scarf=["801c4c", "c8327a", "e458a0", "f89cc8"], band=["8a6a10", "f6d24a", "fff09a"]),
    "teo": dict(kind="teo", fw=0.96, jaw=0.8, chin=91, fem=False, eye_w=1.28, iris_r=5.3, brow_w=1.5,
                skin=["7a4a30", "b07a50", "c98f64", "e0aa80", "f4c8a0"], blush="e08060", lip=["a8504a", "ca7468", "782e30"],
                iris=["2a1a10", "5a3a20", "8a6034"], hair=["0c0806", "1c1410", "30241c", "4a3a2e"], brow_col="1c1410",
                cloth=["1e6a44", "3f9a6a", "62c08c", "a0e6bc"], collar=["1e6a44", "3f9a6a", "62c08c"],
                cap=["8a3a0c", "e8742a", "f8a050", "ffd090"]),
    "grigor": dict(kind="grigor", fw=0.98, jaw=1.04, chin=97, fem=False, eye_w=1.02, iris_r=4.3, brow_w=3.2, brow_gain=1.3,
                   skin=["8a5a44", "c08a70", "dca888", "eec4a8", "fadccc"], blush="e08a78", lip=["a0605a", "c48478", "6a3430"],
                   iris=["1e3a58", "3a6a90", "8ab4d4"], hair=["8a8a96", "bcbcc8", "e8e8ee", "ffffff"], brow_col="d8d8e0",
                   cloth=["0e1626", "27384f", "3e5678", "6a86a8"], collar=["0e1626", "27384f", "3e5678"],
                   cap=["8890a4", "d0d6e2", "f8fafc", "ffffff"], band=["080a0e", "14161c", "2a2e38"], gold=["8a6a10", "c8a02c", "f0d060", "fff0a0"]),
    "pruitt": dict(kind="pruitt", fw=1.02, jaw=1.02, chin=96, fem=False, eye_w=0.98, iris_r=4.2, brow_w=2.6,
                   skin=["8c5a44", "c88a6c", "e2b08a", "f2cca8", "fde4c8"], blush="e0806a", lip=["a8604a", "c88470", "6a3028"],
                   iris=["2a1a10", "5a3a20", "8a6034"], hair=["1c120c", "3a281c", "5a4030", "7a5a44"], brow_col="2a1a10",
                   cloth=["5a626e", "8f98a6", "b4bcc8", "dce2ea"], collar=["b0b6c0", "eef0f3", "ffffff"],
                   cap=["2a303c", "5e6676", "8a92a2", "b8c0ce"], band=["1a1e28", "3a404c", "5a6070"], gold=["8a6a10", "c8a02c", "f0d060", "fff0a0"]),
    "kessler": dict(kind="kessler", fw=0.84, jaw=0.88, chin=99, fem=False, eye_w=1.1, iris_r=4.3, brow_w=2.0,
                    skin=["a07060", "d8a088", "f0c4a8", "fcdcc8", "fff0e4"], blush="f0907a", lip=["a8604a", "c88470", "6a3028"],
                    iris=["2a4a68", "4a6a88", "9ac0dc"], hair=["6a4a28", "9a7440", "c8a468", "e8cc90"], brow_col="8a6a3a",
                    cloth=["5a626e", "9aa3ad", "bcc4ce", "e0e6ee"], collar=["b0b6c0", "eef0f3", "ffffff"],
                    cap=["3a404c", "7a8392", "a0a8b8", "c8d0dc"], band=["1a1e28", "3a404c", "5a6070"], gold=["8a6a10", "c8a02c", "f0d060", "fff0a0"]),
    "valdez": dict(kind="valdez", fw=0.9, jaw=0.92, chin=95, fem=True, eye_w=1.1, iris_r=4.4, brow_w=1.8,
                   skin=["8a5238", "c0866a", "d9a080", "ecc0a0", "f8dcc4"], blush="e87070", lip=["8a2c3c", "b4485a", "5a1424"],
                   iris=["2a1a0e", "4a3018", "7a5a30"], hair=["22181e", "40303a", "6a5864", "9a8a98"], brow_col="2a2028",
                   cloth=["8a3040", "d86a70", "f0949a", "ffc4c8"], collar=["8a3040", "d86a70", "f0949a"],
                   shawl=["3a1458", "6a3a9a", "8a56c0", "b894e0"]),
}
for n, c in CH.items():
    c["parts"] = "res"
    for k in ("skin", "iris", "hair", "cloth", "collar", "lip", "cap", "band", "gold", "scarf", "shawl"):
        if k in c:
            c[k] = [hexc(h) for h in c[k]]
    c["blush"] = hexc(c["blush"]); c["brow_col"] = hexc(c["brow_col"])
    chars.CH[n] = c
NAMES = {"ines": "Ines", "teo": "Teo", "grigor": "Grigor", "pruitt": "Pruitt", "kessler": "Kessler", "valdez": "Mrs. Valdez"}
EXS = ["neutral", "happy"]

if __name__ == "__main__":
    out = sys.argv[1]
    who = sys.argv[2].split(",") if len(sys.argv) > 2 else list(CH)
    sheet = Image.new("RGB", (len(who) * 264 + 8, 2 * 264 + 30), (236, 226, 200))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    for j, c in enumerate(who):
        fr = {}
        for e in EXS:
            rgb, a = downsample(chars.render(c, e))
            fr[(128, e)] = (rgb.astype(np.float32), a.astype(np.float32))
        idx, pal = portraits.quantize_char(c, fr)
        pl = np.vstack([[236, 226, 200], pal]).astype(np.uint8)
        d.text((8 + j * 264, 6), NAMES[c], font=f, fill=(30, 30, 40))
        for i, e in enumerate(EXS):
            im = Image.fromarray(pl[idx[(128, e)]], "RGB").resize((256, 256), Image.NEAREST)
            sheet.paste(im, (8 + j * 264, 28 + i * 264))
        print("done", c, flush=True)
    sheet.save(out)
