from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

_LEAFLET_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
  html, body {{ margin: 0; padding: 0; height: 100%; }}
  #map {{ position: absolute; top: 0; bottom: 0; left: 0; right: 0; }}
  #search-box {{
    position: absolute; top: 10px; left: 60px; z-index: 1000;
    background: white; padding: 6px; border-radius: 6px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3); display: flex; gap: 4px;
  }}
  #search-input {{
    border: 1px solid #ccc; border-radius: 4px; padding: 6px 8px;
    font-size: 13px; width: 260px;
  }}
  #search-btn {{
    background: #3b82f6; color: white; border: none; border-radius: 4px;
    padding: 6px 12px; cursor: pointer; font-size: 13px;
  }}
  #search-btn:hover {{ background: #2563eb; }}
  #coords-label {{
    position: absolute; bottom: 10px; left: 10px; z-index: 1000;
    background: rgba(255,255,255,0.9); padding: 4px 8px; border-radius: 4px;
    font-size: 12px; color: #333;
  }}
</style>
</head>
<body>
<div id="search-box">
  <input id="search-input" type="text" placeholder="Buscar direccion..."/>
  <button id="search-btn" onclick="doSearch()">Buscar</button>
</div>
<div id="map"></div>
<div id="coords-label">Coordenadas: -</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
var map = L.map('map').setView([19.4326, -99.1332], 13);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  attribution: '&copy; OpenStreetMap', maxZoom: 19
}}).addTo(map);

var marker = null;
var latInput = {lat};
var lngInput = {lng};
var reverseAddress = '';

if (latInput && lngInput) {{
  marker = L.marker([latInput, lngInput], {{draggable: true}}).addTo(map);
  map.setView([latInput, lngInput], 16);
  updateCoords(latInput, lngInput);
  marker.on('dragend', function(e) {{
    var pos = e.target.getLatLng();
    updateCoords(pos.lat, pos.lng);
  }});
}}

map.on('click', function(e) {{
  if (marker) marker.setLatLng(e.latlng);
  else {{
    marker = L.marker(e.latlng, {{draggable: true}}).addTo(map);
    marker.on('dragend', function(ev) {{
      var p = ev.target.getLatLng();
      updateCoords(p.lat, p.lng);
    }});
  }}
  updateCoords(e.latlng.lat, e.latlng.lng);
}});

function updateCoords(lat, lng) {{
  document.getElementById('coords-label').textContent =
    'Coordenadas: ' + lat.toFixed(5) + ', ' + lng.toFixed(5);
  reverseGeocode(lat, lng);
}}

function reverseGeocode(lat, lng) {{
  var url = 'https://nominatim.openstreetmap.org/reverse?format=json&lat=' +
    lat + '&lon=' + lng + '&limit=1';
  fetch(url, {{headers: {{'Accept': 'application/json'}}}})
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
      if (data && data.display_name) {{
        reverseAddress = data.display_name;
        document.getElementById('coords-label').textContent =
          'Coordenadas: ' + lat.toFixed(5) + ', ' + lng.toFixed(5) +
          ' | ' + reverseAddress;
      }}
    }})
    .catch(function() {{}});
}}

function doSearch() {{
  var q = document.getElementById('search-input').value;
  if (!q) return;
  var url = 'https://nominatim.openstreetmap.org/search?format=json&q=' +
    encodeURIComponent(q) + '&limit=1';
  fetch(url, {{headers: {{'Accept': 'application/json'}}}})
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
      if (data && data.length > 0) {{
        var lat = parseFloat(data[0].lat);
        var lng = parseFloat(data[0].lon);
        reverseAddress = data[0].display_name || '';
        if (marker) marker.setLatLng([lat, lng]);
        else {{
          marker = L.marker([lat, lng], {{draggable: true}}).addTo(map);
          marker.on('dragend', function(ev) {{
            var p = ev.target.getLatLng();
            updateCoords(p.lat, p.lng);
          }});
        }}
        map.setView([lat, lng], 16);
        updateCoords(lat, lng);
      }} else {{
        alert('No se encontro la direccion. Intenta con una mas especifica.');
      }}
    }})
    .catch(function() {{
      alert('Error al buscar. Verifica tu conexion a internet.');
    }});
}}

document.getElementById('search-input').addEventListener('keydown', function(e) {{
  if (e.key === 'Enter') {{ e.preventDefault(); doSearch(); }}
}});

// Expose for Python to read
window._getCoords = function() {{
  if (!marker) return null;
  var pos = marker.getLatLng();
  return {{lat: pos.lat, lng: pos.lng, address: reverseAddress}};
}};
</script>
</body>
</html>"""


class MapDialog(QDialog):
    def __init__(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("📍 Seleccionar ubicacion")
        self.resize(700, 550)
        self._latitude: float | None = latitude
        self._longitude: float | None = longitude
        self._reverse_address: str = ""

        self._web_view = QWebEngineView()
        html = _LEAFLET_HTML.format(
            lat=self._latitude if self._latitude else "null",
            lng=self._longitude if self._longitude else "null",
        )
        self._web_view.setHtml(html, QUrl("https://unpkg.com/"))

        self._coords_label = QLabel("Coordenadas: -")
        if self._latitude is not None and self._longitude is not None:
            self._coords_label.setText(
                f"Coordenadas: {self._latitude:.5f}, {self._longitude:.5f}"
            )

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._web_view, 1)
        layout.addWidget(self._coords_label)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        # Read coordinates from the JS marker
        self._web_view.page().runJavaScript(
            "window._getCoords ? window._getCoords() : null",
            0,
            self._read_coords,
        )

    def _read_coords(self, result) -> None:
        if result and isinstance(result, dict):
            self._latitude = result.get("lat")
            self._longitude = result.get("lng")
            self._reverse_address = result.get("address") or ""
        if self._latitude is not None and self._longitude is not None:
            self.accept()
        else:
            # No marker placed
            self.reject()

    @property
    def latitude(self) -> float | None:
        return self._latitude

    @property
    def longitude(self) -> float | None:
        return self._longitude

    @property
    def reverse_address(self) -> str:
        return self._reverse_address
