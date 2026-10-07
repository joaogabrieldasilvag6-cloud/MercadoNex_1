document.addEventListener("DOMContentLoaded", () => {
    const modal = document.querySelector("[data-modal]");
    const openButtons = document.querySelectorAll("[data-open-modal]");
    const closeButtons = document.querySelectorAll("[data-close-modal]");
    const valueInput = document.querySelector('input[name="valor"]');
    const typeInputs = document.querySelectorAll('input[name="tipo"]');
    const status = document.querySelector('select[name="status"]');

    function openModal() {
        if (!modal) return;
        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        const first = modal.querySelector('input[name="descricao"]');
        if (first) setTimeout(() => first.focus(), 80);
    }

    function closeModal() {
        if (!modal) return;
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
    }

    openButtons.forEach(button => button.addEventListener("click", openModal));
    closeButtons.forEach(button => button.addEventListener("click", closeModal));

    if (modal) {
        modal.addEventListener("click", event => {
            if (event.target === modal) closeModal();
        });
    }

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") closeModal();
    });

    document.querySelectorAll(".delete-finance-form").forEach(form => {
        form.addEventListener("submit", event => {
            if (!confirm("Excluir esta movimentação financeira?")) event.preventDefault();
        });
    });

    if (valueInput) {
        valueInput.addEventListener("blur", () => {
            const value = valueInput.value.trim().replace(",", ".");
            if (value && !Number.isNaN(Number(value))) {
                valueInput.value = Number(value).toFixed(2).replace(".", ",");
            }
        });
    }

    typeInputs.forEach(input => {
        input.addEventListener("change", () => {
            if (status && input.checked && input.value === "ENTRADA") {
                status.value = "PAGA";
            }
        });
    });
});
