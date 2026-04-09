import json

import httpx

from folium import Map, TileLayer

# %matplotlib inline

titiler_endpoint = "https://titiler.xyz"  # Developmentseed Demo endpoint. Please be kind.
url = "https://github.com/lawls76/Anchor_Cache/raw/working/Anchor_BMap/Anchor_BMap_OutputCOG.tif"

# Fetch File Metadata to get min/max rescaling values (because the file is stored as float32)
r = httpx.get(
    f"{titiler_endpoint}/cog/info",
    params = {
        "url": url,
    }
).json()

bounds = r["bounds"]
print(r)

r = httpx.get(
    f"{titiler_endpoint}/cog/WebMercatorQuad/tilejson.json",
    params = {
        "url": url,
    }
).json()

m = Map(
    location=((bounds[1] + bounds[3]) / 2,(bounds[0] + bounds[2]) / 2),
    zoom_start=13
)

TileLayer(
    tiles=r["tiles"][0],
    opacity=1,
    attr="DigitalGlobe OpenData"
).add_to(m)

m