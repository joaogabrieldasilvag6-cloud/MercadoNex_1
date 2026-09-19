document.addEventListener("DOMContentLoaded", () => {
    const cards = [...document.querySelectorAll(".product-card")];
    const cartList = document.getElementById("listaCarrinho");
    const cartEmpty = document.getElementById("carrinhoVazio");
    const search = document.getElementById("buscaProduto");
    const categoryButtons = [...document.querySelectorAll(".category-chip")];
    const cartBadge = document.getElementById("badgeCarrinho");
    const productCount = document.getElementById("quantidadeProdutos");
    const subtotalEl = document.getElementById("subtotalVenda");
    const discountEl = document.getElementById("valorDesconto");
    const totalEl = document.getElementById("totalVenda");
    const discountInput = document.getElementById("descontoVenda");
    const clientSelect = document.getElementById("clienteVenda");
    const paymentButtons = [...document.querySelectorAll(".payment-card")];
    const cashArea = document.getElementById("areaDinheiro");
    const cashInput = document.getElementById("valorRecebido");
    const changeEl = document.getElementById("trocoVenda");
    const finishButton = document.getElementById("btnFinalizarVenda");
    const newSaleButton = document.getElementById("btnNovaVenda");
    const overlay = document.getElementById("confirmacaoVenda");
    const closeConfirmation = document.getElementById("fecharConfirmacao");
    const cancelConfirmation = document.getElementById("cancelarConfirmacao");
    const confirmSale = document.getElementById("confirmarVenda");
    const confirmTotal = document.getElementById("confirmacaoTotal");
    const confirmPayment = document.getElementById("confirmacaoPagamento");
    const confirmItems = document.getElementById("confirmacaoItens");
    const confirmFiadoLine = document.getElementById("confirmacaoFiadoLinha");
    const confirmFiadoBalance = document.getElementById("confirmacaoSaldoFiado");
    const fiadoInfo = document.getElementById("infoFiadoCliente");
    const saldoFiadoEl = document.getElementById("saldoFiadoCliente");
    const disponivelFiadoEl = document.getElementById("disponivelFiadoCliente");
    const errorEl = document.getElementById("erroVenda");
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

    let cart = [];
    let selectedPayment = "PIX";
    let selectedCategory = "TODAS";
    let sending = false;

    const money = value => `R$ ${Number(value || 0).toFixed(2).replace(".", ",")}`;
    const paymentNames = { PIX: "PIX", DEBITO: "Débito", CREDITO: "Crédito", DINHEIRO: "Dinheiro", FIADO: "Fiado" };

    function getTotals() {
        const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
        const percent = Math.min(100, Math.max(0, Number(discountInput.value || 0)));
        const discount = subtotal * percent / 100;
        return { subtotal, discount, total: Math.max(0, subtotal - discount), percent };
    }

    function updateSummary() {
        const totals = getTotals();
        subtotalEl.textContent = money(totals.subtotal);
        discountEl.textContent = `- ${money(totals.discount)}`;
        totalEl.textContent = money(totals.total);
        const qty = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartBadge.textContent = `${qty} ${qty === 1 ? "item" : "itens"}`;
        updateChange(totals.total);
    }

    function updateFiadoInfo() {
        const option = clientSelect.options[clientSelect.selectedIndex];
        const isFiado = selectedPayment === "FIADO";
        if (!option || !option.value || !isFiado) {
            fiadoInfo.hidden = true;
            return;
        }
        const saldo = Number(option.dataset.saldo || 0);
        const limite = Number(option.dataset.limite || 0);
        const disponivel = Math.max(0, limite - saldo);
        saldoFiadoEl.textContent = money(saldo);
        disponivelFiadoEl.textContent = money(disponivel);
        fiadoInfo.hidden = false;
    }

    function updateChange(total = getTotals().total) {
        if (selectedPayment !== "DINHEIRO") {
            changeEl.textContent = money(0);
            return;
        }
        const received = Number(cashInput.value || 0);
        changeEl.textContent = money(Math.max(0, received - total));
        changeEl.style.color = received >= total ? "var(--pdv-green)" : "var(--pdv-red)";
    }

    function renderCart() {
        cartList.innerHTML = "";
        if (!cart.length) {
            cartList.appendChild(cartEmpty);
        } else {
            cart.forEach((item, index) => {
                const row = document.createElement("div");
                row.className = "cart-item";
                row.innerHTML = `
                    <div class="cart-item-main">
                        <h4></h4><small></small>
                        <div class="cart-item-controls">
                            <button class="qty-button" data-action="minus" data-index="${index}" type="button" aria-label="Diminuir">−</button>
                            <span class="qty-value">${item.quantity}</span>
                            <button class="qty-button" data-action="plus" data-index="${index}" type="button" aria-label="Aumentar">+</button>
                            <button class="remove-item" data-action="remove" data-index="${index}" type="button" aria-label="Remover"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    </div>
                    <div class="cart-item-price">${money(item.price * item.quantity)}</div>`;
                row.querySelector("h4").textContent = item.name;
                row.querySelector("small").textContent = `${money(item.price)} · cód. ${item.code}`;
                cartList.appendChild(row);
            });
        }
        updateSummary();
    }

    function addProduct(card) {
        const id = Number(card.dataset.id);
        const stock = Number(card.dataset.stock);
        const existing = cart.find(item => item.id === id);
        if (existing) {
            if (existing.quantity >= stock) return;
            existing.quantity += 1;
        } else {
            cart.push({ id, name: card.querySelector("h3").textContent.trim(), code: card.dataset.code, price: Number(card.dataset.price), quantity: 1, stock });
        }
        renderCart();
    }

    cards.forEach(card => card.querySelector(".add-product")?.addEventListener("click", () => addProduct(card)));

    cartList.addEventListener("click", event => {
        const button = event.target.closest("button[data-action]");
        if (!button) return;
        const index = Number(button.dataset.index);
        const item = cart[index];
        if (!item) return;
        if (button.dataset.action === "plus" && item.quantity < item.stock) item.quantity += 1;
        if (button.dataset.action === "minus") item.quantity -= 1;
        if (button.dataset.action === "remove" || item.quantity <= 0) cart.splice(index, 1);
        renderCart();
    });

    function filterProducts() {
        const term = search.value.trim().toLowerCase();
        let visible = 0;
        cards.forEach(card => {
            const matchesTerm = !term || card.dataset.name.includes(term) || card.dataset.code.includes(term);
            const matchesCategory = selectedCategory === "TODAS" || card.dataset.category === selectedCategory;
            const show = matchesTerm && matchesCategory;
            card.hidden = !show;
            if (show) visible++;
        });
        productCount.textContent = visible;
        document.getElementById("semResultados").hidden = visible !== 0;
    }

    search.addEventListener("input", filterProducts);
    categoryButtons.forEach(button => button.addEventListener("click", () => {
        categoryButtons.forEach(item => item.classList.remove("active"));
        button.classList.add("active");
        selectedCategory = button.dataset.category;
        filterProducts();
    }));

    clientSelect.addEventListener("change", () => updateFiadoInfo());

    discountInput.addEventListener("input", () => {
        let value = Number(discountInput.value || 0);
        value = Math.min(100, Math.max(0, value));
        discountInput.value = value;
        updateSummary();
    });

    paymentButtons.forEach(button => button.addEventListener("click", () => {
        paymentButtons.forEach(item => item.classList.remove("active"));
        button.classList.add("active");
        selectedPayment = button.dataset.payment;
        cashArea.hidden = selectedPayment !== "DINHEIRO";
        updateChange();
        updateFiadoInfo();
    }));
    cashInput.addEventListener("input", () => updateChange());

    function openConfirmation() {
        errorEl.hidden = true;
        if (!cart.length) return alert("Adicione pelo menos um produto ao carrinho.");
        const total = getTotals().total;
        if (selectedPayment === "DINHEIRO" && Number(cashInput.value || 0) < total) {
            return alert("O valor recebido é menor que o total da venda.");
        }
        if (selectedPayment === "FIADO") {
            const option = clientSelect.options[clientSelect.selectedIndex];
            if (!option || !option.value) return alert("Para vender fiado, selecione um cliente.");
            if (option.dataset.ativoFiado !== "1") return alert("O fiado deste cliente está desativado.");
            const saldo = Number(option.dataset.saldo || 0);
            const limite = Number(option.dataset.limite || 0);
            if (saldo + total > limite + 0.0001) return alert(`Limite de fiado excedido. Disponível: ${money(Math.max(0, limite - saldo))}.`);
            confirmFiadoLine.hidden = false;
            confirmFiadoBalance.textContent = money(saldo + total);
        } else {
            confirmFiadoLine.hidden = true;
        }
        confirmTotal.textContent = money(total);
        confirmPayment.textContent = paymentNames[selectedPayment];
        confirmItems.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
        overlay.hidden = false;
    }

    function closeModal() { overlay.hidden = true; }
    finishButton.addEventListener("click", openConfirmation);
    closeConfirmation.addEventListener("click", closeModal);
    cancelConfirmation.addEventListener("click", closeModal);
    overlay.addEventListener("click", e => { if (e.target === overlay) closeModal(); });

    async function finalizeSale() {
        if (sending) return;
        sending = true;
        confirmSale.disabled = true;
        confirmSale.textContent = "Registrando...";
        errorEl.hidden = true;
        const totals = getTotals();
        const payload = {
            cliente: clientSelect.value || null,
            forma_pagamento: selectedPayment,
            desconto_percentual: totals.percent,
            valor_recebido: selectedPayment === "DINHEIRO" ? Number(cashInput.value || 0) : null,
            itens: cart.map(item => ({ id: item.id, quantidade: item.quantity }))
        };
        try {
            const url = document.getElementById("formFinalizarVenda").dataset.finalizarUrl || "/vendas/finalizar/";
            const response = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json", "X-CSRFToken": csrf, "X-Requested-With": "XMLHttpRequest" }, body: JSON.stringify(payload) });
            const data = await response.json();
            if (!response.ok || !data.sucesso) throw new Error(data.erro || "Não foi possível finalizar a venda.");
            closeModal();
            const extra = selectedPayment === "FIADO" ? `\nNovo saldo fiado: ${money(data.novo_saldo_fiado)}` : "";
            alert(`Venda #${data.venda_id} registrada com sucesso!\nTotal: ${money(data.valor_final)}${extra}`);
            window.location.reload();
        } catch (error) {
            errorEl.textContent = error.message;
            errorEl.hidden = false;
        } finally {
            sending = false;
            confirmSale.disabled = false;
            confirmSale.textContent = "Confirmar Venda";
        }
    }
    confirmSale.addEventListener("click", finalizeSale);

    function resetSale() {
        cart = [];
        clientSelect.value = "";
        discountInput.value = 0;
        cashInput.value = "";
        selectedPayment = "PIX";
        confirmFiadoLine.hidden = true;
        paymentButtons.forEach((button, index) => button.classList.toggle("active", index === 0));
        cashArea.hidden = true;
        renderCart();
        search.focus();
    }
    newSaleButton.addEventListener("click", resetSale);

    document.addEventListener("keydown", event => {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
            event.preventDefault(); search.focus(); search.select();
        }
        if (event.key === "Escape" && !overlay.hidden) closeModal();
        if (event.key === "Enter" && !overlay.hidden && !event.target.matches("input, select, textarea, button")) finalizeSale();
    });

    productCount.textContent = cards.length;
    renderCart();
    updateFiadoInfo();
});
