/* Funções para chamadas de API do Django */

// Função para enviar coordenadas para a API Django
async function sendCoordinatesToApi(latitude, longitude) {
    const csrfToken = getCsrfToken();
    const response = await fetch('/locate_trucks_in_neighborhood/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ latitude, longitude }),
    });
    return response.json();
}

function iniciarRastreamento() {
    const statusDisplay = document.getElementById('status'); // Parágrafo que exibe o status da localização
    const addressDisplay = document.getElementById('address'); // Parágrafo que exibe a localização
    
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            async position => {
                const { latitude, longitude } = position.coords;
                statusDisplay.textContent = "Localização Atualizada";
                marker.setLatLng([latitude, longitude]); // Atualiza marcador
                map.setView([latitude, longitude], 16);
                enviarLocalizacao(latitude, longitude);

                try {
                    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`);
                    if (!response.ok) throw new Error('Erro na API de geocodificação.');

                    const data = await response.json();
                    const address = data?.display_name || 'Endereço não encontrado.';
                    addressDisplay.textContent = address.length > 30 ? address.slice(0, 30) + "..." : address;
                } catch (error) {
                    console.error('Erro ao obter o endereço:', error);
                    addressDisplay.textContent = 'Erro ao buscar o endereço.';
                }
            },
            error => {
                console.error("Erro ao capturar localização", error);
                statusDisplay.textContent = "Erro ao capturar localização.";
            },
            { enableHighAccuracy: true, maximumAge: 0 }
        );

        loadRouteLocations();
        const popupContainer = document.getElementById("popup");
        popupContainer?.classList.remove('show');
    } else {
        alert("Seu navegador não suporta geolocalização.");
    }
}  

function loadRouteLocations() {
    fetch('/api/routes/locations/')
        .then(response => response.json())
        .then(data => {
            const routeLocationsTable = document.getElementById('route-locations');
            routeLocationsTable.innerHTML = ''; // Limpa a tabela
            const waypoints = [];

            data.locations.forEach(location => {
                const row = document.createElement('tr');
                row.setAttribute('data-lat', location.latitude);
                row.setAttribute('data-lng', location.longitude);
                row.innerHTML = `<td>${location.order}</td><td>${location.address}</td>`;

                // Clique para zoom e destacar linha
                row.addEventListener('click', () => {
                    // Remove a classe 'active' de todas as linhas
                    document.querySelectorAll('#route-locations tr').forEach(r => r.classList.remove('active'));
                    
                    // Adiciona a classe 'active' à linha clicada
                    row.classList.add('active');
                    
                    // Zoom no mapa
                    zoomToLocation(location.latitude, location.longitude, location);
                });

                routeLocationsTable.appendChild(row);
                waypoints.push(L.latLng(location.latitude, location.longitude));
            });

            if (waypoints.length > 1) {
                L.Routing.control({
                    waypoints: waypoints,
                    routeWhileDragging: true,
                    lineOptions: { styles: [{ color: 'green', weight: 3 }] },
                    createMarker: (i, waypoint, n) => {
                        const location = data.locations[i]; // Obtém os dados correspondentes ao waypoint atual
                        const icon = i === 0 ? startIcon : i === n - 1 ? endIcon : waypointIcon;

                        // Cria o marcador com o pop-up contendo o endereço
                        return L.marker(waypoint.latLng, { icon: icon })
                            .bindPopup(`<strong>Ponto de coleta ${i + 1}</strong><br>Endereço: ${location.address}`);
                    },
                }).addTo(map);
            }
        })
        .catch(error => console.error('Erro ao carregar localizações:', error));
}
    
function fetchTrackingInfoForUser() {
    const driverNameElement = document.getElementById('driver-name');
    const vehicleIdElement = document.getElementById('vehicle-id');
    const currentAddressElement = document.getElementById('address');

    fetch('/tracking-info-for-user/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
    })
    .then(response => {
        if (!response.ok) throw new Error(`Erro da API: ${response.statusText}`);
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const { driver_name, truck_id, current_address } = data.data;
            driverNameElement.textContent = driver_name || 'Não disponível';
            vehicleIdElement.textContent = truck_id || 'Não disponível';
            currentAddressElement.textContent = current_address?.length > 30
                ? current_address.slice(0, 30) + "..."
                : current_address || 'aguardando...';
        } else {
            console.error('Erro da API:', data.message);
        }
    })
    .catch(error => console.error('Erro na requisição:', error));
}