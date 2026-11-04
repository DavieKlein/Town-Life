#!/bin/bash
# rend.sh scene out_prefix [samples]
cd /tmp/claude-0/s47/work
for l in floor objects; do blender -b -noaudio --python tools/blender_render.py -- $1 $l $2_$l.png 2 ${3:-48} 2>&1 | grep -i -E "error|Traceback" ; done
python3 preview.py $2 $2_c.png
