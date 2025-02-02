/* Validações de formulários */

// index.html - Lógica de autenticação e redirecionamento para a Área do Motorista
document.getElementById('loginForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const truckId = document.getElementById('truckId').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ truck_id: truckId, username: username, password: password }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Login bem-sucedido!');
                window.location.href = '/tracking-interface/';
            } else {
                document.getElementById('loginError').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            document.getElementById('loginError').style.display = 'block';
        });
});
