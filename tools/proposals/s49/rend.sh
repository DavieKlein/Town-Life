#!/bin/bash
# rend.sh scene out_prefix "crop" [flags] [samples]  -> <out>_floor.png <out>_objects.png (2x renders)
D=$(dirname "$0")
for l in floor objects; do
  blender -b -noaudio --python $D/render_scene.py -- $1 $l $2_$l.png "$3" 2 ${5:-64} "$4" 2>&1 | grep -E "Error|Traceback|error:" 
done
