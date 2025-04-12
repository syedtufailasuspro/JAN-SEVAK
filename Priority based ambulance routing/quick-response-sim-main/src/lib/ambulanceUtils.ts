
import L from "leaflet";
import "leaflet-routing-machine";

// Create a custom ambulance icon
export function createAmbulanceIcon(color: string) {
  return L.divIcon({
    className: 'ambulance-icon pulse',
    html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" stroke="#fff" stroke-width="1">
            <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zm-7 1H8V6h5v3zm-1 10c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-8 0c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm1-7.5h4V9H5v2.5zm12 7.5c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
            <path d="M11 14h2v2h-2zm0-4h2v2h-2z" fill="#ffffff"/>
          </svg>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  });
}

// Add a route for an ambulance
export function addRoute(
  map: L.Map, 
  amb: { id: number; coords: [number, number]; severity: number; eta: number; color: string; score: number },
  intersection: [number, number],
  callback?: () => void
) {
  const routeControl = L.Routing.control({
    waypoints: [
      L.latLng(amb.coords[0], amb.coords[1]),
      L.latLng(intersection[0], intersection[1])
    ],
    lineOptions: {
      styles: [{color: amb.color, weight: 5, opacity: 0.8}],
      extendToWaypoints: true,
      missingRouteTolerance: 0
    },
    createMarker: () => null,
    addWaypoints: false,
    draggableWaypoints: false,
    fitSelectedRoutes: false,
    show: false // Don't show the route instructions panel
  }).addTo(map);

  routeControl.on('routesfound', function(e) {
    const route = e.routes[0].coordinates;
    const ambulanceIcon = createAmbulanceIcon(amb.color);
    
    const marker = L.marker([amb.coords[0], amb.coords[1]], {
      icon: ambulanceIcon
    }).addTo(map).bindPopup(`🚑 Ambulance ${amb.id}<br>Severity: ${amb.severity}<br>ETA: ${amb.eta}<br>Score: ${amb.score}`).openPopup();

    let i = 0;
    function move() {
      if (i < route.length) {
        marker.setLatLng([route[i].lat, route[i].lng]);
        
        // Calculate direction for next point if available
        if (i < route.length - 1) {
          const dx = route[i+1].lng - route[i].lng;
          const dy = route[i+1].lat - route[i].lat;
          const angle = Math.atan2(dy, dx) * 180 / Math.PI;
          // If you want to rotate the icon based on direction:
          // marker.setRotationAngle(angle);
        }
        
        i++;
        setTimeout(move, 40);
      } else {
        if (callback) callback();
      }
    }
    move();
  });
}

// Calculate priority scores for ambulances
export function calculateAmbulanceScores(ambulances: Array<{ id: number; severity: number; eta: number; color: string; coords: [number, number] }>) {
  return ambulances.map(amb => ({
    ...amb,
    score: parseFloat(((amb.severity * 0.7) + ((1 / amb.eta) * 0.3)).toFixed(2))
  }));
}
