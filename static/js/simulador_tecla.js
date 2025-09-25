const canvas = document.getElementById('tiro');
const ctx = canvas.getContext('2d');

const centroX = canvas.width / 2;
const centroY = canvas.height / 2;

const radios = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200];

// Dibujar blanco con círculos gris claro y bordes negros
function dibujarBlanco() {
    for (let i = radios.length -1; i >= 0; i--) {
        ctx.beginPath();
        ctx.arc(centroX, centroY, radios[i], 0, Math.PI * 2);
        ctx.fillStyle = '#d3d3d3';  // gris claro
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'black';  // borde negro
        ctx.stroke();

        // Números blancos centrados en el borde derecho del círculo
        ctx.font = "16px Arial";
        ctx.fillStyle = "black";
        ctx.textBaseline = "middle";
        ctx.textAlign = "center";
        ctx.fillText(
            10 - i,
            centroX + radios[i],
            centroY
        );
    }
}

dibujarBlanco();

let lastX = centroX, lastY = centroY;

canvas.addEventListener('mousemove', function(e) {
    const rect = canvas.getBoundingClientRect();
    lastX = e.clientX - rect.left;
    lastY = e.clientY - rect.top;
});

const marcador = document.createElement('div');
marcador.id = 'marcador';
marcador.style.marginTop = '10px';
document.body.appendChild(marcador);

function calcularPuntos(x, y) {
    const dx = x - centroX;
    const dy = y - centroY;
    const distancia = Math.sqrt(dx * dx + dy * dy);

    if (distancia <= 20) return 10;
    else if (distancia <= 40) return 9;
    else if (distancia <= 60) return 8;
    else if (distancia <= 80) return 7;
    else if (distancia <= 100) return 6;
    else if (distancia <= 120) return 5;
    else if (distancia <= 140) return 4;
    else if (distancia <= 160) return 3;
    else if (distancia <= 180) return 2;
    else if (distancia <= 200) return 1;
    else return 0;
}

document.addEventListener('keydown', function(e) {
    if (e.key.toLowerCase() === 'd') {
        const puntos = calcularPuntos(lastX, lastY);

        ctx.beginPath();
        ctx.arc(lastX, lastY, 5, 0, Math.PI * 2);
        ctx.fillStyle = 'red';
        ctx.fill();

        marcador.textContent = `Último disparo: ${puntos} puntos`;

        fetch('/registrar_disparo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x: lastX, y: lastY, puntos: puntos })
        })
        .then(res => res.json())
        .then(data => console.log(data));
    }
});
