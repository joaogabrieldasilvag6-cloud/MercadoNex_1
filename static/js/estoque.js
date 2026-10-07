document.addEventListener("DOMContentLoaded", () => {
    const page = document.querySelector(".estoque-page");
    const rows = [...document.querySelectorAll(".estoque-row")];
    const tbody = document.getElementById("estoqueTableBody");
    const search = document.getElementById("estoqueSearch");
    const categoria = document.getElementById("estoqueCategoria");
    const status = document.getElementById("estoqueStatus");
    const validade = document.getElementById("estoqueValidade");
    const summary = document.getElementById("tableSummary");
    const pagination = document.getElementById("pagination");
    const checkAll = document.getElementById("checkAll");
    const btnExportar = document.getElementById("btnExportar");
    const modal = document.getElementById("estoqueModalBackdrop");
    const modalForm = document.getElementById("estoqueMovimentacaoForm");
    const modalTitle = document.getElementById("estoqueModalTitle");
    const modalProdutoId = document.getElementById("modalProdutoId");
    const modalProdutoSelect = document.getElementById("modalProdutoSelect");
    const modalTipo = document.getElementById("modalTipo");
    const modalQuantidade = document.getElementById("modalQuantidade");
    const modalNovoEstoque = document.getElementById("modalNovoEstoque");
    const novoEstoqueWrap = document.getElementById("novoEstoqueWrap");
    const currentStockInfo = document.getElementById("currentStockInfo");
    const feedback = document.getElementById("formFeedback");
    const toast = document.getElementById("estoqueToast");
    let currentRows = [...rows];
    let currentPage = 1;
    const pageSize = 8;

    function toastMsg(message) {
        toast.textContent = message;
        toast.classList.add("show");
        clearTimeout(window.__estoqueToastTimer);
        window.__estoqueToastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
    }

    function parseDate(value) {
        if (!value) return null;
        const d = new Date(value + "T00:00:00");
        return Number.isNaN(d.getTime()) ? null : d;
    }

    function applyFilters() {
        const q = (search?.value || "").trim().toLowerCase();
        const cat = (categoria?.value || "").toLowerCase();
        const st = (status?.value || "").toLowerCase();
        const val = validade?.value || "";
        const today = new Date(); today.setHours(0,0,0,0);

        currentRows = rows.filter(row => {
            const name = row.dataset.name || "";
            const code = row.dataset.code || "";
            const rowCat = row.dataset.category || "";
            const rowStatus = row.dataset.status || "";
            const expiry = parseDate(row.dataset.expiry || "");
            let matchValidity = true;

            if (val === "7") matchValidity = expiry ? ((expiry - today) / 86400000 >= 0 && (expiry - today) / 86400000 <= 7) : false;
            if (val === "30") matchValidity = expiry ? ((expiry - today) / 86400000 >= 0 && (expiry - today) / 86400000 <= 30) : false;
            if (val === "sem") matchValidity = !expiry;

            return (!q || name.includes(q) || code.includes(q)) && (!cat || rowCat === cat) && (!st || rowStatus === st) && matchValidity;
        });

        currentPage = 1;
        renderPage();
    }

    function renderPage() {
        rows.forEach(row => row.style.display = "none");
        const total = currentRows.length;
        const pages = Math.max(1, Math.ceil(total / pageSize));
        if (currentPage > pages) currentPage = pages;
        const start = (currentPage - 1) * pageSize;
        currentRows.slice(start, start + pageSize).forEach(row => row.style.display = "");
        summary.textContent = total ? `Mostrando ${start + 1}-${Math.min(start + pageSize, total)} de ${total} produtos` : "Mostrando 0 produtos";
        renderPagination(pages);
        syncCheckAll();
    }

    function renderPagination(pages) {
        pagination.innerHTML = "";
        const prev = document.createElement("button");
        prev.className = "page-btn";
        prev.textContent = "Anterior";
        prev.disabled = currentPage <= 1;
        prev.onclick = () => { currentPage--; renderPage(); };
        pagination.appendChild(prev);

        for (let i = 1; i <= pages; i++) {
            if (pages > 7 && i > 3 && i < pages - 2) {
                if (!pagination.querySelector(".ellipsis")) {
                    const span = document.createElement("span");
                    span.className = "ellipsis";
                    span.textContent = "…";
                    span.style.cssText = "padding:0 3px;color:#94A3B8;font-size:9px;";
                    pagination.appendChild(span);
                }
                continue;
            }
            const button = document.createElement("button");
            button.className = `page-btn${i === currentPage ? " active" : ""}`;
            button.textContent = i;
            button.onclick = () => { currentPage = i; renderPage(); };
            pagination.appendChild(button);
        }

        const next = document.createElement("button");
        next.className = "page-btn";
        next.textContent = "Próxima";
        next.disabled = currentPage >= pages;
        next.onclick = () => { currentPage++; renderPage(); };
        pagination.appendChild(next);
    }

    function syncCheckAll() {
        const visibleChecks = currentRows.slice((currentPage - 1) * pageSize, currentPage * pageSize).map(row => row.querySelector(".row-check")).filter(Boolean);
        checkAll.checked = visibleChecks.length > 0 && visibleChecks.every(input => input.checked);
        checkAll.indeterminate = visibleChecks.some(input => input.checked) && !checkAll.checked;
    }

    function openModal(type = "entrada", id = "", nome = "", quantidade = "") {
        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
        modalTipo.value = type;
        modalProdutoId.value = id || "";
        if (id) modalProdutoSelect.value = String(id);
        if (!modalProdutoSelect.value && nome) {
            const option = [...modalProdutoSelect.options].find(o => o.textContent.trim().toLowerCase() === nome.trim().toLowerCase());
            if (option) modalProdutoSelect.value = option.value;
        }
        modalTitle.textContent = type === "ajuste" ? "Ajustar estoque" : "Registrar entrada";
        novoEstoqueWrap.classList.toggle("is-hidden", type !== "ajuste");
        modalQuantidade.required = type !== "ajuste";
        modalNovoEstoque.required = type === "ajuste";
        modalQuantidade.value = type === "ajuste" ? "" : (quantidade || "");
        modalNovoEstoque.value = type === "ajuste" ? (quantidade || "") : "";
        updateCurrentStock();
        feedback.textContent = "";
        feedback.className = "form-feedback";
    }

    function closeModal() {
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
        modalForm.reset();
        modalProdutoId.value = "";
    }

    function updateCurrentStock() {
        const id = modalProdutoSelect.value;
        const row = rows.find(r => r.querySelector(".row-check") && r.dataset && r.querySelector(`.row-menu [data-id="${id}"]`));
        const qty = row ? Number(row.dataset.stock || 0) : null;
        currentStockInfo.innerHTML = `Estoque atual: <strong>${qty === null ? "—" : qty.toLocaleString("pt-BR")}</strong>`;
        if (modalTipo.value === "ajuste" && qty !== null && !modalNovoEstoque.value) modalNovoEstoque.value = qty;
    }

    search?.addEventListener("input", applyFilters);
    categoria?.addEventListener("change", applyFilters);
    status?.addEventListener("change", applyFilters);
    validade?.addEventListener("change", applyFilters);

    checkAll?.addEventListener("change", () => {
        currentRows.slice((currentPage - 1) * pageSize, currentPage * pageSize).forEach(row => {
            const checkbox = row.querySelector(".row-check");
            if (checkbox) checkbox.checked = checkAll.checked;
        });
    });

    document.querySelectorAll(".row-check").forEach(input => input.addEventListener("change", syncCheckAll));

    document.querySelectorAll(".row-menu-btn").forEach(button => {
        button.addEventListener("click", event => {
            event.stopPropagation();
            document.querySelectorAll(".row-menu.open").forEach(menu => { if (menu !== button.parentElement) menu.classList.remove("open"); });
            button.parentElement.classList.toggle("open");
        });
    });

    document.querySelectorAll(".row-menu-dropdown button").forEach(button => {
        button.addEventListener("click", () => {
            openModal(button.dataset.action, button.dataset.id, button.dataset.nome, button.dataset.quantidade || "");
            button.closest(".row-menu").classList.remove("open");
        });
    });

    document.addEventListener("click", () => document.querySelectorAll(".row-menu.open").forEach(menu => menu.classList.remove("open")));

    document.getElementById("btnRegistrarEntrada")?.addEventListener("click", () => openModal("entrada"));
    document.getElementById("estoqueModalClose")?.addEventListener("click", closeModal);
    document.getElementById("estoqueModalCancel")?.addEventListener("click", closeModal);
    modal?.addEventListener("click", e => { if (e.target === modal) closeModal(); });
    modalProdutoSelect?.addEventListener("change", () => {
        modalProdutoId.value = modalProdutoSelect.value;
        updateCurrentStock();
    });
    modalTipo?.addEventListener("change", updateCurrentStock);

    modalForm?.addEventListener("submit", async e => {
        e.preventDefault();
        const type = modalTipo.value;
        const endpoint = type === "ajuste" ? "/estoque/ajustar/" : "/estoque/registrar-entrada/";
        const formData = new FormData(modalForm);
        if (!formData.get("produto_id")) formData.set("produto_id", modalProdutoSelect.value);

        feedback.textContent = "Salvando...";
        feedback.className = "form-feedback";

        try {
            const response = await fetch(endpoint, { method: "POST", body: formData, headers: {"X-Requested-With":"XMLHttpRequest"} });
            const data = await response.json();
            if (!response.ok || !data.sucesso) throw new Error(data.mensagem || "Não foi possível salvar a movimentação.");
            feedback.textContent = data.mensagem;
            feedback.className = "form-feedback success";
            toastMsg(data.mensagem);
            setTimeout(() => window.location.reload(), 650);
        } catch (error) {
            feedback.textContent = error.message;
            feedback.className = "form-feedback error";
        }
    });

    btnExportar?.addEventListener("click", () => {
        const params = new URLSearchParams();
        if (search.value) params.set("q", search.value);
        if (categoria.value) params.set("categoria", categoria.value);
        if (status.value) params.set("status", status.value);
        window.location.href = `/estoque/exportar/?${params.toString()}`;
    });

    document.getElementById("btnMaisFiltros")?.addEventListener("click", () => {
        validade.focus();
        toastMsg("Use os filtros de validade para refinar a lista.");
    });

    document.querySelectorAll("[data-scroll-target]").forEach(button => {
        button.addEventListener("click", () => {
            const id = button.dataset.scrollTarget;
            document.getElementById(id)?.scrollIntoView({behavior:"smooth", block:"start"});
        });
    });

    document.getElementById("btnCriarPedido")?.addEventListener("click", () => toastMsg("A área de compras pode receber o pedido de reposição."));
    renderPage();
});
