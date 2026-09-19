document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       ELEMENTOS
    ===================================================== */

    const sidebar =
        document.getElementById("sidebar");

    const sidebarOverlay =
        document.getElementById("sidebarOverlay");

    const mobileMenuButton =
        document.getElementById(
            "mobileMenuButton"
        );

    const mobileClose =
        document.getElementById(
            "mobileClose"
        );


    const userMenuButton =
        document.getElementById(
            "userMenuButton"
        );

    const userMenu =
        document.getElementById(
            "userMenu"
        );


    /* =====================================================
       MENU ATIVO
    ===================================================== */

    const currentPath =
        window.location.pathname;


    const navItems =
        document.querySelectorAll(
            ".nav-item[data-page]"
        );


    function ativarMenu(item) {

        navItems.forEach(nav => {

            nav.classList.remove(
                "active"
            );

            nav.removeAttribute(
                "aria-current"
            );

        });


        item.classList.add(
            "active"
        );

        item.setAttribute(
            "aria-current",
            "page"
        );

    }


    navItems.forEach(item => {

        const href =
            item.getAttribute("href");

        if (
            !href ||
            href === "#"
        ) {
            return;
        }


        try {

            const url =
                new URL(
                    href,
                    window.location.origin
                );


            let linkPath =
                url.pathname;


            /*
             * Remove barra final para
             * facilitar a comparação.
             */

            linkPath =
                linkPath.replace(
                    /\/$/,
                    ""
                );


            let path =
                currentPath.replace(
                    /\/$/,
                    ""
                );


            if (
                linkPath === path
            ) {

                ativarMenu(item);

            }

        } catch (erro) {

            console.warn(
                "Erro ao identificar menu:",
                erro
            );

        }

    });


    /* =====================================================
       MENU MOBILE
    ===================================================== */

    function abrirMenuMobile() {

        sidebar?.classList.add(
            "mobile-open"
        );

        sidebarOverlay?.classList.add(
            "visible"
        );

        document.body.style.overflow =
            "hidden";

    }


    function fecharMenuMobile() {

        sidebar?.classList.remove(
            "mobile-open"
        );

        sidebarOverlay?.classList.remove(
            "visible"
        );

        document.body.style.overflow =
            "";

    }


    mobileMenuButton?.addEventListener(
        "click",
        abrirMenuMobile
    );


    mobileClose?.addEventListener(
        "click",
        fecharMenuMobile
    );


    sidebarOverlay?.addEventListener(
        "click",
        fecharMenuMobile
    );


    /* =====================================================
       FECHAR MOBILE AO CLICAR NO MENU
    ===================================================== */

    navItems.forEach(item => {

        item.addEventListener(
            "click",
            () => {

                fecharMenuMobile();

            }
        );

    });


    /* =====================================================
       MENU DO USUÁRIO
    ===================================================== */

    function abrirUserMenu() {

        userMenu?.classList.add(
            "open"
        );

        userMenuButton?.setAttribute(
            "aria-expanded",
            "true"
        );

    }


    function fecharUserMenu() {

        userMenu?.classList.remove(
            "open"
        );

        userMenuButton?.setAttribute(
            "aria-expanded",
            "false"
        );

    }


    userMenuButton?.addEventListener(
        "click",
        event => {

            event.stopPropagation();


            if (
                userMenu?.classList.contains(
                    "open"
                )
            ) {

                fecharUserMenu();

            } else {

                abrirUserMenu();

            }

        }
    );


    document.addEventListener(
        "click",
        event => {

            if (
                userMenu &&
                userMenuButton &&
                !userMenu.contains(
                    event.target
                ) &&
                !userMenuButton.contains(
                    event.target
                )
            ) {

                fecharUserMenu();

            }

        }
    );


    /* =====================================================
       ESC
    ===================================================== */

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape"
            ) {

                fecharMenuMobile();

                fecharUserMenu();

            }

        }
    );


    /* =====================================================
       ANIMAÇÃO DA PÁGINA
    ===================================================== */

    const contentArea =
        document.querySelector(
            ".content-area"
        );


    if (contentArea) {

        contentArea.classList.add(
            "page-enter"
        );

    }


    console.log(
        "MercadoNex — dashboard.js carregado."
    );

});