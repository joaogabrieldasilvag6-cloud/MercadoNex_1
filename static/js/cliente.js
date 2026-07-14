// ===============================
// MODAL DE CLIENTES
// ===============================

const modalCliente = document.getElementById("modalCliente");
const btnNovoCliente = document.getElementById("btnNovoCliente");
const fecharCliente = document.getElementById("fecharModal");
const cancelarModal = document.getElementById("cancelarModal");
const clienteForm = document.getElementById("cliente-form");

// ===============================
// ABRIR MODAL
// ===============================

if (btnNovoCliente) {

    btnNovoCliente.addEventListener("click", () => {

        clienteForm.reset();

        clienteForm.action = "/clientes/cadastrar/";

        modalCliente.classList.add("show");

    });

}

// ===============================
// FECHAR MODAL
// ===============================

function fecharModalCliente() {

    modalCliente.classList.remove("show");

    clienteForm.reset();

}

if (fecharCliente) {
    fecharCliente.addEventListener("click", fecharModalCliente);
}

if (cancelarModal) {
    cancelarModal.addEventListener("click", fecharModalCliente);
}

window.addEventListener("click", function (e) {

    if (e.target === modalCliente) {
        fecharModalCliente();
    }

});

// ===============================
// EDITAR CLIENTE
// ===============================

async function editarCliente(id) {

    const form = document.getElementById("cliente-form");

    // Abre modal
    modalCliente.classList.add("show");

    // Define action de edição
    form.action = `/clientes/editar/${id}/`;

    // Busca dados do cliente
    const response = await fetch(`/clientes/json/${id}/`);
    const cliente = await response.json();

    // Preenche formulário
    form.nome.value = cliente.nome;
    form.telefone.value = cliente.telefone;
    form.email.value = cliente.email;
    form.cpf.value = cliente.cpf;
    form.endereco.value = cliente.endereco;
    form.limite_fiado.value = cliente.limite_fiado;
    form.ativo_fiado.checked = cliente.ativo_fiado;

}

// ===============================
// SALVAR CLIENTE (AJAX)
// ===============================

clienteForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const formData = new FormData(clienteForm);

    try {

        const resposta = await fetch(clienteForm.action, {

            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }

        });

        const dados = await resposta.json();

         if (dados.success) {

            alert("✅ Cliente salvo com sucesso!");

            fecharModalCliente();

            atualizarLinhaCliente(dados.cliente);


        } else {

            alert(dados.erro);


        }

    } catch (erro) {

        console.error("Erro:", erro);

        alert("Erro na comunicação com o servidor.");

    }

});

function atualizarLinhaCliente(cliente){

    const linhas = document.querySelectorAll("#clientes-tbody tr");

    linhas.forEach(linha => {

        const botaoEditar = linha.querySelector(".btn-outline-sm");

        if(!botaoEditar) return;

        const onclick = botaoEditar.getAttribute("onclick");

        if(onclick.includes(`(${cliente.id})`)){

            linha.children[0].textContent = cliente.nome;
            linha.children[1].textContent = cliente.telefone;
            linha.children[2].textContent = cliente.email;
            linha.children[3].textContent = "R$ " + Number(cliente.saldo).toFixed(2);

            linha.children[4].innerHTML = cliente.ativo_fiado
                ? '<span class="badge badge-mec">Ativo</span>'
                : '<span class="badge badge-events">Bloqueado</span>';
        }

    });

}

async function removerCliente(id){

    const confirmar = confirm(
        "Deseja remover este cliente?"
    );

    if(!confirmar){
        return;
    }

    try{

        const resposta = await fetch(`/clientes/excluir/${id}/`);

        const dados = await resposta.json();

        if(dados.success){

            const linhas =
            document.querySelectorAll("#clientes-tbody tr");

            linhas.forEach(linha=>{

                const botao =
                linha.querySelector(".btn-danger-sm");

                if(!botao) return;

                if(botao.getAttribute("onclick").includes(`(${id})`)){

                    linha.remove();

                }

            });

            alert("✅ Cliente removido!");

        }

    }catch(erro){

        console.error(erro);

        alert("Erro ao remover cliente.");

    }

}

const campoBusca = document.getElementById("buscarCliente");

if (campoBusca) {

    campoBusca.addEventListener("input", function () {

        const valor = this.value.toLowerCase();

        const linhas = document.querySelectorAll("#clientes-tbody tr");

        linhas.forEach(linha => {

            const texto = linha.textContent.toLowerCase();

            if (texto.includes(valor)) {

                linha.style.display = "";

            } else {

                linha.style.display = "none";

            }

        });

    });

}
console.log("JS CLIENTES CARREGADO");