# -*- coding: utf-8 -*-

"""
# Python Flask Folium GeoJson Leaflet Ajax (Jquery) Sample
I couldn't find a simple example of how to combine Folium with an AJAX / getJson call.
1. Generate Folium Map with some static map features
2. Render to Template View with `render_template_string`
3. jquery Ajax call polls `/geojson` with `getJson`
4. Leafletjs renders the GeoJson
```sh
pip install Flask==2.2.2 geojson==2.5.0 folium==0.13.0
```
# Notes
- note `geojson` and `folium`, latitude and longitude order is reversed
- the `._id` of the folium map must explicitly defined: `live`
- we access the global variable in JS created by folium with jquery: `map_live`
- GeoJson features get rendered into their own layer
- The GeoJson Layer is deleted per ajax call
# References
- https://python-visualization.github.io/folium/
- https://python-geojson.readthedocs.io/en/latest/
"""
import os
from flask import Flask, jsonify, render_template_string, Response, json
import geojson
import folium
import datetime

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
    # tiles = "file:///home/lawls/Documents/Driftwood/Anchor_BMap/TheAnchor_Basemap/TheAnchor_Basemap/{z}/{x}/{y}.png"
    map = folium.Map(location=P, zoom_start=11)#, tiles=tiles)
    map._id = 'live'


    folium.CircleMarker(
        location=P,
        radius=50,
        popup="Hurricane Hole Nassau Bahamas",
        color="crimson",
        fill=False,
    ).add_to(map)

    _ = map._repr_html_()  # must call ._repr_html_() before .get_root()
    script = map.get_root().script.render()
    header = map.get_root().header.render()
    html = map.get_root().html.render()

    context = {}
    context['head'] = header
    context['body'] = html
    context['scripts'] = script

    # return render_template_string(HTML, **context)
    return render_template_string(HTML, **context)


@app.route('/geojson')
def gps():
    td = (now() - T0).seconds / 200.

    # generate some geometry and put into a collection
    p1 = geojson.Point([LONGITUDE, LATITUDE + td])
    p2 = geojson.Point([LONGITUDE + td, LATITUDE])
    l = geojson.LineString([p1, p2])
    collection = geojson.GeometryCollection([p1, p2, l])

    # can just jsonify it: return jsonify(collection)
    # we'll explicitly use the geojson's dumps function
    j = geojson.dumps(collection, sort_keys=True)
    return Response(j, mimetype='application/json')


# our HTML string
HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
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
</script>
</body>
</html>
    """

# if __name__ == '__main__':
#     app.run(debug=True)