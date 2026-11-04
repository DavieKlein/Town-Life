"""Character definitions (proposal). Coordinates in metres for a 1.78 m body, facing -Y, x = character's left (+x)."""
CHARS = {
 "mia": dict(label="Mia", model="Female_Casual", height=1.78,
    colours={"Shirt":"#2a9a96","Pants":"#3c4a66","Hair":"#c8622a","HairBase":"#c8622a","Skin":"#f2c8a4","Shoes":"#3a2a22","Socks":"#f2efe6"}, props=[]),
 "player": dict(label="You", model="Male_LongSleeve", height=1.78,
    colours={"Shirt":"#2f5aa8","Pants":"#c8a46a","Hair":"#5a3420","Skin":"#f0c09a","Shoes":"#3a2a22","Socks":"#f2efe6"}, props=[]),
 "rosa": dict(label="Rosa Bellini", model="Female_Alternative", height=1.56,
    colours={"Jacket":"#7a2236","LightJacket":"#8e2d44","Shirt":"#efe6cc","Pants":"#34303a","Hair":"#c4c4cc","HairBase":"#c4c4cc","Skin":"#eabf9c","Shoes":"#2e2420","Socks":"#e9e2d0"},
    props=[("sphere",(0,0.09,1.71),(0.075,0.075,0.07),"#c4c4cc"),            # grey bun
           ("torus",(0.043,-0.125,1.665),(0.034,0.034,0.006),"#2a2a30",(90,0,0)),   # round glasses
           ("torus",(-0.043,-0.125,1.665),(0.034,0.034,0.006),"#2a2a30",(90,0,0)),
           ("box",(0,-0.125,1.67),(0.03,0.008,0.008),"#2a2a30"),
           ("torus",(0,-0.035,1.435),(0.075,0.075,0.009),"#f4f0e8")]),       # pearls
 "dex": dict(label="Dex (shop)", model="Male_Shirt", height=1.78,
    colours={"Shirt":"#d8662a","Shirt2":"#e8dcc0","Pants":"#3a4f7a","Hair":"#2a1c18","Hair2":"#2a1c18","Skin":"#dfa676","Shoes":"#f0f0f0","Socks":"#f4f4f4","Eyes":"#202020"},
    props=[("box",(0,-0.118,1.02),(0.27,0.03,0.42),"#2f7a45"),             # green Corner Market apron
           ("box",(0.09,-0.139,1.15),(0.07,0.01,0.04),"#f0e0a0")]),        # name tag
 "dex_vault": dict(label="Dex (VaultMart)", model="Male_Shirt", height=1.78,
    colours={"Shirt":"#a3a9b2","Shirt2":"#eef0f3","Pants":"#8c9199","Hair":"#241814","Hair2":"#241814","Skin":"#dfa676","Shoes":"#25252b","Socks":"#222222","Eyes":"#202020"},
    props=[("box",(0,-0.125,1.20),(0.05,0.02,0.34),"#e2b53a"),             # slick gold tie
           ("box",(0.10,-0.128,1.30),(0.07,0.01,0.04),"#e2b53a"),          # badge
           ]),
 "victor": dict(label="Victor Vault", model="Male_Suit", height=1.84, widen=1.06,
    colours={"Shirt":"#d9ab36","Pants":"#efe2bc","Details":"#f6d874","TieTexture":"#16110e","Hair":"#f1ead4","Skin":"#d49a68","Eyes":"#2a1a10","Shoes":"#2a1a10"},
    props=[("box",(0,-0.115,1.64),(0.205,0.03,0.05),"#0c0c10"),             # sunglasses
           ("torus",(0,-0.07,1.395),(0.125,0.125,0.014),"#f6d874",(62,0,0)),
           ("cyl",(0,-0.145,1.27),(0.042,0.042,0.012),"#f6d874",(90,0,0)),            # gold chain
           ("cyl",(0.255,-0.06,0.42),(0.014,0.014,0.84),"#f2c94c"),        # gold cane
           ("sphere",(0.255,-0.06,0.86),(0.04,0.04,0.04),"#f2c94c")]),
 "pimm": dict(label="Mr. Pimm", model="Male_LongSleeve", height=1.62,
    colours={"Shirt":"#a98d5c","Pants":"#4a4036","Hair":"#f2f2ee","Skin":"#e9bf9c","Shoes":"#3d3026","Socks":"#e8e8e0","Eyes":"#202020"},
    props=[("sphere",(0.0,-0.035,1.70),(0.128,0.132,0.085),"#8b6b45"),            # flat cap
           ("box",(0,-0.13,1.712),(0.17,0.1,0.014),"#6e5236",(8,0,0)),           # cap brim
           ("torus",(0,-0.02,1.46),(0.095,0.095,0.03),"#a8312f"),         # red scarf
           ("cyl",(-0.255,-0.05,0.42),(0.012,0.012,0.84),"#5a3d22")]),     # walking stick
 "lou": dict(label="Big Lou", model="Male_Casual", height=1.66, widen=1.32, depth=1.15,
    colours={"Shirt":"#f4f1ea","Pants":"#566074","Hair":"#3a2a1e","Skin":"#e6b48a","Shoes":"#2d2d2d","Socks":"#eeeeee"},
    props=[("box",(0,-0.125,1.00),(0.30,0.03,0.52),"#b83a32"),             # red diner apron
           ("box",(0,-0.115,1.31),(0.15,0.02,0.07),"#b83a32"),
           ("cyl",(0,0,1.765),(0.108,0.108,0.09),"#fbfbfb"),                # chef hat band
           ("sphere",(0,0,1.86),(0.15,0.15,0.1),"#fbfbfb"),                # puffy top
           ("box",(0,-0.1,1.626),(0.10,0.03,0.022),"#2b1d14")],           # moustache
    pcam=(0.80,1.96)),
}

ROBOT = dict(label="Valet", model="ROBOT", height=1.34, colours={}, props=[], pcam=(0.90, 1.40))


CHARS["robot"]=ROBOT
