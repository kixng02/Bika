/* ===== Bika Map – MapLibre GL + GeoNames clustering ===== */

const GEONAMES_URL =
  'https://secure.geonames.org/searchJSON' +
  '?formatted=true&q=nature%20reserve&country=ZA&maxRows=100&lang=en&username=kxngmali&style=full';

const FALLBACK_RESERVES = [
  { name: 'Kruger National Park',         lng: 31.4913, lat: -23.9884, adminName1: 'Limpopo' },
  { name: 'Table Mountain NP',            lng: 18.4097, lat: -34.0000, adminName1: 'Western Cape' },
  { name: 'Addo Elephant NP',             lng: 25.7469, lat: -33.4820, adminName1: 'Eastern Cape' },
  { name: 'iSimangaliso Wetland Park',    lng: 32.5333, lat: -27.9667, adminName1: 'KwaZulu-Natal' },
  { name: 'Hluhluwe-iMfolozi Park',       lng: 31.9167, lat: -28.0833, adminName1: 'KwaZulu-Natal' },
  { name: 'Kgalagadi Transfrontier Park', lng: 20.5833, lat: -26.5000, adminName1: 'Northern Cape' },
  { name: 'Pilanesberg NP',               lng: 27.0833, lat: -25.2500, adminName1: 'North West' },
  { name: 'Golden Gate Highlands NP',     lng: 28.6167, lat: -28.5000, adminName1: 'Free State' },
  { name: 'Bontebok NP',                  lng: 20.4583, lat: -34.0583, adminName1: 'Western Cape' },
  { name: 'Mountain Zebra NP',            lng: 25.6667, lat: -32.2500, adminName1: 'Eastern Cape' },
  { name: 'Mapungubwe NP',                lng: 29.3667, lat: -22.2000, adminName1: 'Limpopo' },
  { name: 'Marakele NP',                  lng: 27.4667, lat: -24.4333, adminName1: 'Limpopo' },
  { name: 'Augrabies Falls NP',           lng: 20.3333, lat: -28.5833, adminName1: 'Northern Cape' },
  { name: 'Richtersveld NP',              lng: 17.2333, lat: -28.2667, adminName1: 'Northern Cape' },
  { name: 'Tsitsikamma NP',               lng: 23.9167, lat: -33.9333, adminName1: 'Eastern Cape' },
  { name: 'West Coast NP',                lng: 18.1167, lat: -33.2500, adminName1: 'Western Cape' },
  { name: 'Tankwa Karoo NP',              lng: 19.9333, lat: -32.1667, adminName1: 'Northern Cape' },
  { name: 'Camdeboo NP',                  lng: 25.5833, lat: -31.5667, adminName1: 'Eastern Cape' },
  { name: 'Namaqua NP',                   lng: 17.2333, lat: -29.2667, adminName1: 'Northern Cape' },
  { name: 'Boulders Penguin Colony',      lng: 18.4500, lat: -34.1978, adminName1: 'Western Cape' },
];

const C = { light:'#74c69d', mid:'#40916c', dark:'#1b4332', pin:'#2d6a4f', white:'#ffffff' };

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://tiles.openfreemap.org/styles/liberty',
  center: [25.0, -29.0],
  zoom: 5,
  attributionControl: false,
});

map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');
map.addControl(new maplibregl.NavigationControl(), 'top-right');
map.addControl(new maplibregl.FullscreenControl(), 'top-right');
map.addControl(new maplibregl.GeolocateControl({ positionOptions: { enableHighAccuracy: true }, trackUserLocation: false }), 'top-right');

function toGeoJSON(places) {
  return {
    type: 'FeatureCollection',
    features: places.map(p => {
      const lng = parseFloat(p.lng), lat = parseFloat(p.lat);
      if (isNaN(lng) || isNaN(lat)) return null;
      return {
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [lng, lat] },
        properties: {
          name:        p.name        || '',
          adminName1:  p.adminName1  || '',
          countryName: p.countryName || 'South Africa',
          fcodeName:   p.fcodeName   || '',
          elevation:   p.elevation   || '',
        },
      };
    }).filter(Boolean),
  };
}

