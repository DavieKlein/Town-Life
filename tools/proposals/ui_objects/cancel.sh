cd /home/user/Town-Life
run(){ n=$1; shift; /tmp/claude-0/s47/t.sh c_$n "$@" >/dev/null; }
S=/tmp/claude-0/s47/c_
run sink public_toilet 1.8 3.4 "press a; wait 3; press a; wait 40; shot ${S}sink_0.png; press b; wait 6; shot ${S}sink_1.png; wait 120; shot ${S}sink_2.png"
run read community_centre 2.5 2.0 "press a; wait 3; press a; wait 60; shot ${S}read_0.png; press b; wait 6; shot ${S}read_1.png; wait 120; shot ${S}read_2.png"
run bin city_centre 5.0 22.0 "press a; wait 3; press a; wait 60; shot ${S}bin_0.png; press b; wait 6; shot ${S}bin_1.png; wait 200; shot ${S}bin_2.png"
run eat corner_market 13.9 16.2 "press a; wait 3; press a; wait 40; shot ${S}eat_0.png; press b; wait 6; shot ${S}eat_1.png; wait 200; shot ${S}eat_2.png"
run drink city_centre 53.0 44.2 "press a; wait 3; press down; press a; wait 50; shot ${S}drink_0.png; press b; wait 6; shot ${S}drink_1.png; wait 150; shot ${S}drink_2.png"
run wface city_centre 53.0 44.2 "press a; wait 3; press a; wait 50; shot ${S}wface_0.png; press b; wait 6; shot ${S}wface_1.png; wait 150; shot ${S}wface_2.png"
run toilet public_toilet 1.2 2.6 "press a; wait 3; press a; wait 60; shot ${S}toilet_0.png; press b; wait 6; shot ${S}toilet_1.png; wait 100; shot ${S}toilet_2.png" town-life.gba 20
