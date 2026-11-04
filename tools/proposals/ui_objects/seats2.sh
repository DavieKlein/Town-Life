cd /home/user/Town-Life
for spec in "diner_chair diner 7.0 5.5" "diner_booth2 diner 1.2 7.9" "cc_chair community_centre 6.1 3.5" "cc_couch community_centre 2.2 9.0" "lobby_bench vaulttech_lobby 1.5 4.0" "lobby_sofa vaulttech_lobby 11.3 9.7"; do
 set -- $spec
 /tmp/claude-0/s47/t.sh s2_$1 $2 $3 $4 "wait 330; shot /tmp/claude-0/s47/s2_$1_0.png; press a; wait 4; shot /tmp/claude-0/s47/s2_$1_m.png; press a; wait 40; shot /tmp/claude-0/s47/s2_$1_1.png; press b; wait 8;  shot /tmp/claude-0/s47/s2_$1_2.png" >/dev/null
done
