"""
Town Life - per-character face look (shared by the Blender side tools/face_kit.py and the pixel pass tools/face_pass.py).

  iris / brow / lips  colours of the modelled 3D features (Blender)
  female              thicker lashes, narrower mouth
  hair                hair colour (strands / highlights; the brow and hair-highlight pixels of the pixel pass derive from it)
  glasses             "rosa" (round) / "victor" (sunglasses): fitted to the head instead of the cast.py prop; None = no glasses
  plips               colour of the mouth pixel in the sprite palette (reserved palette entry)
"""
FACE = {
    "player":    dict(iris="#5a3a22", brow="#3a2214", lips="#b5605a", plips="#a8584e", female=False, hair="#4a2a18", glasses=None),
    "mia":       dict(iris="#2f8a78", brow="#a24a1e", lips="#c4505a", plips="#b8484e", female=True,  hair="#c8622a", glasses=None),
    "rosa":      dict(iris="#6f8fb0", brow="#8e8e98", lips="#b0505a", plips="#a84850", female=True,  hair="#c4c4cc", glasses="rosa"),
    "victor":    dict(iris="#2a1a10", brow="#e8e0c8", lips="#a8604a", plips="#9a5440", female=False, hair="#f1ead4", glasses="victor"),
    "dex":       dict(iris="#3a2616", brow="#2a1c18", lips="#a85a4a", plips="#9c5046", female=False, hair="#2a1c18", glasses=None),
    "dex_vault": dict(iris="#3a2616", brow="#241814", lips="#a85a4a", plips="#9c5046", female=False, hair="#241814", glasses=None),
    "pimm":      dict(iris="#5a7a8a", brow="#d8d8d0", lips="#b0685c", plips="#a2605a", female=False, hair="#f2f2ee", glasses=None),
    "lou":       dict(iris="#4a3020", brow="#3a2a1e", lips="#b0584c", plips="#a2504a", female=False, hair="#3a2a1e", glasses=None),
}
