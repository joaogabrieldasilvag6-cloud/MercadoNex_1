// ============================
// MODAL DE PRODUTOS
// ============================

const modalProduto = document.getElementById("modalProduto");
const formProduto = document.getElementById("product-form");
const btnCadastrar = document.getElementById("btnCadastrar");
const btnFechar = document.querySelector(".fechar");


// ============================
// ABRIR MODAL PARA CADASTRAR
// ============================

if (btnCadastrar) {

    btnCadastrar.addEventListener("click", () => {

        formProduto.reset();

        formProduto.action = "/produtos/cadastrar/";

        modalProduto.classList.add("show");

    });

}


// ============================
// FECHAR MODAL
// ============================

function fecharModalProduto(){

    modalProduto.classList.remove("show");

}


if(btnFechar){

    btnFechar.addEventListener("click", fecharModalProduto);

}


// Fecha clicando fora

window.addEventListener("click", function(e){

    if(e.target === modalProduto){

        fecharModalProduto();

    }

});


// ============================
// EDITAR PRODUTO
// ============================

async function editarProduto(id){

    try{

        const resposta = await fetch(`/produtos/json/${id}/`, {
            method: "GET",
            headers:{
                "X-Requested-With":"XMLHttpRequest"
            }
        });


        if(!resposta.ok){

            throw new Error(
                "Erro ao buscar produto: " + resposta.status
            );

        }

        
        const produto = await resposta.json();
        console.log(formProduto);
        console.log(formProduto.elements);
        console.log(formProduto.elements["nome"]);

        console.log("Produto carregado:", produto);


        // altera ação do formulário

        formProduto.action = `/produtos/editar/${id}/`;


        // Preenche campos

        formProduto.elements["nome"].value =
            produto.nome || "";


        formProduto.elements["categoria"].value =
            produto.categoria || "";


        formProduto.elements["descricao"].value =
            produto.descricao || "";


        formProduto.elements["codigo"].value =
            produto.codigo || "";


        formProduto.elements["marca"].value =
            produto.marca || "";


        formProduto.elements["preco_venda"].value =
            produto.preco_venda || "";


        formProduto.elements["preco_custo"].value =
            produto.preco_custo || "";


        formProduto.elements["quantidade"].value =
            produto.quantidade || "";


        formProduto.elements["validade"].value =
            produto.validade || "";


        formProduto.elements["fornecedor"].value =
            produto.fornecedor || "";


        formProduto.elements["status"].checked =
            produto.status;


        formProduto.elements["destaque"].checked =
            produto.destaque;



        // abre modal

        modalProduto.classList.add("show");


    }catch(erro){

        console.error(
            "Erro ao carregar produto:",
            erro
        );

        alert("Erro ao acessar o produto.");

    }

}



console.log("JS Produtos carregado.");