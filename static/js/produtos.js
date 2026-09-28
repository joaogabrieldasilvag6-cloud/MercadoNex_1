/* MercadoNex — Gestão de Produtos */
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("modalProduto");
    const form = document.getElementById("product-form");
    const btnCadastrar = document.getElementById("btnCadastrar");
    const btnFechar = document.getElementById("btnFecharModal");
    const btnCancelar = document.getElementById("btnCancelarProduto");
    const modalTitulo = document.getElementById("modalProdutoTitulo");
    const modalSubtitle = document.getElementById("modalProdutoSubtitle");
    const btnSalvar = document.getElementById("btnSalvarProduto");
    const inputImagem = document.getElementById("img-upload");
    const fileDrop = document.getElementById("fileDrop");
    const preview = document.getElementById("uploadPreview");
    const uploadTitle = document.getElementById("uploadTitle");
    const uploadSubtitle = document.getElementById("uploadSubtitle");
    const uploadIcon = document.querySelector(".produto-upload-icon");

    function abrirModal(){ if(!modal)return; modal.classList.add("show"); modal.setAttribute("aria-hidden","false"); document.body.classList.add("modal-produto-open"); setTimeout(()=>form?.elements["nome"]?.focus(),120); }
    function fecharModal(){ if(!modal)return; modal.classList.remove("show"); modal.setAttribute("aria-hidden","true"); document.body.classList.remove("modal-produto-open"); }
    window.fecharModalProduto = fecharModal;

    function novoProduto(){
        if(!form)return;
        form.reset(); form.action="/produtos/cadastrar/";
        if(modalTitulo) modalTitulo.innerHTML='<i class="fa-solid fa-box"></i> Novo Produto';
        if(modalSubtitle) modalSubtitle.textContent="Preencha os dados abaixo para cadastrar o produto.";
        if(btnSalvar) btnSalvar.innerHTML='<i class="fa-regular fa-floppy-disk"></i><span>Salvar Produto</span>';
        if(form.elements["status"]) form.elements["status"].checked=true;
        if(form.elements["destaque"]) form.elements["destaque"].checked=false;
        limparPreview(); abrirModal();
    }
    btnCadastrar?.addEventListener("click", novoProduto);

    window.editarProduto = async function(id){
        if(!form || !modal)return;
        try{
            const resposta=await fetch(`/produtos/json/${id}/`,{headers:{"X-Requested-With":"XMLHttpRequest","Accept":"application/json"}});
            if(!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
            const produto=await resposta.json();
            form.action=`/produtos/editar/${id}/`;
            ["nome","categoria","descricao","codigo","marca","preco_venda","preco_custo","quantidade","validade","fornecedor"].forEach(nome=>{if(form.elements[nome])form.elements[nome].value=produto[nome]??"";});
            if(form.elements["status"]) form.elements["status"].checked=produto.status===true||produto.status===1||produto.status==="1";
            if(form.elements["destaque"]) form.elements["destaque"].checked=produto.destaque===true||produto.destaque===1||produto.destaque==="1";
            if(modalTitulo) modalTitulo.innerHTML='<i class="fa-solid fa-pen"></i> Editar Produto';
            if(modalSubtitle) modalSubtitle.textContent="Atualize os dados do produto e salve as alterações.";
            if(btnSalvar) btnSalvar.innerHTML='<i class="fa-solid fa-pen"></i><span>Atualizar Produto</span>';
            limparPreview();
            if(produto.imagem) mostrarPreview(produto.imagem,"Imagem atual");
            abrirModal();
        }catch(erro){ console.error(erro); alert("Não foi possível carregar os dados do produto."); }
    };

    function mostrarPreview(url,nome){
        if(!preview)return;
        preview.src=url; preview.style.display="block";
        if(uploadIcon) uploadIcon.style.display="none";
        if(uploadTitle) uploadTitle.textContent="Imagem selecionada";
        if(uploadSubtitle) uploadSubtitle.textContent=nome||"Imagem atual";
    }
    function limparPreview(){
        if(preview){preview.removeAttribute("src");preview.style.display="none";}
        if(uploadIcon) uploadIcon.style.display="grid";
        if(uploadTitle) uploadTitle.textContent="Clique para selecionar uma imagem";
        if(uploadSubtitle) uploadSubtitle.textContent="PNG, JPG ou WEBP";
        if(inputImagem) inputImagem.value="";
    }

    btnFechar?.addEventListener("click",fecharModal);
    btnCancelar?.addEventListener("click",fecharModal);
    modal?.addEventListener("click",e=>{if(e.target.matches("[data-modal-close]"))fecharModal();});
    document.addEventListener("keydown",e=>{if(e.key==="Escape"&&modal?.classList.contains("show"))fecharModal();});

    fileDrop?.addEventListener("click",()=>inputImagem?.click());
    inputImagem?.addEventListener("change",()=>{const arquivo=inputImagem.files?.[0]; if(!arquivo)return; if(!arquivo.type.startsWith("image/")){alert("Selecione uma imagem válida.");inputImagem.value="";limparPreview();return;} mostrarPreview(URL.createObjectURL(arquivo),arquivo.name);});
    fileDrop?.addEventListener("dragover",e=>{e.preventDefault();fileDrop.classList.add("dragover")});
    fileDrop?.addEventListener("dragleave",()=>fileDrop.classList.remove("dragover"));
    fileDrop?.addEventListener("drop",e=>{e.preventDefault();fileDrop.classList.remove("dragover");const arquivo=e.dataTransfer.files?.[0];if(!arquivo)return;if(!arquivo.type.startsWith("image/")){alert("Solte apenas arquivos de imagem.");return;}try{const dt=new DataTransfer();dt.items.add(arquivo);inputImagem.files=dt.files;}catch(_){ }mostrarPreview(URL.createObjectURL(arquivo),arquivo.name);});

    form?.addEventListener("submit",e=>{
        if(form.dataset.enviando==="true"){e.preventDefault();return;}
        form.dataset.enviando="true";
        if(btnSalvar){btnSalvar.disabled=true;btnSalvar.innerHTML='<i class="fa-solid fa-spinner fa-spin"></i><span>Salvando...</span>';}
    });

    console.log("MercadoNex — produtos.js carregado.");
});
