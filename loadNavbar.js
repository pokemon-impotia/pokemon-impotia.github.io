// Inclure la navbar à partir de navbar.html
fetch('navbar.html')
    .then(response => response.text())
    .then(data => {
        document.getElementById('navbar').innerHTML = data;
    })
    .catch(error => console.error('Erreur lors du chargement de la navbar:', error));
