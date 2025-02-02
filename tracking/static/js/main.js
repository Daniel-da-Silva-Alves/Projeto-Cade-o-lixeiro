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