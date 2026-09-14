/* =========================================================
   MERCADONEX — DASHBOARD.JS
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const navItems = document.querySelectorAll(".nav-item");
    const sections = document.querySelectorAll(".content-section");

    const pageTitle = document.getElementById("pageTitle");
    const pageSubtitle = document.getElementById("pageSubtitle");
    const pageHeading = document.getElementById("pageHeading");

    const sidebar = document.getElementById("sidebar");
    const sidebarOverlay = document.getElementById("sidebarOverlay");
    const mobileMenuButton = document.getElementById("mobileMenuButton");
    const mobileClose = document.getElementById("mobileClose");

    const userMenuButton = document.getElementById("userMenuButton");
    const userMenu = document.getElementById("userMenu");

    let currentSection = document.querySelector(".content-section.active");
    let isChangingSection = false;

    /* =====================================================
       TROCA DE SEÇÃO
    ===================================================== */

    function changeSection(sectionName, title, subtitle, updateUrl = true) {

        if (isChangingSection) return;

        const nextSection = document.querySelector(
            `.content-section[data-section="${sectionName}"]`
        );

        if (!nextSection || nextSection === currentSection) {
            closeMobileMenu();
            return;
        }

        isChangingSection = true;

        /* Atualiza item ativo do menu */
        navItems.forEach(item => {
            const isActive = item.dataset.section === sectionName;
            item.classList.toggle("active", isActive);

            if (isActive) {
                item.setAttribute("aria-current", "page");
            } else {
                item.removeAttribute("aria-current");
            }
        });

        /* Animação do título */
        pageHeading.classList.add("changing");

        /* Animação de saída */
        if (currentSection) {
            currentSection.classList.add("leaving");

            setTimeout(() => {
                currentSection.classList.remove("active", "leaving");
            }, 160);
        }

        /* Entra a nova seção */
        setTimeout(() => {

            nextSection.classList.add("active");

            pageTitle.textContent = title || "MercadoNex";
            pageSubtitle.textContent = subtitle || "";

            requestAnimationFrame(() => {
                pageHeading.classList.remove("changing");
            });

            currentSection = nextSection;
            isChangingSection = false;

        }, 175);

        /* Atualiza hash sem recarregar */
        if (updateUrl) {
            history.pushState(
                { section: sectionName },
                "",
                `#${sectionName}`
            );
        }

        closeMobileMenu();
        closeUserMenu();
    }

    /* =====================================================
       EVENTOS DO MENU
    ===================================================== */

    navItems.forEach(item => {

        item.addEventListener("click", () => {

            const section = item.dataset.section;
            const title = item.dataset.title;
            const subtitle = item.dataset.subtitle;

            changeSection(section, title, subtitle);
        });

    });

    /* Logo volta para o dashboard */
    document.querySelectorAll("[data-section='dashboard'].brand-link")
        .forEach(link => {

            link.addEventListener("click", event => {
                event.preventDefault();

                const dashboardButton =
                    document.querySelector(".nav-item[data-section='dashboard']");

                changeSection(
                    "dashboard",
                    dashboardButton?.dataset.title || "Painel Inicial",
                    dashboardButton?.dataset.subtitle || "Visão geral do seu mercadinho"
                );
            });

        });

    /* Botões "Voltar ao painel" */
    document.querySelectorAll("[data-back-dashboard]").forEach(button => {

        button.addEventListener("click", () => {

            const dashboardButton =
                document.querySelector(".nav-item[data-section='dashboard']");

            changeSection(
                "dashboard",
                dashboardButton?.dataset.title || "Painel Inicial",
                dashboardButton?.dataset.subtitle || "Visão geral do seu mercadinho"
            );

        });

    });

    /* =====================================================
       HASH DA URL
    ===================================================== */

    function loadSectionFromHash() {

        const hash = window.location.hash.replace("#", "");

        if (!hash) return;

        const item = document.querySelector(
            `.nav-item[data-section="${hash}"]`
        );

        if (!item) return;

        /* Inicialização sem criar histórico */
        const section = document.querySelector(
            `.content-section[data-section="${hash}"]`
        );

        if (!section) return;

        navItems.forEach(nav => {
            const active = nav.dataset.section === hash;
            nav.classList.toggle("active", active);

            if (active) {
                nav.setAttribute("aria-current", "page");
            }
        });

        sections.forEach(sec => sec.classList.remove("active"));

        section.classList.add("active");

        pageTitle.textContent = item.dataset.title;
        pageSubtitle.textContent = item.dataset.subtitle;

        currentSection = section;
    }

    window.addEventListener("popstate", () => {

        const hash = window.location.hash.replace("#", "") || "dashboard";

        const item = document.querySelector(
            `.nav-item[data-section="${hash}"]`
        );

        if (!item) return;

        changeSection(
            hash,
            item.dataset.title,
            item.dataset.subtitle,
            false
        );
    });

    loadSectionFromHash();

    /* =====================================================
       MENU MOBILE
    ===================================================== */

    function openMobileMenu() {
        sidebar.classList.add("mobile-open");
        sidebarOverlay.classList.add("visible");
        document.body.style.overflow = "hidden";
    }

    function closeMobileMenu() {
        sidebar.classList.remove("mobile-open");
        sidebarOverlay.classList.remove("visible");
        document.body.style.overflow = "";
    }

    mobileMenuButton?.addEventListener("click", openMobileMenu);
    mobileClose?.addEventListener("click", closeMobileMenu);
    sidebarOverlay?.addEventListener("click", closeMobileMenu);

    /* ESC fecha menus */
    document.addEventListener("keydown", event => {

        if (event.key !== "Escape") return;

        closeMobileMenu();
        closeUserMenu();

    });

    /* =====================================================
       MENU DO USUÁRIO
    ===================================================== */

    function openUserMenu() {
        userMenu.classList.add("open");
        userMenuButton.setAttribute("aria-expanded", "true");
    }

    function closeUserMenu() {
        userMenu?.classList.remove("open");
        userMenuButton?.setAttribute("aria-expanded", "false");
    }

    userMenuButton?.addEventListener("click", event => {

        event.stopPropagation();

        const isOpen = userMenu.classList.contains("open");

        if (isOpen) {
            closeUserMenu();
        } else {
            openUserMenu();
        }

    });

    document.addEventListener("click", event => {

        if (
            userMenu &&
            !userMenu.contains(event.target) &&
            !userMenuButton.contains(event.target)
        ) {
            closeUserMenu();
        }

    });

    /* =====================================================
       ANIMAÇÃO DOS CARDS AO CARREGAR
    ===================================================== */

    const animatedElements = document.querySelectorAll(
        ".stat-card, .panel-card, .stock-alert"
    );

    animatedElements.forEach((element, index) => {

        element.style.opacity = "0";
        element.style.transform = "translateY(8px)";

        setTimeout(() => {

            element.style.transition =
                "opacity .35s ease, transform .35s cubic-bezier(.2,.8,.2,1)";

            element.style.opacity = "1";
            element.style.transform = "translateY(0)";

        }, 80 + (index * 45));

    });

    /* =====================================================
       MICROINTERAÇÃO — ESTOQUE
    ===================================================== */

    document.querySelectorAll(".stock-item").forEach(item => {

        item.addEventListener("click", () => {

            item.animate(
                [
                    { transform: "scale(1)" },
                    { transform: "scale(.98)" },
                    { transform: "scale(1)" }
                ],
                {
                    duration: 180,
                    easing: "ease-out"
                }
            );

        });

    });

});
