/* =========================================
   PARTÍCULAS
========================================= */

const particlesContainer =
    document.getElementById("particles");


const quantidadeParticulas = 32;


for (
    let i = 0;
    i < quantidadeParticulas;
    i++
) {

    const particle =
        document.createElement("span");


    particle.classList.add("particle");


    /* Tamanho aleatório */

    const tamanho =
        Math.random() * 3 + 1;


    particle.style.width =
        `${tamanho}px`;


    particle.style.height =
        `${tamanho}px`;


    /* Posição horizontal */

    particle.style.left =
        `${Math.random() * 100}%`;


    /* Velocidade */

    particle.style.animationDuration =
        `${Math.random() * 8 + 7}s`;


    /* Atraso */

    particle.style.animationDelay =
        `${Math.random() * 8}s`;


    particlesContainer.appendChild(
        particle
    );

}


/* =========================================
   FORMULÁRIO
========================================= 

const loginForm =
    document.getElementById("loginForm");


loginForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();

        console.log(
            "Login enviado!"
        );

    }
);
*/