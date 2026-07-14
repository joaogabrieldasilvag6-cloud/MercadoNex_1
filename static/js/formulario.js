const modal = document.getElementById("modalProduto");
const btn = document.getElementById("btnCadastrar");
const fecharProduto = document.querySelector(".fechar");

btn.onclick = () => {
    modal.style.display = "flex";
};

fecharProduto.onclick = () => {
    modal.style.display = "none";
};

window.onclick = (e) => {
    if (e.target === modal) {
        modal.style.display = "none";
    }
};