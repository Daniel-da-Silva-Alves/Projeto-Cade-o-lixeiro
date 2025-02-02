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




