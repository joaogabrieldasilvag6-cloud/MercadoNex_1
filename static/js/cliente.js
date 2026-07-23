// =====================================================
// MERCADONEX
// GESTÃO DE CLIENTES
// =====================================================


// =====================================================
// ELEMENTOS
// =====================================================

const modalCliente = document.getElementById("modalCliente");

const clienteForm = document.getElementById("cliente-form");

const btnNovoCliente = document.getElementById("btnNovoCliente");

const btnFecharModal = document.getElementById("fecharModal");

const btnCancelarModal = document.getElementById("cancelarModal");

const tituloModal = document.getElementById("tituloModalCliente");

const btnSalvar = document.querySelector(".btn-salvar");

const tabelaClientes = document.getElementById("clientes-tbody");

const campoBusca = document.getElementById("buscarCliente");


// =====================================================
// ABRIR MODAL
// =====================================================

function abrirModalCliente() {

    clienteForm.reset();

    clienteForm.action = "/clientes/cadastrar/";

    tituloModal.innerHTML = `
        <i class="fa-solid fa-user-plus"></i>
        Novo Cliente
    `;

    btnSalvar.innerHTML = `
        <i class="fa-solid fa-floppy-disk"></i>
        Salvar Cliente
    `;

    modalCliente.classList.add("show");

}


// =====================================================
// FECHAR MODAL
// =====================================================

function fecharModalCliente() {

    modalCliente.classList.remove("show");

    clienteForm.reset();

    clienteForm.action = "/clientes/cadastrar/";

}


// =====================================================
// EVENTOS
// =====================================================

if(btnNovoCliente){

    btnNovoCliente.addEventListener("click", abrirModalCliente);

}

if(btnFecharModal){

    btnFecharModal.addEventListener("click", fecharModalCliente);

}

if(btnCancelarModal){

    btnCancelarModal.addEventListener("click", fecharModalCliente);

}

window.addEventListener("click",(e)=>{

    if(e.target === modalCliente){

        fecharModalCliente();

    }

});


// =====================================================
// EDITAR CLIENTE
// =====================================================

async function editarCliente(id){

    try{

        const resposta = await fetch(`/clientes/json/${id}/`);

        const cliente = await resposta.json();

        clienteForm.action = `/clientes/editar/${id}/`;

        tituloModal.innerHTML = `
            <i class="fa-solid fa-user-pen"></i>
            Editar Cliente
        `;

        btnSalvar.innerHTML = `
            <i class="fa-solid fa-floppy-disk"></i>
            Atualizar Cliente
        `;

        clienteForm.nome.value = cliente.nome;
        clienteForm.telefone.value = cliente.telefone;
        clienteForm.email.value = cliente.email;
        clienteForm.cpf.value = cliente.cpf;
        clienteForm.endereco.value = cliente.endereco;
        clienteForm.limite_fiado.value = cliente.limite_fiado;
        clienteForm.ativo_fiado.checked = cliente.ativo_fiado;

        modalCliente.classList.add("show");

    }

    catch(erro){

        console.error(erro);

        alert("Erro ao carregar os dados do cliente.");

    }

}


// =====================================================
// SALVAR CLIENTE
// =====================================================

clienteForm.addEventListener("submit", async function(e){

    e.preventDefault();

    const formData = new FormData(clienteForm);

    try{

        const resposta = await fetch(clienteForm.action,{

            method:"POST",

            body:formData,

            headers:{
                "X-Requested-With":"XMLHttpRequest"
            }

        });

        const dados = await resposta.json();

        if(dados.success){

            fecharModalCliente();

            atualizarLinhaCliente(dados.cliente);

            alert("Cliente salvo com sucesso!");

        }

        else{

            alert(dados.erro);

        }

    }

    catch(erro){

        console.error(erro);

        alert("Erro na comunicação com o servidor.");

    }

});


// =====================================================
// ATUALIZAR TABELA
// =====================================================

function atualizarLinhaCliente(cliente){

    let encontrou = false;

    document.querySelectorAll("#clientes-tbody tr").forEach(linha=>{

        const botao = linha.querySelector(".btn-editar");

        if(!botao) return;

        if(!botao.getAttribute("onclick").includes(`(${cliente.id})`)) return;

        encontrou = true;

        linha.children[0].innerHTML = `<strong>${cliente.nome}</strong>`;

        linha.children[1].textContent = cliente.telefone;

        linha.children[2].textContent = cliente.email;

        linha.children[3].textContent =
            "R$ " + Number(cliente.saldo).toFixed(2);

        linha.children[4].innerHTML = cliente.ativo_fiado
            ? '<span class="badge badge-success">Ativo</span>'
            : '<span class="badge badge-danger">Bloqueado</span>';

    });

    if(!encontrou){

        location.reload();

    }

}


// =====================================================
// REMOVER CLIENTE
// =====================================================

async function removerCliente(id){

    if(!confirm("Deseja remover este cliente?")) return;

    try{

        const resposta = await fetch(`/clientes/excluir/${id}/`);

        const dados = await resposta.json();

        if(dados.success){

            document.querySelectorAll("#clientes-tbody tr").forEach(linha=>{

                const botao = linha.querySelector(".btn-excluir");

                if(!botao) return;

                if(botao.getAttribute("onclick").includes(`(${id})`)){

                    linha.remove();

                }

            });

            alert("Cliente removido com sucesso!");

        }

        else{

            alert(dados.erro);

        }

    }

    catch(erro){

        console.error(erro);

        alert("Erro ao remover cliente.");

    }

}


// =====================================================
// BUSCA
// =====================================================

if(campoBusca){

    campoBusca.addEventListener("input",function(){

        const valor = this.value.toLowerCase();

        document.querySelectorAll("#clientes-tbody tr").forEach(linha=>{

            linha.style.display =
                linha.textContent.toLowerCase().includes(valor)
                ? ""
                : "none";

        });

    });

}


// =====================================================
// INICIALIZAÇÃO
// =====================================================

console.log("✔ MercadoNex | Gestão de Clientes carregada.");