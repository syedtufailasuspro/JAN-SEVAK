
import React from 'react';
import { cn } from "@/lib/utils";

interface Ambulance {
  id: number;
  severity: number;
  eta: number;
  score: number;
  color: string;
  coords: [number, number];
}

interface AmbulanceScoreListProps {
  ambulances: Ambulance[];
}

const AmbulanceScoreList: React.FC<AmbulanceScoreListProps> = ({ ambulances }) => {
  // Sort ambulances by score (descending)
  const sortedAmbulances = [...ambulances].sort((a, b) => b.score - a.score);
  const priorityAmbulanceId = sortedAmbulances.length > 0 ? sortedAmbulances[0].id : null;

  return (
    <div className="space-y-3">
      {sortedAmbulances.map((ambulance) => (
        <div 
          key={ambulance.id}
          className={cn(
            "p-3 rounded-md border transition-all hover:shadow-md",
            ambulance.id === priorityAmbulanceId 
              ? "border-l-4 border-l-green-500 bg-green-50 dark:bg-green-950/30" 
              : "border-l-4 border-gray-200"
          )}
        >
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <span className="mr-2">🚑</span>
              <span className="font-semibold">
                Ambulance {ambulance.id} 
                {ambulance.id === priorityAmbulanceId && (
                  <span className="ml-2 text-green-600 dark:text-green-400">(Priority)</span>
                )}
              </span>
            </div>
            <div className="bg-primary/10 text-primary font-mono py-1 px-2 rounded-md">
              Score: {ambulance.score}
            </div>
          </div>
          <div className="mt-2 text-sm text-muted-foreground grid grid-cols-2 gap-2">
            <div>Severity: {ambulance.severity}</div>
            <div>ETA: {ambulance.eta} min</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AmbulanceScoreList;
