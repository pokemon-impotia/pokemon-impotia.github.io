document.addEventListener("DOMContentLoaded", function() {
    fetch("footer.html")
        .then(response => {
            if (!response.ok) throw new Error("Erreur de chargement du footer");
            return response.text();
        })
        .then(data => {
            document.getElementById("footer").innerHTML = data;
        })
        .catch(error => console.error("Erreur:", error));
});
