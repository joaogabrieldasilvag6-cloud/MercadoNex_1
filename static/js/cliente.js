document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modalCliente');
    const btnNovo = document.getElementById('btnNovoCliente');
    const btnFechar = document.getElementById('fecharModal');
    const btnCancelar = document.getElementById('cancelarModal');
    const busca = document.getElementById('buscarCliente');
    const tbody = document.getElementById('clientes-tbody');
    const resultCount = document.getElementById('resultCount');
    const inadimplentesCard = document.getElementById('clientesInadimplentes');
    const form = document.getElementById('cliente-form');

    let filtroAtual = 'todos';

    const rows = () => Array.from(document.querySelectorAll('.cliente-row'));

    function abrirModal() {
        if (!modal) return;
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-aberto');
        const primeiro = document.getElementById('clienteNome');
        if (primeiro) setTimeout(() => primeiro.focus(), 80);
    }

    function fecharModal() {
        if (!modal) return;
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-aberto');
    }

    function normalizar(texto) {
        return (texto || '').toString().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }

    function aplicarFiltros() {
        const termo = normalizar(busca?.value);
        let visiveis = 0;
        let inadimplentes = 0;

        rows().forEach(row => {
            const status = row.dataset.status || '';
            const texto = normalizar(row.dataset.search || row.textContent);
            const passaStatus = filtroAtual === 'todos' || status === filtroAtual;
            const passaBusca = !termo || texto.includes(termo);
            const mostrar = passaStatus && passaBusca;

            row.classList.toggle('is-hidden', !mostrar);
            if (mostrar) visiveis++;
            if (status === 'inadimplente') inadimplentes++;
        });

        if (resultCount) {
            resultCount.textContent = `${visiveis} ${visiveis === 1 ? 'resultado' : 'resultados'}`;
        }
        if (inadimplentesCard) inadimplentesCard.textContent = inadimplentes;

        const vazio = document.getElementById('clientesSemFiltro');
        if (vazio) vazio.remove();
        if (tbody && visiveis === 0 && rows().length > 0) {
            const tr = document.createElement('tr');
            tr.id = 'clientesSemFiltro';
            tr.innerHTML = `<td colspan="6" class="sem-registros"><i class="fa-solid fa-magnifying-glass"></i><strong>Nenhum cliente encontrado.</strong><span>Tente outro nome, CPF, telefone ou filtro.</span></td>`;
            tbody.appendChild(tr);
        }
    }

    btnNovo?.addEventListener('click', abrirModal);
    btnFechar?.addEventListener('click', fecharModal);
    btnCancelar?.addEventListener('click', fecharModal);
    modal?.querySelector('[data-close-modal]')?.addEventListener('click', fecharModal);
    busca?.addEventListener('input', aplicarFiltros);

    document.querySelectorAll('.status-filter').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.status-filter').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            filtroAtual = button.dataset.filter || 'todos';
            aplicarFiltros();
        });
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && modal && !modal.hidden) fecharModal();
        if (event.key === 'Enter' && event.ctrlKey && modal?.hidden) abrirModal();
    });

    form?.addEventListener('submit', event => {
        const limite = Number(document.getElementById('limiteFiado')?.value || 0);
        if (limite < 0) {
            event.preventDefault();
            alert('O limite de fiado não pode ser negativo.');
        }
    });

    window.editarCliente = function(id) {
        // Mantém o ponto de integração existente do projeto.
        // Se o backend já possui edição, ele pode substituir esta função global.
        if (typeof window.abrirEdicaoCliente === 'function') {
            window.abrirEdicaoCliente(id);
            return;
        }
        console.info('Editar cliente:', id);
    };


    window.quitarFiadoCliente = async function(id) {
        if (!confirm('Confirmar quitação de todo o fiado em aberto deste cliente?')) return;

        const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        try {
            const response = await fetch(`/clientes/fiado/${id}/quitar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.erro || 'Não foi possível quitar o fiado.');
            }
            alert(`Fiado quitado com sucesso!\nValor pago: R$ ${Number(data.valor_pago).toFixed(2)}\nNovo saldo: R$ ${Number(data.novo_saldo_fiado).toFixed(2)}`);
            window.location.reload();
        } catch (error) {
            alert(error.message);
        }
    };

    window.removerCliente = function(id) {
        // Mantém o ponto de integração existente do projeto.
        // O backend deve confirmar a exclusão antes de efetivá-la.
        if (typeof window.excluirCliente === 'function') {
            window.excluirCliente(id);
            return;
        }
        console.info('Remover cliente:', id);
    };

    aplicarFiltros();
});
