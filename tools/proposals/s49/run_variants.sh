#!/bin/bash
# renders the 4 crops x 2 layers x 4 variants into $OUT (default /tmp/claude-0/s49/sh); 2 jobs at a time
OUT=${OUT:-/tmp/claude-0/s49/sh}
cd "$(dirname "$0")/../../.."
jobs_list=()
declare -A CROP=( [street]="city_centre 1368,696,1608,840" [fountain]="city_centre 1048,880,1288,1024"
                  [toilet]="public_toilet 0,40,240,184" [library]="community_centre 144,80,384,224" )
for v in A B C D; do for n in street fountain toilet library; do for l in floor objects; do
  set -- ${CROP[$n]}
  [ -f $OUT/${n}_${l}_$v.png ] && continue
  jobs_list+=("blender -b -noaudio --python tools/proposals/s49/render_variant.py -- $1 $l $OUT/${n}_${l}_$v.png $v $2 > /dev/null 2>&1")
done; done; done
printf '%s\n' "${jobs_list[@]}" | xargs -P 2 -I{} bash -c "{}"
echo done > $OUT/ALL_DONE
