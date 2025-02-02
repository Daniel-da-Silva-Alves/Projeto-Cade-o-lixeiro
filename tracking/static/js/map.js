/* # Lógica para o Leaflet.js (mapa) */

 // Configuração dos ícones para os usuarios
 const userIcon = L.icon({
    iconUrl: '/static/tracking/images/usuario-icon.png',
    iconSize: [37, 60],
    iconAnchor: [19, 38],
    popupAnchor: [0, -38],
});

const truckIcon = L.icon({
    iconUrl: '/static/tracking/images/caminhao-de-reciclagem.png',
    iconSize: [40, 40],
    iconAnchor: [19, 38],
    popupAnchor: [0, -38],
});

// Inicialização do mapa
var map = L.map('mapid').setView([-3.0421492195005304, -59.98956721838468], 13);

// Configuração do mapa com o Tile Layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Função para obter coordenadas do usuário
function getUserCoordinates() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
    });
}

// Função para atualizar o mapa e a lista de caminhões
function updateMapAndList(data, latitude, longitude) {
    const truckListElement = document.querySelector('.truck-list');
    if (!truckListElement) {
        console.error("Elemento .truck-list não encontrado");
        return;
    }

    // Adicionar a localização do usuário ao mapa
    const userMarker = L.marker([latitude, longitude], { icon: userIcon }).addTo(map);
    userMarker.bindPopup('Você está aqui!').openPopup();
    map.setView([latitude, longitude], 16);

    // Atualizar a legenda com base na resposta da API
    if (data.success) {
        truckListElement.innerHTML = ''; // Limpar a lista antes de atualizar
        data.trucks.forEach(truck => {
            truckListElement.innerHTML += `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div class="d-flex align-items-center">
                        <div class="bg-success rounded-circle me-2" style="width: 10px; height: 10px;"></div>
                        <span>${truck.truck_id}</span>
                    </div>
                    <span>${truck.last_updated}</span>
                </div>
            `;

            // Adicionar caminhões no mapa
            const truckMarker = L.marker([truck.latitude, truck.longitude], { icon: truckIcon }).addTo(map);
            const truckPopupContent = `
                <div>
                    <strong>Código do Caminhão:</strong> ${truck.truck_id}<br>
                    <strong>Última Atualização:</strong> ${truck.last_updated}<br>
                    <strong>Endereço:</strong> ${truck.address}
                </div>
            `;
            truckMarker.bindPopup(truckPopupContent);
        });
    } else {
        truckListElement.innerHTML = '<p>Sem caminhões no seu bairro.</p>';
    }
}

 // Função principal para obter localização e atualizar a interface
 async function locateTrucks() {
    try {
        toggleLoadingIndicator(true);
        const position = await getUserCoordinates();
        const { latitude, longitude } = position.coords;
        const data = await sendCoordinatesToApi(latitude, longitude);
        console.log('Resposta da API:', data);
        updateMapAndList(data, latitude, longitude);
    } catch (error) {
        console.error('Erro:', error);
        alert('Ocorreu um erro ao buscar os caminhões. Tente novamente mais tarde.');
    } finally {
        toggleLoadingIndicator(false);
    }
}

// Iniciar o processo de localização de caminhões
locateTrucks();

// Função para limpar os marcadores antigos no mapa
function clearOldMarkers(map) {
    map.eachLayer(function(layer) {
        if (layer instanceof L.Marker) {
            const iconOptions = layer.options.icon && layer.options.icon.options;
            if (iconOptions && iconOptions.className && !iconOptions.className.includes('user-icon')) {
                map.removeLayer(layer);
            }
        }
    });
}

// Função para limpar a lista de caminhões
function clearTruckList() {
    const truckListElement = document.querySelector('.truck-list');
    if (truckListElement) {
        truckListElement.innerHTML = ''; // Limpar a lista antes de atualizar
    }
}

// Função para adicionar caminhões ao mapa e à lista
function addTrucksToMapAndList(data, map, bounds) {
    const truckListElement = document.querySelector('.truck-list');
    data.forEach(truck => {
        // Formatar a data de atualização para exibição legível
        const updatedAt = new Date(truck.last_updated);
        const formattedDate = updatedAt.toLocaleString(); // Exibe data e hora no formato local

        // Exibe os dados na lista (HTML)
        if (truckListElement) {
            truckListElement.innerHTML += `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <!-- Coluna Caminhão -->
                    <div class="d-flex align-items-center">
                        <div class="bg-success rounded-circle me-2" style="width: 10px; height: 10px;"></div>
                        <span>${truck.truck_id}</span>
                    </div>
                    <!-- Coluna Data de Atualização -->
                    <span>${formattedDate}</span> <!-- Exibe a data formatada -->
                </div>
            `;
        }

        // Adicionar marcadores de caminhão no mapa
        const truckMarker = L.marker([truck.latitude, truck.longitude], { icon: truckIcon }).addTo(map);

        // Conteúdo da popup do caminhão com informações adicionais
        const truckPopupContent = `
            <div>
                <strong>Código do Caminhão:</strong> ${truck.truck_id}<br>
                <strong>Última Atualização:</strong> ${formattedDate}<br> <!-- Exibe a data formatada na popup -->
                <strong>Endereço:</strong> ${truck.address}
            </div>
        `;
        truckMarker.bindPopup(truckPopupContent); // Exibe a popup com detalhes do caminhão

        // Atualiza os limites do mapa para incluir o caminhão atual
        bounds.extend([truck.latitude, truck.longitude]);
    });
}

// Função para adicionar a localização do usuário no mapa
function addUserLocationToMap(map, bounds) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const userLat = position.coords.latitude;
            const userLon = position.coords.longitude;

            // Adiciona o marcador da localização do usuário no mapa
            const userMarker = L.marker([userLat, userLon], { icon: userIcon }).addTo(map);

            // Conteúdo da popup do usuário
            const userPopupContent = `
                <div>
                    <strong>Localização do Usuário</strong><br>
                    Latitude: ${userLat}<br>
                    Longitude: ${userLon}
                </div>
            `;
            userMarker.bindPopup(userPopupContent); // Exibe a popup com a localização do usuário

            // Atualiza os limites do mapa para incluir a localização do usuário
            bounds.extend([userLat, userLon]);

            // Ajusta o mapa para incluir todos os caminhões e a localização do usuário
            map.fitBounds(bounds);
        });
    } else {
        console.error("Geolocalização não suportada pelo navegador.");
    }
}

// Função para exibir mensagem de ausência de caminhões
function displayNoTrucksMessage() {
    const truckListElement = document.querySelector('.truck-list');
    if (truckListElement) {
        truckListElement.innerHTML = '<p>Sem caminhões no seu bairro.</p>';
    }
}

// Função principal para carregar as localizações dos caminhões com base no bairro selecionado
async function fetchTruckLocations(neighborhood) {
    try {
        const response = await fetch(`/api/locations?neighborhood=${neighborhood}`);
        const data = await response.json();

        // Verifica se há caminhões no bairro
        if (data.length > 0) {
            clearOldMarkers(map);
            clearTruckList();

            // Criar um array de coordenadas para definir o limite de visualização do mapa
            const bounds = L.latLngBounds();

            addTrucksToMapAndList(data, map, bounds);
            addUserLocationToMap(map, bounds);
        } else {
            displayNoTrucksMessage();
        }
    } catch (error) {
        console.error('Erro ao buscar localizações:', error);
    }
}