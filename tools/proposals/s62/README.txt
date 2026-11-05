s62 proposal scripts (work dir /tmp/claude-0/s62, tools/ = copy of the repo tools + s55 gate patches + these files).
 rooms62.py            scenes vaultmart_a / vaultmart_b (cold VaultMart interiors). Needs rooms55.py (gate B + STAFF ONLY sign, with its
                       'SCENES += ...' line removed) and "import rooms62" at the end of tools/scene.py.
 blender_render_s62.patch  materials: sign_red/sign_white/shutter_grey/hazard_black (s55) + vm_* cold materials (floor, wall, shelf, box, band, led, screen...)
 scene_s62.patch       Scene.text(..., bold=False) (s55) + import rooms62
 blender_car.py        golden limousine (convex-hull body, gold metal, tinted glass, chrome, VV plates), 4 facings, iso camera
 car_sprites.py        outline + one shared 15-colour palette -> car/car_{se,nw,sw,ne}_q.png  (python3 car_sprites.py car 64 1.0 --rerender)
 car_plan.py / car_size.py   OBJ piece cover + tile counts, size sheet with the player
 mock_car.py           in-game mocks (parked with Victor + Valet, 4-frame drive-in, leaving)  python3 mock_car.py car out/city_q.png mock 1.0
 mock_vm.py            in-game mocks inside VaultMart (player + Valet + HUD + dialogue panel)
 compose62.py          vaultmart.png / car.png
Renders: python3 tools/proposals/s52/full_check.py out --samples 64 vma:vaultmart_a:all vmb:vaultmart_b:all cm:corner_market:all city:city_centre:1100,560,1580,816
