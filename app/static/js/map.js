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


const startRouteIcon = L.icon({
    iconUrl: '/static/tracking/images/saco-de-lixo-start.png',
    iconSize: [40, 40],
    iconAnchor: [19, 38],
    popupAnchor: [0, -38],
});

const endRouteIcon = L.icon({
    iconUrl: '/static/tracking/images/saco-de-lixo-finish.png',
    iconSize: [40, 40],
    iconAnchor: [19, 38],
    popupAnchor: [0, -38],
});

// apaguei o  wayPointIcon pq é possível reutilizar o trashIcon
// apaguei o garbageTruckIcon pq é possível reutilizar o truckIcon

const trashIcon = L.icon({
    iconUrl: '/static/tracking/images/saco-de-lixo.png',
    iconSize: [40, 40],
    iconAnchor: [19, 38],
    popupAnchor: [0, -38],
});

// Array global para armazenar localizações clicadas
const locations = [];


// Inicialização do mapa
const map = L.map(mapElement).setView([0, 0], 13);
const mapElement = document.getElementById('map');
const marker = L.marker([0, 0], { icon: truckIcon }).addTo(map);

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

function zoomToLocation(lat, lng, location) {
    // Adicionar a localização ao array se ainda não estiver presente
    if (!locations.some(loc => loc.order === location.order)) {
        locations.push(location);
    }

    // Ordenar as localizações por 'order' para garantir que o primeiro e o último sejam identificados corretamente
    locations.sort((a, b) => a.order - b.order);

    // Verificar se é a primeira, última ou intermediária localização
    const isFirst = locations[0].order === location.order; // Primeira localização
    const isLast = locations[locations.length - 1].order === location.order; // Última localização
    const isIntermediate = !isFirst && !isLast; // Localização intermediária

    // Definir ícone com base na posição
    let icon = trashIcon; // Ícone padrão
    if (isFirst) {
        icon = startIcon; // Ícone para a primeira localização
    } else if (isLast) {
        icon = endIcon; // Ícone para a última localização
    } else if (isIntermediate) {
        icon = trashIcon; // Ícone para localizações intermediárias
    }

    // Centralizar o mapa na localização clicada
    map.setView([lat, lng], 15);

    // Adicionar marcador no mapa com o ícone apropriado
    const marker = L.marker([lat, lng], { icon: icon }).addTo(map);
    marker.bindPopup(`<strong>Ponto de coleta ${location.order}</strong><br>Endereço: ${location.address}`).openPopup();

    // Vincular popup ao marcador
    marker.bindPopup(popupContent).openPopup();
}