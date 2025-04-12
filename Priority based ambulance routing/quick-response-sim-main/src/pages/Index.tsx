
import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapContainer, TileLayer, useMap, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { createAmbulanceIcon, addRoute, calculateAmbulanceScores } from "@/lib/ambulanceUtils";
import AmbulanceScoreList from "@/components/AmbulanceScoreList";

// Import Leaflet CSS
import "leaflet/dist/leaflet.css";
import "leaflet-routing-machine/dist/leaflet-routing-machine.css";

const Index = () => {
  const [ambulances, setAmbulances] = useState([
    { id: 1, coords: [13.0727, 80.2707] as [number, number], severity: 5, eta: 4, color: "green", score: 0 },  // South
    { id: 2, coords: [13.0827, 80.2807] as [number, number], severity: 3, eta: 2, color: "red", score: 0 }     // East
  ]);
  const [mapLoaded, setMapLoaded] = useState(false);
  const mapRef = useRef<L.Map | null>(null);
  const intersection: [number, number] = [13.0827, 80.2707];
  
  // Calculate scores when component mounts
  useEffect(() => {
    const scoredAmbulances = calculateAmbulanceScores(ambulances);
    setAmbulances(scoredAmbulances);
  }, []);

  // Initialize map routes once map is loaded
  useEffect(() => {
    if (!mapLoaded) return;
    
    const map = mapRef.current;
    if (!map) return;
    
    // Sort ambulances by score (descending)
    const sortedAmbulances = [...ambulances].sort((a, b) => b.score - a.score);
    const [priorityAmbulance, secondaryAmbulance] = sortedAmbulances;
    
    // Add routes in sequence
    if (priorityAmbulance && map) {
      addRoute(map, priorityAmbulance, intersection, () => {
        if (secondaryAmbulance) {
          setTimeout(() => {
            addRoute(map, secondaryAmbulance, intersection);
          }, 1000); // Red waits 1s after green finishes
        }
      });
    }
  }, [mapLoaded, ambulances, intersection]);
  
  // Map initialization component
  const MapInitializer = () => {
    const map = useMap();
    
    useEffect(() => {
      mapRef.current = map;
      setMapLoaded(true);
    }, [map]);
    
    return null;
  };
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center text-primary">
        Ambulance Priority Simulation
      </h1>
      
      <Card className="mb-6 shadow-lg">
        <CardContent className="p-0">
          <div className="h-[600px] w-full">
            <MapContainer
              center={[13.0827, 80.2707]}
              zoom={14}
              style={{ height: "100%", width: "100%" }}
              whenReady={() => {}}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapInitializer />
            </MapContainer>
          </div>
        </CardContent>
      </Card>
      
      <Card className="shadow-md">
        <CardHeader className="bg-muted/50">
          <CardTitle className="flex items-center">
            <span className="text-red-500 mr-2">🚑</span>
            <span>Ambulance Priority Scores</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AmbulanceScoreList ambulances={ambulances} />
        </CardContent>
      </Card>
    </div>
  );
};

export default Index;
