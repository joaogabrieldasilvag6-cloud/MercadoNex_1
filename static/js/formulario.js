const modal = document.getElementById("modalProduto");
const btn = document.getElementById("btnCadastrar");
const fecharProduto = document.querySelector(".fechar");

if (modal && btn && fecharProduto) {

    btn.onclick = () => {
        modal.style.display = "flex";
    };

    fecharProduto.onclick = () => {
        modal.style.display = "none";
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

}