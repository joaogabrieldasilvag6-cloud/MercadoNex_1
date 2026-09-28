document.addEventListener('DOMContentLoaded', () => {
    const periodo = document.getElementById('periodo');
    const customo = document.getElementById('periodoCustomo');
    const btnImprimir = document.getElementById('btnImprimir');
    const form = document.getElementById('periodoForm');

    function atualizarPeriodo() {
        if (!periodo || !customo) return;
        customo.hidden = periodo.value !== 'custom';
    }

    periodo?.addEventListener('change', atualizarPeriodo);

    form?.addEventListener('submit', event => {
        if (periodo?.value === 'custom') {
            const inicio = document.getElementById('inicio')?.value;
            const fim = document.getElementById('fim')?.value;

            if (!inicio || !fim) {
                event.preventDefault();
                alert('Informe as datas inicial e final.');
                return;
            }

            if (inicio > fim) {
                event.preventDefault();
                alert('A data inicial não pode ser maior que a data final.');
            }
        }
    });

    btnImprimir?.addEventListener('click', () => window.print());

    atualizarPeriodo();
});
