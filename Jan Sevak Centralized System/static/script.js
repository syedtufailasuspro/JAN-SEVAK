async function fetchCases() {
    const response = await fetch('/get-active-cases');
    const cases = await response.json();

    const container = document.getElementById('cases-container');
    container.innerHTML = "";

    cases.forEach(caseData => {
        const caseDiv = document.createElement('div');
        caseDiv.classList.add('case');
        caseDiv.innerHTML = `
            <h2>🚨 Emergency Case #${caseData.case_id}</h2>
            <p><strong>📍 Location:</strong> ${caseData.location}</p>
            <p><strong>🚑 Assigned Ambulance:</strong> Ambulance ${caseData.case_id}</p>
            <p><strong>🏥 Hospital Assigned:</strong> ${caseData.hospital_assigned || 'Not Assigned'}</p>
            <p><strong>⏳ Status:</strong> ${caseData.status}</p>
            <button class="close-case-btn button danger-button" data-case-id="${caseData.case_id}">
                <span class="icon">✅</span> Close Case
            </button>
        `;
        container.appendChild(caseDiv);
    });

    // Add event listeners to all close buttons
    document.querySelectorAll('.close-case-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const caseId = this.getAttribute('data-case-id');
            try {
                const response = await fetch('/close-case', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ case_id: caseId })
                });
                if (response.ok) {
                    fetchCases(); // Refresh the cases
                }
            } catch (error) {
                console.error('Error closing case:', error);
            }
        });
    });
}

setInterval(fetchCases, 5000);  // Update every 5 seconds
fetchCases();

// Hotspots Map Modal functionality
document.getElementById('view-hotspots').addEventListener('click', async function() {
    const modal = document.getElementById('hotspots-modal');
    modal.style.display = 'block';
    
    // Initialize map if not already done
    if (!window.hotspotsMap) {
        window.hotspotsMap = L.map('hotspots-map').setView([20.5937, 78.9629], 5); // Default to India view
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(window.hotspotsMap);
    }
    
    // Fetch hotspots data
    const response = await fetch('/get-accident-hotspots');
    const hotspots = await response.json();
    
    // Clear existing markers
    if (window.hotspotMarkers) {
        window.hotspotMarkers.forEach(marker => window.hotspotsMap.removeLayer(marker));
    }
    window.hotspotMarkers = [];
    
    // Add new markers
    hotspots.forEach(hotspot => {
        const lat = parseFloat(hotspot.lat);
        const lng = parseFloat(hotspot.lng);
        const count = parseInt(hotspot.count);
        
        const radius = Math.min(20 + (count * 0.05), 50); // Scale radius based on count
        
        const circle = L.circle([lat, lng], {
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.5,
            radius: radius * 10 // Convert to meters
        }).addTo(window.hotspotsMap);
        
        circle.bindPopup(`<b>Accident Hotspot</b><br>Accidents: ${count}`);
        window.hotspotMarkers.push(circle);
    });
    
    // Fit map to show all hotspots
    if (hotspots.length > 0) {
        const bounds = L.latLngBounds(hotspots.map(h => [parseFloat(h.lat), parseFloat(h.lng)]));
        window.hotspotsMap.fitBounds(bounds, { padding: [50, 50] });
    }
});

// Close modal functionality
document.querySelectorAll('.close-modal').forEach(button => {
    button.addEventListener('click', function() {
        this.closest('.modal').style.display = 'none';
    });
});

window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});

// Statistics Modal functionality
// Statistics Modal functionality
document.getElementById('view-statistics').addEventListener('click', async function() {
    const modal = document.getElementById('statistics-modal');
    modal.style.display = 'block';
    
    // Ensure canvas is ready
    const canvas = document.getElementById('accidents-chart');
    canvas.style.display = 'block';
    const ctx = canvas.getContext('2d');
    
    try {
        const response = await fetch('/get-accident-statistics');
        const stats = await response.json();
        
        console.log('Statistics data:', stats); // Debug logging
        
        // Destroy previous chart if exists
        if (window.accidentsChart) {
            window.accidentsChart.destroy();
        }
        
        // Prepare hourly data (fill empty hours with 0)
        const hourlyLabels = Array.from({length: 24}, (_, i) => `${i}:00`);
        const hourlyData = Array(24).fill(0);
        if (stats.hourly) {
            stats.hourly.forEach(item => {
                const hour = parseInt(item.hour);
                if (hour >= 0 && hour < 24) {
                    hourlyData[hour] = item.count || 0;
                }
            });
        }
        
        // Create the chart
        window.accidentsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: hourlyLabels,
                datasets: [{
                    label: 'Accidents by Hour of Day',
                    data: hourlyData,
                    backgroundColor: 'rgba(231, 57, 70, 0.7)',
                    borderColor: 'rgba(231, 57, 70, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Accidents'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Hour of Day'
                        }
                    }
                }
            }
        });
        
        // If no data exists, show message
        if ((!stats.hourly || stats.hourly.length === 0) && 
            (!stats.daily || stats.daily.length === 0)) {
            canvas.style.display = 'none';
            const noDataMsg = document.createElement('div');
            noDataMsg.textContent = 'No accident statistics available yet';
            noDataMsg.style.textAlign = 'center';
            noDataMsg.style.padding = '20px';
            noDataMsg.style.color = '#666';
            document.querySelector('.chart-container').appendChild(noDataMsg);
        }
        
    } catch (error) {
        console.error('Error loading statistics:', error);
        canvas.style.display = 'none';
        const errorMsg = document.createElement('div');
        errorMsg.textContent = 'Failed to load statistics';
        errorMsg.style.textAlign = 'center';
        errorMsg.style.padding = '20px';
        errorMsg.style.color = 'red';
        document.querySelector('.chart-container').appendChild(errorMsg);
    }
});
