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
        `;
        container.appendChild(caseDiv);
    });
}

setInterval(fetchCases, 5000);  // Update every 5 seconds
fetchCases();
