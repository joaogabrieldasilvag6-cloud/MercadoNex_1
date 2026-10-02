document.addEventListener("DOMContentLoaded", () => {
    const page = document.querySelector("[data-perfil-page]");
    if (!page) return;

    const toast = document.getElementById("perfilToast");
    const toastText = document.getElementById("perfilToastText");
    const formFoto = document.getElementById("formFoto");
    const formFotoInput = document.getElementById("formFotoInput");
    const btnAlterarFoto = document.getElementById("btnAlterarFoto");
    const btnTrocarFoto = document.getElementById("btnTrocarFoto");
    const btnRemoverFoto = document.getElementById("btnRemoverFoto");

    let toastTimer = null;

    function mostrarToast(mensagem, erro = false) {
        if (!toast || !toastText) return;

        clearTimeout(toastTimer);
        toastText.textContent = mensagem;
        toast.classList.toggle("error", erro);
        toast.classList.add("show");

        toastTimer = setTimeout(() => {
            toast.classList.remove("show");
        }, 3200);
    }

    function csrfToken() {
        const input = page.querySelector("input[name=csrfmiddlewaretoken]");
        return input?.value || "";
    }

    function abrirModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;

        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-open");
    }

    function fecharModal(id) {
        const modal = document.getElementById(id);
        if (!modal) return;

        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");

        if (!document.querySelector(".perfil-modal.open")) {
            document.body.classList.remove("modal-open");
        }
    }

    document.querySelectorAll("[data-open-modal]").forEach(button => {
        button.addEventListener("click", () => {
            abrirModal(button.dataset.openModal);
        });
    });

    document.querySelectorAll("[data-close-modal]").forEach(element => {
        element.addEventListener("click", () => {
            fecharModal(element.dataset.closeModal);
        });
    });

    document.addEventListener("keydown", event => {
        if (event.key !== "Escape") return;

        const aberto = document.querySelector(".perfil-modal.open");
        if (aberto) fecharModal(aberto.id);
    });

    document.querySelectorAll(".password-toggle").forEach(button => {
        button.addEventListener("click", () => {
            const target = document.getElementById(button.dataset.target);
            if (!target) return;

            const mostrar = target.type === "password";
            target.type = mostrar ? "text" : "password";

            const icon = button.querySelector("i");
            if (icon) {
                icon.classList.toggle("fa-eye", !mostrar);
                icon.classList.toggle("fa-eye-slash", mostrar);
            }

            button.setAttribute(
                "aria-label",
                mostrar ? "Ocultar senha" : "Mostrar senha"
            );
        });
    });

    async function enviarFormulario(form, options = {}) {
        const botao = form.querySelector("button[type=submit]");
        const textoOriginal = botao?.innerHTML;

        if (botao) {
            botao.disabled = true;
            botao.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';
        }

        try {
            const resposta = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: {
                    "X-CSRFToken": csrfToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const dados = await resposta.json().catch(() => ({}));

            if (!resposta.ok || !dados.success) {
                throw new Error(dados.erro || "Não foi possível salvar as alterações.");
            }

            fecharModal(options.modalId || "");
            mostrarToast(dados.mensagem || "Alterações salvas com sucesso.");

            if (options.reload !== false) {
                setTimeout(() => window.location.reload(), 650);
            }
        } catch (erro) {
            mostrarToast(erro.message || "Ocorreu um erro ao salvar.", true);
        } finally {
            if (botao) {
                botao.disabled = false;
                botao.innerHTML = textoOriginal;
            }
        }
    }

    const formEditarPerfil = document.getElementById("formEditarPerfil");
    if (formEditarPerfil) {
        formEditarPerfil.addEventListener("submit", event => {
            event.preventDefault();
            enviarFormulario(formEditarPerfil, {modalId: "modalEditarPerfil"});
        });
    }

    const formSenha = document.getElementById("formSenha");
    if (formSenha) {
        formSenha.addEventListener("submit", event => {
            event.preventDefault();

            const nova = document.getElementById("novaSenha")?.value || "";
            const confirmar = document.getElementById("confirmarSenha")?.value || "";

            if (nova !== confirmar) {
                mostrarToast("As novas senhas não coincidem.", true);
                return;
            }

            enviarFormulario(formSenha, {
                modalId: "modalSenha",
                reload: false
            }).then(() => {
                formSenha.reset();
            });
        });
    }

    const formEstabelecimento = document.getElementById("formEstabelecimento");
    if (formEstabelecimento) {
        formEstabelecimento.addEventListener("submit", event => {
            event.preventDefault();
            enviarFormulario(formEstabelecimento, {
                modalId: "modalEstabelecimento"
            });
        });
    }

    function abrirSeletorFoto() {
        if (formFotoInput) formFotoInput.click();
    }

    btnAlterarFoto?.addEventListener("click", abrirSeletorFoto);
    btnTrocarFoto?.addEventListener("click", abrirSeletorFoto);

    async function enviarFoto(arquivo) {
        if (!arquivo) return;

        if (!arquivo.type.startsWith("image/")) {
            mostrarToast("Selecione um arquivo de imagem.", true);
            return;
        }

        if (arquivo.size > 5 * 1024 * 1024) {
            mostrarToast("A imagem deve ter no máximo 5 MB.", true);
            return;
        }

        try {
            const resposta = await fetch(formFoto.action, {
                method: "POST",
                body: new FormData(formFoto),
                headers: {
                    "X-CSRFToken": csrfToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const dados = await resposta.json().catch(() => ({}));

            if (!resposta.ok || !dados.success) {
                throw new Error(dados.erro || "Não foi possível alterar a foto.");
            }

            mostrarToast(dados.mensagem || "Foto atualizada com sucesso.");

            const avatar = document.getElementById("perfilAvatar");
            if (avatar && dados.foto) {
                avatar.innerHTML = `<img src="${dados.foto}?t=${Date.now()}" alt="Foto de perfil" id="perfilAvatarImage">`;
            }

            setTimeout(() => window.location.reload(), 700);
        } catch (erro) {
            mostrarToast(erro.message || "Ocorreu um erro ao enviar a foto.", true);
        }
    }

    formFotoInput?.addEventListener("change", () => {
        enviarFoto(formFotoInput.files?.[0]);
    });

    btnRemoverFoto?.addEventListener("click", async () => {
        const confirmar = confirm("Deseja remover sua foto de perfil?");
        if (!confirmar) return;

        try {
            const resposta = await fetch(btnRemoverFoto.dataset.url || page.dataset.removerFotoUrl || "/perfil/foto/remover/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const dados = await resposta.json().catch(() => ({}));

            if (!resposta.ok || !dados.success) {
                throw new Error(dados.erro || "Não foi possível remover a foto.");
            }

            mostrarToast(dados.mensagem || "Foto removida com sucesso.");
            setTimeout(() => window.location.reload(), 650);
        } catch (erro) {
            mostrarToast(erro.message || "Ocorreu um erro ao remover a foto.", true);
        }
    });
});
