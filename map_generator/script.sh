#!/bin/sh

# imagemagic script generating map with scores
# every district has label containg points collected by every fellowship (fraction)
# district color changes when it is occupied by one of fellowships
# colored border indicates which fellowship is privileged in district

cd map_generator
pwd
convert -size 1000x707 xc: \
mapa.png -gravity center -composite \
\
d1_col.png -gravity center -compose over -composite \
d2_col.png -gravity center -compose over -composite \
d3_col.png -gravity center -compose over -composite \
d4_col.png -gravity center -compose over -composite \
d5_col.png -gravity center -compose over -composite \
d6_col.png -gravity center -compose over -composite \
d7_col.png -gravity center -compose over -composite \
d8_col.png -gravity center -compose over -composite \
\
punkty.png -gravity center -composite \
-layers flatten ../static/map/13-11-2025_21-48-06.png