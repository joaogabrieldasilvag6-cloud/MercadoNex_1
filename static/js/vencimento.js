const cards = document.querySelectorAll(".card-vencimento");
const painel = document.getElementById("painel-vencimentos");
const tabela = document.getElementById("lista-produtos-vencimento");
const titulo = document.getElementById("titulo-lista");

function obterProdutosPorFiltro(filtro) {

    const produtos =
        JSON.parse(localStorage.getItem("produtos")) || [];

    const hoje = new Date();

    return produtos.filter(produto => {

        if (!produto.validade) return false;

        const validade = new Date(produto.validade);

        const diferencaDias =
            Math.ceil(
                (validade - hoje) /
                (1000 * 60 * 60 * 24)
            );

        if (filtro === "vencidos") {
            return diferencaDias < 0;
        }

        if (filtro === "7dias") {
            return diferencaDias >= 0 && diferencaDias <= 7;
        }

        if (filtro === "30dias") {
            return diferencaDias > 7 && diferencaDias <= 30;
        }

        return false;

    });

}

function atualizarContadores() {

    const produtos =
        JSON.parse(localStorage.getItem("produtos")) || [];

    const hoje = new Date();

    let vencidos = 0;
    let seteDias = 0;
    let trintaDias = 0;

    produtos.forEach(produto => {

        if (!produto.validade) return;

        const validade = new Date(produto.validade);

        const diferencaDias =
            Math.ceil(
                (validade - hoje) /
                (1000 * 60 * 60 * 24)
            );

        if (diferencaDias < 0) {
            vencidos++;
        }
        else if (diferencaDias <= 7) {
            seteDias++;
        }
        else if (diferencaDias <= 30) {
            trintaDias++;
        }

    });

    document.getElementById("total-vencidos").textContent =
        vencidos;

    document.getElementById("total-7dias").textContent =
        seteDias;

    document.getElementById("total-30dias").textContent =
        trintaDias;
}

atualizarContadores();

cards.forEach(card => {

    card.addEventListener("click", () => {

        const filtro = card.dataset.filtro;

        const produtosFiltrados =
            obterProdutosPorFiltro(filtro);

        tabela.innerHTML = "";

        painel.style.display = "block";

        if (filtro === "vencidos") {
            titulo.innerText = "Produtos Vencidos";
        }

        if (filtro === "7dias") {
            titulo.innerText =
                "Produtos vencendo em até 7 dias";
        }

        if (filtro === "30dias") {
            titulo.innerText =
                "Produtos vencendo em até 30 dias";
        }

        if (produtosFiltrados.length === 0) {

            tabela.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align:center">
                        Nenhum produto encontrado.
                    </td>
                </tr>
            `;

            return;
        }

        produtosFiltrados.forEach(produto => {

            let status = "Em dia";
            let classe = "status-ok";

            const validade =
                new Date(produto.validade);

            const hoje =
                new Date();

            const diferencaDias =
                Math.ceil(
                    (validade - hoje) /
                    (1000 * 60 * 60 * 24)
                );

            if (diferencaDias < 0) {
                status = "Vencido";
                classe = "status-vencido";
            }
            else if (diferencaDias <= 7) {
                status = "Atenção";
                classe = "status-alerta";
            }

            tabela.innerHTML += `
                <tr>
                    <td>${produto.nome}</td>
                    <td>${produto.categoria}</td>
                    <td>${produto.validade}</td>
                    <td class="${classe}">
                        ${status}
                    </td>
                </tr>
            `;

        });

        painel.scrollIntoView({
            behavior: "smooth"
        });

    });

});

