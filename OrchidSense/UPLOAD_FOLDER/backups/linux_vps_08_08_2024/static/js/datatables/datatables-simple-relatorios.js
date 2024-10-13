window.addEventListener('DOMContentLoaded', event => {
    const tabelaIds = ['idTabelaResumoHorario', 'idTabelaResumoDiario', 'idTabelaResumoSemanal', 'idTabelaResumoMensal', 'idTabelaResumoAnual'];

    tabelaIds.forEach(id => {
        const tabelaElement = document.getElementById(id);
        if (tabelaElement) {
            new simpleDatatables.DataTable(tabelaElement);
        }
    });
});

