# s71 style proposal: "less blocky, smoother" (proposal only, no game asset changed)

Scripts: `s71_render.py` (Blender, real blender_render.py + monkeypatched variants cur/v1/v2), `s71_actor.py` (actor light/smoothing
variants), `variants.py` (grade + Lab k-means + limited ordered dither = v3), `run.py` (render / actors / compose).
Owner narrowed the scope to Current vs V1 "Soft" (bevelled boxes, 32-segment cylinders/spheres, smooth normals, softer sun,
thinner/softer outlines, softer grade); V2/V3 and actor/market results exist but were not pursued.

Crop stats (31x21-cell window, tiles floor/objects; cache = 624 slots per layer): fountain cur 597/253, V1 604/240;
market cur 551/405, V1 571/385. So V1 does not change tile pressure noticeably, but the floor layer is already near 624.
Cost: crop renders equal in Cycles time (~28 s objects / ~52 s floor); Python scene build +44 s on the city because
`bmesh.ops.bevel` per box in a shared bmesh is slow (rewrite needed: bevel each box in its own bmesh before merging, or build
chamfered boxes by hand). Only 224 city boxes qualified for bevel under the current rules (small furniture-like boxes).
