/* =========================================
   PARTÍCULAS
========================================= */

const particlesContainer =
    document.getElementById("particles");

const quantidadeParticulas = 32;

for (let i = 0; i < quantidadeParticulas; i++) {

    const particle = document.createElement("span");

    particle.classList.add("particle");

    const tamanho = Math.random() * 3 + 1;

    particle.style.width = `${tamanho}px`;
    particle.style.height = `${tamanho}px`;
    particle.style.left = `${Math.random() * 100}%`;

    particle.style.animationDuration =
        `${Math.random() * 8 + 7}s`;

    particle.style.animationDelay =
        `${Math.random() * 8}s`;

    particlesContainer.appendChild(particle);
}




/* =========================================
   FORMULÁRIO DE CADASTRO
========================================= 

const cadastroForm =
    document.getElementById("cadastroForm");

if (cadastroForm) {

    cadastroForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();

            const senha =
                document.getElementById("senha").value;

            const confirmarSenha =
                document.getElementById("confirmarSenha").value;


            if (senha !== confirmarSenha) {

                alert(
                    "As senhas não são iguais."
                );

                return;
            }


            alert(
                "Cadastro realizado com sucesso!"
            );

        }
    );


     =====================================
       MÁSCARA DE TELEFONE
    ====================================== 

    const telefone =
        document.getElementById("telefone");

    if (telefone) {

        telefone.addEventListener(
            "input",
            function () {

                let valor =
                    telefone.value.replace(/\D/g, "");

                valor =
                    valor.substring(0, 11);


                if (valor.length <= 10) {

                    valor =
                        valor.replace(
                            /^(\d{2})(\d{4})(\d{0,4}).(obs: tirar essa pate e colocar essa (* / ),
                            "($1) $2-$3"
                        );

                } else {

                    valor =
                        valor.replace(
                            /^(\d{2})(\d{5})(\d{0,4}).(obs: tirar essa pate e colocar essa (* / ),
                            "($1) $2-$3"
                        );

                }

                telefone.value = valor;

            }
        );

    }

}
*/