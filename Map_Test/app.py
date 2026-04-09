
import json
import os

import geojson
from geojson import Feature, Polygon, FeatureCollection
from flask import Flask, jsonify, render_template_string, Response, url_for
import folium
import datetime

import json

import httpx

from folium import Map, TileLayer, IFrame


app = Flask(__name__)

# Center on Hurricane Hole Nassau Bahamas
LONGITUDE = -77.3193
LATITUDE = 25.07932



# small helper function
def now():
    return datetime.datetime.now()


T0 = now()



# Define a function to create the HTML for the popup
def create_popup(feature):
    name = feature["Descrip"] # feature['properties']['name']
    price = feature["Unit Price"]
    # print(feature)
    image_url = feature['image_url']
    if feature["id"]:
        
        html = f'''
            <div>
                <body>
                <h4><strong>{name}</strong></h4>
                <p> The Cost of this {name} is ${price}. </p>
                <img src="{image_url}" alt="SVG Image" width="900" height="750" max_native_zoom=27 style="transform:rotate(90deg);" img style="width:200%; height:150%;">
                <a>
                <br>               
                <button onclick="alert('Button clicked!')">Purchase Now</button>
                </a>
                </body>                
            </div>
        '''
    return folium.Popup(html, max_width=1000)
@app.route('/')
def index():
    # Get Starting point lat/long location
    P = [LATITUDE, LONGITUDE]

    # map = folium.Map(max_zoom=33, min_zoom=0, zoom_start=18, zoom_control=True,
    #                  control_scale=True, crs="EPSG3857")

    #Set Format for Geotiff Image
    titiler_endpoint = "https://titiler.xyz"  # Developmentseed Demo endpoint. Please be kind.

    #fetch url of GeoTiff image from Git
    url = "https://github.com/lawls76/Anchor_Cache/raw/working/Anchor_BM_geo.tif" #Anchor_Seat_geo_update.tif"

    # Fetch File Metadata to get min/max rescaling values (because the file is stored as float32)
    r = httpx.get(
        f"{titiler_endpoint}/cog/info",
        params={
            "url": url,
        }
    ).json()

    bounds = r["bounds"]
    # print(r)

    r = httpx.get(
        f"{titiler_endpoint}/cog/WebMercatorQuad/tilejson.json",
        params={
            "url": url,
        }
    ).json()

    map = Map(
        location=((bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2),
        zoom_start=18
    )
    map._id = 'live'


    TileLayer(
        tiles=r["tiles"][0],
        opacity=1,
        attr="Custom COG Raster Data",
        name="The Anchor",
        overlay=True,
        show=True,
        max_native_zoom=27,
        min_zoom=5,
        max_zoom=28,

    ).add_to(map)

    # map.fitBounds([[25.070000143523796, -77.30999926807162], [25.07999999999999, -77.322]])
    tiles_source = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' #'https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg'

    attr_source = " " #'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    raster_t = folium.raster_layers.TileLayer(name="Stadia_Map", tiles=tiles_source, attr=attr_source)

    white = folium.TileLayer(title="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAAA1BMVEX///+nxBvIAAAAH0lEQVQYGe3BAQ0AAADCIPunfg43YAAAAAAAAAAA5wIhAAAB9aK9BAAAAABJRU5ErkJggg==",
                             minZoom=10,max_zoom=30, show=True)
    white.add_to(map)

    # Anchor_image = "https://github.com/lawls76/Anchor_Cache/tree/4cbc26bfcb6f0e9ed65f71f58ab27968437d617b/Anchor_BMap"
    # Anchor_files = "/{z}/{x}/{y}"
    # Anchor_image_join = Anchor_image + Anchor_files
    #
    # if not os.path.exists(Anchor_image_join):
    #     print(f"Could not find{Anchor_image}")
    # else:
    #     # Anchor_image_join = 'https://{s}' + Anchor_image + Anchor_files
    #     raster_Anchor = folium.raster_layers.TileLayer(name='The Anchor', image=Anchor_image_join, overlay=True, attr=' ')
    #     raster_Anchor.add_to(map)
    raster_t.add_to(map)



    folium.CircleMarker(
        location=P,
        radius=200,
        popup="Hurricane Hole Nassau Bahamas",
        color="crimson",
        fill=False,
        max_zoom=17
         ).add_to(map)    

# @app.route('/geojson')
# #


# def get_layer_seat():
    """Get the GeoJSON data and add to map"""
    map._id = 'live'

    site_root = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(site_root, 'static/Data', 'Seat_Slip_New.geojson')
    # GeoJSON Loading of data Getter
    data_geojson_dict = geojson.load(open(json_url))
    data_geojson_json = json.load(open(json_url))
    prop = {
        "image_url": "https://github.com/lawls76/Anchor_Cache/raw/working/Anchor_Seating_Images/3D_Design_2top.svg"}
        # if index_1 != 0:
    for data_json in data_geojson_json["features"]:
        dict(data_json)["properties"].update(prop)
    # for index_1 in range(len(data_json["properties"])):

        jsonl = dict(data_json)
        # print(jsonl["features"][i])

        try:
            # for featurel in jsonl:

            popup = create_popup(data_json["properties"])
            folium.Marker(location=[data_json['geometry']['coordinates'][0][0][0][1],
                                data_json['geometry']['coordinates'][0][0][0][0]],
                  popup=popup).add_to(map)

        except Exception as e:
            if e == KeyError('image_url'):
                pass
            else:
                print(e)
                

    layer_geom = folium.FeatureGroup(name='Seating_Slip.geojson', control=False)
    list_tooltip_vars = ['Type', 'Ticket Num', 'Descrip', 'Site Code', 'Ticket Qty', 'Unit Price']
    for i in range(len(data_geojson_dict["features"])):

        # print(data_geojson_dict["features"][i]['geometry']['coordinates'][0][0][0][1])
        temp_geojson = {"features": [data_geojson_dict["features"][i]],"type": "FeatureCollection"}
        temp_geojson_layer = folium.GeoJson(temp_geojson,
                                            highlight_function=lambda x: {'weight': 3, 'color': 'black'},
                                            control=False,
                                            style_function=lambda feature: {
                                                'color': 'black',
                                                'weight': 1},
                                            tooltip=folium.features.GeoJsonTooltip(fields=list_tooltip_vars,
                                                                                   aliases=[x.capitalize() + ":" for x
                                                                                            in list_tooltip_vars],
                                                                                   labels=True,
                                                                                   sticky=False,
                                                                                   localize=True
                                                                                   ),
                                            popup=folium.GeoJsonPopup(fields=list_tooltip_vars,
                                                                      labels=True, localize=True)
                                            ).add_to(map)
    temp_geojson_layer.add_to(layer_geom)
        
    layer_geom.add_to(map)
    folium.LayerControl(autoZIndex=False, collapsed=True).add_to(map)

    _ = map._repr_html_()  # must call ._repr_html_() before .get_root()
    script = map.get_root().script.render()
    header = map.get_root().header.render()
    html = map.get_root().html.render()

    context = {}
    context['head'] = header
    context['body'] = html
    context['scripts'] = script

    # Save as HTML file
    # map.save("popup_index.html")
    # get_layer_seat().add_to(map)

    return render_template_string(HTML, **context)


HTML="""<!doctype html
<html lang="en">
  <head>
            <meta charset="utf-8">
            <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes' />
            <title>The Anchor</title>

            <!-- Leaflet -->
            <!--link rel="stylesheet" href="https://unpkg.com/leaflet@0.7.5/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@0.7.5/dist/leaflet.js"></script>-->

            <style>
                body { margin:0; padding:0; }
                body, table, tr, td, th, div, h1, h2, input { font-family: "Calibri", "Trebuchet MS", "Ubuntu", Serif; font-size: 11pt; }
                #map { position:absolute; top:0; bottom:0; width:100%; } /* full size */
                .ctl {
                    padding: 2px 10px 2px 10px;
                    background: white;
                    background: rgba(255,255,255,0.9);
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                    border-radius: 5px;
                    text-align: right;
                }
                .title {
                    font-size: 18pt;
                    font-weight: bold;
                }
                .src {
                    font-size: 10pt;
                }

            </style>

        </head>
<!-- head -->
{{head|safe}}
<!-- head -->
</head>
<body>
<!-- body -->
{{body|safe}}
<!-- body -->
<script>
/* scripts */
{{scripts|safe}}
/* scripts */
/*
(function () {
    var geojsonFeatures;
    function update_position() {
        $.getJSON('/geojson', function (data) {
            console.log(data);
            if (geojsonFeatures){
                map_live.removeLayer(geojsonFeatures);
            }
            geojsonFeatures = L.geoJSON(data, {
            });
            geojsonFeatures.addTo(map_live);

        });
        setTimeout(update_position, 1000);
    }
     update_position();
})();
*/
</script>
</body>
</html>
"""

# """<!DOCTYPE html>
# <html lang="en">
#   <head>
#     <meta charset="utf-8">
#     <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' />
#     <title>merge_out.vrt</title>
#
#     <!-- Leaflet -->
#     <link rel="stylesheet" href="https://unpkg.com/leaflet@0.7.5/dist/leaflet.css" />
#     <script src="https://unpkg.com/leaflet@0.7.5/dist/leaflet.js"></script>
#
#     <style>
#         body { margin:0; padding:0; }
#         body, table, tr, td, th, div, h1, h2, input { font-family: "Calibri", "Trebuchet MS", "Ubuntu", Serif; font-size: 11pt; }
#         #map { position:absolute; top:0; bottom:0; width:100%; } /* full size */
#         .ctl {
#             padding: 2px 10px 2px 10px;
#             background: white;
#             background: rgba(255,255,255,0.9);
#             box-shadow: 0 0 15px rgba(0,0,0,0.2);
#             border-radius: 5px;
#             text-align: right;
#         }
#         .title {
#             font-size: 18pt;
#             font-weight: bold;
#         }
#         .src {
#             font-size: 10pt;
#         }
#
#     </style>
#
# </head>
# <body>
# /* scripts */
# /*
# (function () {
#     var geojsonFeatures;
#     function update_position() {
#         $.getJSON('/geojson', function (data) {
#             console.log(data);
#             if (geojsonFeatures){
#                 map_live.removeLayer(geojsonFeatures);
#             }
#             geojsonFeatures = L.geoJSON(data, {
#             });
#             geojsonFeatures.addTo(map_live);
#
#         });
#         setTimeout(update_position, 1000);
#     }
# #     update_position();
# })();
# */
# </script>
# < / body >
# < / html >"""







# """<!doctype html
# <html lang="en">
#   <head>
#     <meta charset="utf-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
# <!-- head -->
# {{head|safe}}
# <!-- head -->
# </head>
# <body>
# <!-- body -->
# {{body|safe}}
# <!-- body -->
# <script>
# /* scripts */
# {{scripts|safe}}
# /* scripts */
# /*
# (function () {
#     var geojsonFeatures;
#     function update_position() {
#         $.getJSON('/geojson', function (data) {
#             console.log(data);
#             if (geojsonFeatures){
#                 map_live.removeLayer(geojsonFeatures);
#             }
#             geojsonFeatures = L.geoJSON(data, {
#             });
#             geojsonFeatures.addTo(map_live);
#
#         });
#         setTimeout(update_position, 1000);
#     }
# #     update_position();
# })();
# */
# </script>
# </body>
# </html>
# """


if __name__ == '__main__':
    app.run(debug=True)