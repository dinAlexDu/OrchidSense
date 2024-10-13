window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }
});
window.addEventListener('DOMContentLoaded', event => {
    const tabelaIds = ['idTabelaResumoHorario', 'idTabelaResumoDiario', 'idTabelaResumoSemanal', 'idTabelaResumoMensal', 'idTabelaResumoAnual'];

    tabelaIds.forEach(id => {
        const tabelaElement = document.getElementById(id);
        if (tabelaElement) {
            new simpleDatatables.DataTable(tabelaElement);
        }
    });
});
