const canvas = document.getElementById('tiro');
const ctx = canvas.getContext('2d');

// Centro del blanco
const centerX = canvas.width / 2;
const centerY = canvas.height / 2;

// Radios y puntuación
const radios = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200];
const puntos = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1];

// Dibujar los círculos y etiquetas
function dibujarBlanco() {
    for (let i = radios.length - 1; i >= 0; i--) {
        ctx.beginPath();
        ctx.arc(centerX, centerY, radios[i], 0, Math.PI * 2);
        ctx.strokeStyle = '#000';
        ctx.stroke();

        // Etiqueta de puntos
        ctx.font = "16px Arial";
        ctx.fillStyle = "#000";
        ctx.fillText(puntos[i], centerX + radios[i] - 15, centerY);
    }

    // Círculo externo (puntuación 0)
    ctx.beginPath();
    ctx.arc(centerX, centerY, 220, 0, Math.PI * 2);
    ctx.stroke();
    ctx.font = "16px Arial";
    ctx.fillText("0", centerX + 210, centerY);
}

dibujarBlanco();

// Disparo manual con clic
canvas.addEventListener('click', function(e) {
    disparar(e.offsetX, e.offsetY);
});

// Disparo con tecla D (disparo aleatorio)
document.addEventListener('keydown', function(e) {
    if (e.key.toLowerCase() === 'd') {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        disparar(x, y);
    }
});

// Función que ejecuta un disparo y evalúa puntos
function disparar(x, y) {
    // Dibujar disparo
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fillStyle = 'red';
    ctx.fill();

    // Calcular distancia al centro
    let distancia = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
    let puntosObtenidos = 0;

    for (let i = 0; i < radios.length; i++) {
        if (distancia <= radios[i]) {
            puntosObtenidos = puntos[i];
            break;
        }
    }

    // Si está fuera del último círculo (220), es 0
    if (distancia > 220) puntosObtenidos = 0;

    console.log(`Disparo en (${x.toFixed(1)}, ${y.toFixed(1)}), puntos: ${puntosObtenidos}`);

    // Enviar al backend
    fetch('/registrar_disparo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x: x, y: y, puntos: puntosObtenidos })
    })
    .then(response => response.json())
    .then(data => console.log('Respuesta:', data));
}
