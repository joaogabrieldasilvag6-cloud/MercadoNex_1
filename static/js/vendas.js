// =======================================
// ELEMENTOS DA PÁGINA
// =======================================

// Modal
const modal = document.getElementById("modalVenda");
const btnNovaVenda = document.getElementById("btnNovaVenda");
const btnFechar = document.getElementById("fecharModal");

// Formulário
const formVenda = document.getElementById("formVenda");

const clienteVenda = document.getElementById("clienteVenda");
const pagamentoVenda = document.getElementById("pagamentoVenda");
const produtoVenda = document.getElementById("produtoVenda");
const quantidadeProduto = document.getElementById("quantidadeProduto");

// Carrinho
const btnAdicionar = document.getElementById("btnAdicionar");
const listaProdutos = document.getElementById("listaProdutos");
const totalVenda = document.getElementById("totalVenda");

// Cards
const faturamentoHoje = document.getElementById("faturamentoHoje");
const vendasHoje = document.getElementById("vendasHoje");
const itensVendidos = document.getElementById("itensVendidos");
const vendasPendentes = document.getElementById("vendasPendentes");

// =======================================
// VARIÁVEIS
// =======================================

let carrinho = [];

// =======================================
// ABRIR MODAL
// =======================================

btnNovaVenda.addEventListener("click", () => {

    formVenda.reset();

    carrinho = [];

    atualizarTabela();

    modal.classList.add("show");

});

// =======================================
// FECHAR MODAL
// =======================================

btnFechar.addEventListener("click", fecharModal);

window.addEventListener("click", (e) => {

    if (e.target === modal) {

        fecharModal();

    }

});

function fecharModal() {

    modal.classList.remove("show");

}

// =======================================
// ADICIONAR PRODUTO
// =======================================

btnAdicionar.addEventListener("click", () => {

    const produto = produtoVenda.value;
    const quantidade = Number(quantidadeProduto.value);

    if (produto === "") {

        alert("Selecione um produto.");

        return;

    }

    if (quantidade <= 0) {

        alert("Informe uma quantidade válida.");

        return;

    }

    // Valor fictício por enquanto
    const option = produtoVenda.options[produtoVenda.selectedIndex];
    const preco = Number(option.dataset.preco);
    const estoque = Number(option.dataset.estoque);

    if (quantidade > estoque){

    alert("Quantidade indisponível em estoque.");

    return;

}

    carrinho.push({
    id: produtoVenda.value,
    produto: option.text,
    quantidade,
    preco,
    subtotal: preco * quantidade

});

    atualizarTabela();

    produtoVenda.selectedIndex = 0;
    quantidadeProduto.value = 1;

});

// =======================================
// ATUALIZAR TABELA
// =======================================

function atualizarTabela() {

    listaProdutos.innerHTML = "";

    let total = 0;

    carrinho.forEach((item, index) => {

        total += item.subtotal;

        listaProdutos.innerHTML += `

            <tr>

                <td>${item.produto}</td>

                <td>${item.quantidade}</td>

                <td>R$ ${item.preco.toFixed(2)}</td>

                <td>R$ ${item.subtotal.toFixed(2)}</td>

                <td>

                    <button
                        class="acao excluir"
                        onclick="removerProduto(${index})">

                        <i class="fa-solid fa-trash"></i>

                    </button>

                </td>

            </tr>

        `;

    });

    totalVenda.innerText = total.toFixed(2);

}

// =======================================
// REMOVER PRODUTO
// =======================================

function removerProduto(index) {

    carrinho.splice(index, 1);

    atualizarTabela();

}

// =======================================
// FINALIZAR VENDA
// =======================================

formVenda.addEventListener("submit", function (e) {

    e.preventDefault();

    if (clienteVenda.value === "") {

        alert("Selecione um cliente.");

        return;

    }

    if (carrinho.length === 0) {

        alert("Adicione pelo menos um produto.");

        return;

    }

    const dadosVenda = {

    cliente: clienteVenda.value,

    forma_pagamento: pagamentoVenda.value,

    desconto: 0,

    itens: carrinho

};

fetch("/vendas/finalizar/", {

    method: "POST",

    headers: {

        "Content-Type": "application/json",

        "X-CSRFToken": getCookie("csrftoken")

    },

    body: JSON.stringify(dadosVenda)

})
.then(resposta => resposta.json())
.then(dados => {

    if(dados.sucesso){

        alert("Venda enviada para o Django com sucesso!");

    }else{

        alert("Erro ao enviar.");

    }

});

    carrinho = [];

    atualizarTabela();

    formVenda.reset();

    fecharModal();
    

});

// =======================================
// ATUALIZAR CARDS (DEMONSTRAÇÃO)
// =======================================

function atualizarCards() {

    faturamentoHoje.textContent = "R$ 0,00";
    vendasHoje.textContent = "0";
    itensVendidos.textContent = "0";
    vendasPendentes.textContent = "0";

}

atualizarCards();

let vendas = [

    {

        codigo:1,

        cliente:"João Gabriel",

        data:"13/07/2026",

        total:75,

        pagamento:"PIX",

        status:"Pago"

    }

];

function getCookie(nome) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(nome + "=")) {

                cookieValue = decodeURIComponent(cookie.substring(nome.length + 1));

                break;

            }

        }

    }

    return cookieValue;

}

console.log("Módulo de Vendas carregado com sucesso.");