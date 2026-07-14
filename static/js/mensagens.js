// ==========================
// MENSAGENS DO DJANGO
// ==========================

document.addEventListener("DOMContentLoaded", () => {

    const alertas = document.querySelectorAll(".alerta");

    if (alertas.length === 0) return;

    setTimeout(() => {

        alertas.forEach(alerta => {

            alerta.style.transition = "opacity .5s ease";
            alerta.style.opacity = "0";

            setTimeout(() => {
                alerta.remove();
            }, 500);

        });

    }, 3000);

});