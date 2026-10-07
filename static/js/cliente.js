document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modalCliente');
    const btnNovo = document.getElementById('btnNovoCliente');
    const btnFechar = document.getElementById('fecharModal');
    const btnCancelar = document.getElementById('cancelarModal');
    const busca = document.getElementById('buscarCliente');
    const tbody = document.getElementById('clientes-tbody');
    const resultCount = document.getElementById('resultCount');
    const form = document.getElementById('cliente-form');
    const tituloModal = document.getElementById('tituloModalCliente');
    const btnSalvar = form?.querySelector('.btn-salvar');

    let filtroAtual = 'todos';

    const rows = () => Array.from(document.querySelectorAll('.cliente-row'));

    function csrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    function abrirModal() {
        if (!modal || !form) return;
        form.reset();
        form.action = '/clientes/cadastrar/';
        if (tituloModal) tituloModal.innerHTML = '<i class="fa-solid fa-user-plus"></i> Novo Cliente';
        if (btnSalvar) btnSalvar.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Salvar Cliente';
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-aberto');
        setTimeout(() => document.getElementById('clienteNome')?.focus(), 80);
    }

    function fecharModal() {
        if (!modal || !form) return;
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-aberto');
        form.reset();
        form.action = '/clientes/cadastrar/';
    }

    function normalizar(texto) {
        return (texto || '').toString().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }

    function aplicarFiltros() {
        const termo = normalizar(busca?.value);
        let visiveis = 0;

        rows().forEach(row => {
            const status = row.dataset.status || '';
            const texto = normalizar(row.dataset.search || row.textContent);
            const passaStatus = filtroAtual === 'todos' || status === filtroAtual;
            const passaBusca = !termo || texto.includes(termo);
            const mostrar = passaStatus && passaBusca;
            row.classList.toggle('is-hidden', !mostrar);
            if (mostrar) visiveis++;
        });

        if (resultCount) resultCount.textContent = `${visiveis} ${visiveis === 1 ? 'resultado' : 'resultados'}`;

        document.getElementById('clientesSemFiltro')?.remove();
        if (tbody && visiveis === 0 && rows().length > 0) {
            const tr = document.createElement('tr');
            tr.id = 'clientesSemFiltro';
            tr.innerHTML = '<td colspan="6" class="sem-registros"><i class="fa-solid fa-magnifying-glass"></i><strong>Nenhum cliente encontrado.</strong><span>Tente outro nome, CPF, telefone ou filtro.</span></td>';
            tbody.appendChild(tr);
        }
    }

    async function carregarCliente(id) {
        const resposta = await fetch(`/clientes/json/${id}/`, {headers: {'X-Requested-With': 'XMLHttpRequest'}});
        if (!resposta.ok) throw new Error('Não foi possível carregar os dados do cliente.');
        return resposta.json();
    }

    async function salvarCliente() {
        if (!form) return;

        const limite = Number(document.getElementById('limiteFiado')?.value || 0);
        if (limite < 0) {
            alert('O limite de fiado não pode ser negativo.');
            return;
        }

        const dados = new FormData(form);
        const resposta = await fetch(form.action, {
            method: 'POST',
            body: dados,
            headers: {
                'X-CSRFToken': csrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await resposta.json();
        if (!resposta.ok || !data.success) throw new Error(data.erro || 'Não foi possível salvar o cliente.');
        return data;
    }

    window.editarCliente = async function(id) {
        try {
            const cliente = await carregarCliente(id);
            form.action = `/clientes/editar/${id}/`;
            tituloModal.innerHTML = '<i class="fa-solid fa-user-pen"></i> Editar Cliente';
            btnSalvar.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Atualizar Cliente';

            form.nome.value = cliente.nome || '';
            form.telefone.value = cliente.telefone || '';
            form.email.value = cliente.email || '';
            form.cpf.value = cliente.cpf || '';
            form.endereco.value = cliente.endereco || '';
            form.limite_fiado.value = cliente.limite_fiado ?? 0;
            form.ativo_fiado.checked = Boolean(cliente.ativo_fiado);

            modal.hidden = false;
            modal.setAttribute('aria-hidden', 'false');
            document.body.classList.add('modal-aberto');
            setTimeout(() => document.getElementById('clienteNome')?.focus(), 80);
        } catch (error) {
            console.error(error);
            alert(error.message || 'Erro ao carregar os dados do cliente.');
        }
    };

    window.removerCliente = async function(id) {
        if (!confirm('Deseja realmente excluir este cliente?')) return;

        try {
            const resposta = await fetch(`/clientes/excluir/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await resposta.json();
            if (!resposta.ok || !data.success) throw new Error(data.erro || 'Não foi possível excluir o cliente.');

            document.querySelector(`.cliente-row[data-id="${id}"]`)?.remove();
            aplicarFiltros();
            alert(data.mensagem || 'Cliente removido com sucesso!');
        } catch (error) {
            console.error(error);
            alert(error.message || 'Erro ao remover cliente.');
        }
    };

    window.alternarBloqueioCliente = async function(id, vaiBloquear) {
        const mensagem = vaiBloquear
            ? 'Deseja bloquear as compras no fiado deste cliente?'
            : 'Deseja desbloquear as compras no fiado deste cliente?';

        if (!confirm(mensagem)) return;

        try {
            const resposta = await fetch(`/clientes/bloquear/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await resposta.json();
            if (!resposta.ok || !data.success) throw new Error(data.erro || 'Não foi possível alterar o status.');

            alert(data.mensagem);
            window.location.reload();
        } catch (error) {
            console.error(error);
            alert(error.message || 'Erro ao alterar o status do cliente.');
        }
    };

    window.quitarFiadoCliente = async function(id) {
        if (!confirm('Confirmar quitação de todo o fiado em aberto deste cliente?')) return;

        try {
            const resposta = await fetch(`/clientes/fiado/${id}/quitar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await resposta.json();
            if (!resposta.ok || !data.success) throw new Error(data.erro || 'Não foi possível quitar o fiado.');

            alert(`Fiado quitado com sucesso!\nValor pago: R$ ${Number(data.valor_pago).toFixed(2)}\nNovo saldo: R$ ${Number(data.novo_saldo_fiado).toFixed(2)}`);
            window.location.reload();
        } catch (error) {
            console.error(error);
            alert(error.message || 'Erro ao quitar o fiado.');
        }
    };

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

    form?.addEventListener('submit', async event => {
        event.preventDefault();
        if (!btnSalvar) return;
        btnSalvar.disabled = true;
        const textoOriginal = btnSalvar.innerHTML;
        btnSalvar.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';

        try {
            await salvarCliente();
            fecharModal();
            alert('Cliente salvo com sucesso!');
            window.location.reload();
        } catch (error) {
            console.error(error);
            alert(error.message || 'Erro na comunicação com o servidor.');
        } finally {
            btnSalvar.disabled = false;
            btnSalvar.innerHTML = textoOriginal;
        }
    });

    aplicarFiltros();
});