let activePopup = null;
function showPopup(lngLat, props) {
  if (activePopup) activePopup.remove();
  activePopup = new maplibregl.Popup({ closeButton: true, maxWidth: '260px', offset: 10 })
    .setLngLat(lngLat)
    .setHTML(`
      <div class="popup-title">${props.name || 'Nature Reserve'}</div>
      <div class="popup-sub">
        ${props.adminName1 ? `${props.adminName1} &middot; ` : ''}
        ${props.countryName || 'South Africa'}
      </div>
      ${props.fcodeName ? `<div class="popup-sub" style="margin-top:4px;font-style:italic;">${props.fcodeName}</div>` : ''}
      ${props.elevation  ? `<div class="popup-sub">Elevation: ${props.elevation} m</div>` : ''}
    `)
    .addTo(map);
}

function loadData(fc) {
  map.getSource('reserves').setData(fc);
  if (!fc.features.length) return;
  const lngs = fc.features.map(f => f.geometry.coordinates[0]);
  const lats  = fc.features.map(f => f.geometry.coordinates[1]);
  map.fitBounds(
    [[Math.min(...lngs), Math.min(...lats)], [Math.max(...lngs), Math.max(...lats)]],
    { padding: 60, maxZoom: 7, duration: 800 }
  );
}

map.on('load', () => {

  map.addSource('reserves', {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] },
    cluster: true,
    clusterMaxZoom: 6,   // individual markers visible from zoom 7+
    clusterRadius: 40,
  });

  // Cluster circles
  map.addLayer({
    id: 'clusters', type: 'circle', source: 'reserves',
    filter: ['has', 'point_count'],
    paint: {
      'circle-color': ['step', ['get', 'point_count'], C.light, 5, C.mid, 20, C.dark],
      'circle-radius': ['step', ['get', 'point_count'], 20, 5, 28, 20, 38],
      'circle-stroke-width': 3,
      'circle-stroke-color': C.white,
    },
  });

  // Cluster count labels
  map.addLayer({
    id: 'cluster-count', type: 'symbol', source: 'reserves',
    filter: ['has', 'point_count'],
    layout: {
      'text-field': ['get', 'point_count_abbreviated'],
      'text-font': ['Noto Sans Bold', 'Arial Unicode MS Bold'],
      'text-size': 13,
    },
    paint: { 'text-color': C.white },
  });

  // Individual point — plain circle, no custom image needed
  map.addLayer({
    id: 'unclustered-point', type: 'circle', source: 'reserves',
    filter: ['!', ['has', 'point_count']],
    paint: {
      'circle-radius': 9,
      'circle-color': C.pin,
      'circle-stroke-width': 2.5,
      'circle-stroke-color': C.white,
    },
  });

  // Interactions
  map.on('click', 'clusters', e => {
    const f = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
    const src = map.getSource('reserves');
    const center = f[0].geometry.coordinates;
    const clusterId = f[0].properties.cluster_id;
    // MapLibre v4 returns a Promise; v3 uses a callback — support both
    const result = src.getClusterExpansionZoom(clusterId);
    if (result && typeof result.then === 'function') {
      result.then(zoom => map.easeTo({ center, zoom }));
    } else {
      src.getClusterExpansionZoom(clusterId, (err, zoom) => {
        if (!err) map.easeTo({ center, zoom });
      });
    }
  });

  map.on('click', 'unclustered-point', e => {
    showPopup(e.features[0].geometry.coordinates.slice(), e.features[0].properties);
  });

  ['clusters', 'unclustered-point'].forEach(layer => {
    map.on('mouseenter', layer, () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', layer, () => { map.getCanvas().style.cursor = ''; });
  });

  const countEl = document.getElementById('reserveCount');

  fetch(GEONAMES_URL)
    .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
    .then(data => {
      const places = (data.geonames || []).filter(p => p.lng && p.lat);
      if (!places.length) throw new Error('empty');
      if (countEl) countEl.textContent = places.length + ' reserves loaded';
      loadData(toGeoJSON(places));
    })
    .catch(err => {
      console.warn('GeoNames fallback:', err.message);
      if (countEl) countEl.textContent = FALLBACK_RESERVES.length + ' reserves loaded';
      loadData(toGeoJSON(FALLBACK_RESERVES));
    });
});
