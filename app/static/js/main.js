/* Configurações e inicialização globais */


// index.html - Ação para o botão "Aplicar"
document.getElementById('applyFilters').addEventListener('click', function() {
    const selectedNeighborhood = document.getElementById('neighborhoodSelect').value;
    fetchTruckLocations(selectedNeighborhood);
});

// index.html - Ação para o botão "Limpar"
document.getElementById('clearFilters').addEventListener('click', function() {
    document.getElementById('neighborhoodSelect').value = 'todos';
});

// Botão de inicialização do rastreamento (Motorista)
document.addEventListener('DOMContentLoaded', () => {
    fetchTrackingInfoForUser();

    const startTrackingButton = document.createElement("button");
    startTrackingButton.id = "startTrackingButton";
    startTrackingButton.textContent = "Compartilhar localização";
    startTrackingButton.addEventListener("click", iniciarRastreamento);

    const popupContainer = document.getElementById("popup");
    if (popupContainer) {
        popupContainer.appendChild(startTrackingButton);
        popupContainer.classList.add('show');
    }
});  

// Expansão/retração da tabela
 document.getElementById('toggleButton').addEventListener('click', () => {
        const table = document.getElementById('routeTable');
        const expandIcon = document.querySelector('.icon-expand');
        const collapseIcon = document.querySelector('.icon-collapse');

        if (table.classList.contains('collapse')) {
            table.classList.remove('collapse');
            expandIcon.classList.add('d-none');
            collapseIcon.classList.remove('d-none');
        } else {
            table.classList.add('collapse');
            expandIcon.classList.remove('d-none');
            collapseIcon.classList.add('d-none');
        }
});

// index.html - Função para obter o CSRF Token
function getCsrfToken() {
    const csrfTokenElement = document.querySelector('[name=csrf-token]');
    return csrfTokenElement ? csrfTokenElement.content : '';
}

// index.html - Função para exibir ou esconder o indicador de carregamento
function toggleLoadingIndicator(show) {
    const loadingElement = document.querySelector('.loading');
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}