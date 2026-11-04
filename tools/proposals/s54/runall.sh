#!/bin/bash
cd /tmp/claude-0/s54
for o in base A C1 C2; do for c in player mia rosa victor; do
  echo "blender -b -noaudio --python keep/faces.py -- $c r/${c}_$o 4 64 $o all > r/${c}_$o.log 2>&1"
done; done | xargs -P 4 -I{} bash -c "{}"
