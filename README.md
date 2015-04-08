Congressional Gerrymandering
============================

This is a d3 mapping project that creates a map with each congressional district
colored by the degree to which it is gerrymandered. E.g. Dark red is a
highly gerrymandered republican district and dark blue is democratic and highly
gerrymandered.  

This repo contains the following files:

1. gerrymandering.py --- This contains all the code I used for merging various datasets as well as generating the gerrymandering metrics.
2. gerrymandering.html --- This is the html/CSS/javascript/d3 code I used to create the visual representation of my project. You can view this visualization at bl.ocks.org/warrenronsiek.
3. topo_uscd.json --- These are results from the gerrymandering.py file written into json format to be used by gerrymandering.html.

The shapefiles I used for this project were gotten from the US Census bureau. The party data (i.e. whether a district should be blue or red) was gotten from the Office of the Clerk (in the house of representatives).

Note that I calculate the Reock metric a bit differently than standard. I calculated the smallest square that the district can fit in, and then used the largest circle that could fit in that square for the comparison.
