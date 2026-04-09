
import json
import os

import geojson
from geojson import Feature, Polygon, FeatureCollection
from flask import Flask, jsonify, render_template_string, Response, url_for
import folium
import datetime

import json

import httpx

from folium import Map, TileLayer


app = Flask(__name__)

# Center on Hurricane Hole Nassau Bahamas
LONGITUDE = -77.3193
LATITUDE = 25.07932



# small helper function
def now():
    return datetime.datetime.now()


T0 = now()


@app.route('/')
def index():
    P = [LATITUDE, LONGITUDE]
    # "/home/lawls/PycharmProjects/TileToTiff/merge.tiff" #"file:///home/lawls/Documents/Driftwood/Anchor_BMap/BM8/AnchorGeotiffgdal.tif"

    # map = folium.Map(max_zoom=33, min_zoom=0, zoom_start=18, zoom_control=True,
    #                  control_scale=True, crs="EPSG3857")
    titiler_endpoint = "https://titiler.xyz"  # Developmentseed Demo endpoint. Please be kind.
    url = "https://github.com/lawls76/Anchor_Cache/raw/working/Anchor_Seat_geo_update.tif"

    # Fetch File Metadata to get min/max rescaling values (because the file is stored as float32)
    r = httpx.get(
        f"{titiler_endpoint}/cog/info",
        params={
            "url": url,
        }
    ).json()

    bounds = r["bounds"]
    print(r)

    r = httpx.get(
        f"{titiler_endpoint}/cog/WebMercatorQuad/tilejson.json",
        params={
            "url": url,
        }
    ).json()

    map = Map(
        location=((bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2),
        zoom_start=17
    )

    TileLayer(
        tiles=r["tiles"][0],
        opacity=1,
        attr="DigitalGlobe OpenData",
        name="The Anchor",
        overlay=True,
        show=True,
        max_native_zoom=25,
        min_zoom=5,
        max_zoom=28
    ).add_to(map)
    # map.fitBounds([[25.070000143523796, -77.30999926807162], [25.07999999999999, -77.322]])
    tiles_source = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

    attr_source = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    raster_t = folium.raster_layers.TileLayer(name="ArcGISWorld", tiles=tiles_source, attr=attr_source)

    white = folium.TileLayer(title="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAAA1BMVEX///+nxBvIAAAAH0lEQVQYGe3BAQ0AAADCIPunfg43YAAAAAAAAAAA5wIhAAAB9aK9BAAAAABJRU5ErkJggg==",
                             minZoom=10,axZoom=30)
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

    # attr_Anchor = "(C) xyzservices"


    map._id = 'live'
    site_root = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(site_root, 'static/Data', 'Seat_Slip_New.geojson')
    # base_map = os.path.join(site_root, 'static/Data', 'TheAnchor_Basemap')
    # folium.TileLayer(base_map).add_to(map)

    data_geojson_dict = geojson.load(open(json_url))
    # data_geojson_dict = geojson.load(data_geojson_dict_obj)
    # folium.GeoJson(json_url).add_to(map)

    # folium.TileLayer(base_map).add_to(map)
    layer_geom = folium.FeatureGroup(name='Seating_Slip.geojson', control=False)
    list_tooltip_vars = ['Type', 'Ticket Num', 'Descrip','Site Code', 'Ticket Qty', 'Unit Price']
    for i in range(len(data_geojson_dict["features"])):
        temp_geojson = {"features": [data_geojson_dict["features"][i]], "type": "FeatureCollection"}
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
                                                                                   )
                                            )
        # point_offset =  temp_geojson_layer.
        folium.GeoJsonPopup(fields=list_tooltip_vars, localize=True).add_to(temp_geojson_layer)
        # folium.Popup(temp_geojson["features"][0]["properties"]["Descrip"]).add_to(temp_geojson_layer)
        temp_geojson_layer.add_to(layer_geom)

    layer_geom.add_to(map)
    folium.LayerControl(autoZIndex=False, collapsed=True).add_to(map)


    # folium.CircleMarker(
    #     location=P,
    #     radius=100,
    #     popup="Hurricane Hole Nassau Bahamas",
    #     color="crimson",
    #     fill=False,
    # ).add_to(map)

    _ = map._repr_html_()  # must call ._repr_html_() before .get_root()
    script = map.get_root().script.render()
    header = map.get_root().header.render()
    html = map.get_root().html.render()

    context = {}
    context['head'] = header
    context['body'] = html
    context['scripts'] = script
    # ticket()

    # return render_template_string(HTML, **context)
    return render_template_string(HTML, **context)

@app.route('/geojson')
#def gps():
    # td = (now() - T0).seconds / 200.

    # generate some geometry and put into a collection
    # p1 = geojson.Point([LONGITUDE, LATITUDE + td])
    # p2 = geojson.Point([LONGITUDE + td, LATITUDE])
    # l = geojson.LineString([p1, p2])
    # collection = geojson.GeometryCollection([p1, p2, l])

    # can just jsonify it: return jsonify(collection)
    # we'll explicitly use the geojson's dumps function
    # j = geojson.dumps(collection, sort_keys=True)
    # poly_ticket = geojson.Polygon()
    # j = geojson.dumps(poly_ticket,sort_keys=True)
    # return Response(j, mimetype='application/json')

    # static/data/TheAnchor_Ticket_Seat.json
def ticket():
    site_root = os.path.realpath(os.path.dirname(__file__))
    path = os.path.join(site_root, 'static/Data', 'Seating_Slip_Update.geojson')
    with open(path) as poly_ticket:
        #data = geojson.dumps(json, poly_ticket, encoding="utf-8")  # json.load(poly_ticket)
        print(poly_ticket)
    feature_coll = FeatureCollection(poly_ticket['features'])
    print(feature_coll)
    #j = geojson.Polygon(json_url)
    return Response(feature_coll, mimetype='application/json'), render_template_string(HTML, **context)
    # #data = json.load(open(filename))
    # j = geojson.dumps(poly_ticket, sort_keys=True)
    # return Response(j, mimetype='application/json')
    #return render_template(data=data)


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