// Set new default font family and font color to mimic Bootstrap's default styling
(Chart.defaults.global.defaultFontFamily = "Metropolis"),
    '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = "#858796";


// Função  para formatação de números

function number_format(number, decimals, dec_point, thousands_sep) {
    // *     example: number_format(1234.56, 2, ',', ' ');
    // *     return: '1 234,56'
    number = (number + "").replace(",", "").replace(" ", "");
    var n = !isFinite(+number) ? 0 : +number,
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = typeof thousands_sep === "undefined" ? "," : thousands_sep,
        dec = typeof dec_point === "undefined" ? "." : dec_point,
        s = "",
        toFixedFix = function (n, prec) {
            var k = Math.pow(10, prec);
            return "" + Math.round(n * k) / k;
        };
    // Fix for IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : "" + Math.round(n)).split(".");
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || "").length < prec) {
        s[1] = s[1] || "";
        s[1] += new Array(prec - s[1].length + 1).join("0");
    }
    return s.join(dec);
}

// GRÁFICOS
// Area Chart Horario


document.addEventListener("DOMContentLoaded", function () {
    $.ajax({
        url: '/api/dados/horario',
        type: 'GET',
        success: function (data) {
            renderTemperaturaHorarioChart(data);
            renderHumidadeHorarioChart(data);
            renderLuminosidadeHorarioChart(data);
        }
    });
});

function renderTemperaturaHorarioChart(data) {
    var ctxTemp = document.getElementById('temperaturaHorarioChart').getContext('2d');
    var temperaturaHorarioChart = new Chart(ctxTemp, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Temp. Máx.',
                    data: data.temperaturas_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(255, 99, 132, 0.05)', // red
                    borderColor: 'rgb(255, 99, 132, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                    pointBorderColor: 'rgba(255, 99, 132, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
                    pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Temp. Méd.',
                    data: data.temperaturas_medias,
                    fill: false,
                    backgroundColor: 'rgba(255, 206, 86, 1)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    lineTensiontension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Temp. Mín.',
                    data: data.temperaturas_minimas,
                    fill: false,
                    backgroundColor: 'rgba(54, 162, 235, 0.05)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' °C';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + ' °C';
                    }
                }
            }
        }
    });
}

function renderHumidadeHorarioChart(data) {
    var ctxHum = document.getElementById('humidadeHorarioChart').getContext('2d');
    var humidadeHorarioChart = new Chart(ctxHum, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Hum. Máx.',
                    data: data.humidades_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(0, 123, 255, 0.05)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(0, 123, 255, 1)',
                    pointBorderColor: 'rgba(0, 123, 255, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(0, 123, 255, 1)',
                    pointHoverBorderColor: 'rgba(0, 123, 255, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Hum. Méd.',
                    data: data.humidades_medias,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(75, 192, 192, 0.05)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Hum. Mín.',
                    data: data.humidades_minimas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(201, 203, 207, 0.05)',
                    borderColor: 'rgba(201, 203, 207, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(201, 203, 207, 1)',
                    pointBorderColor: 'rgba(201, 203, 207, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(201, 203, 207, 1)',
                    pointHoverBorderColor: 'rgba(201, 203, 207, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' %';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + '%';
                    }
                }
            }
        }
    });
}
function renderLuminosidadeHorarioChart(data) {
    var ctxLux = document.getElementById('luminosidadeHorarioChart').getContext('2d');
    var luminosidadeHorarioChart = new Chart(ctxLux, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Lux Máx.',
                    data: data.lux_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(255, 206, 86, 0.05)', // yellow
                    borderColor: 'rgba(255, 206, 86, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Méd.',
                    data: data.lux_medias,
                    fill: false,
                    backgroundColor: 'rgba(75, 192, 192, 0.05)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    lineTensiontension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Mín.',
                    data: data.lux_minimas,
                    fill: false,
                    backgroundColor: 'rgba(54, 162, 235, 0.05)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value + ' lx';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel + ' lx';
                    }
                }
            }
        }
    });
}





// Area Chart Diario

document.addEventListener("DOMContentLoaded", function () {
    $.ajax({
        url: '/api/dados/diario',
        type: 'GET',
        success: function (data) {
            renderTemperaturaDiarioChart(data);
            renderHumidadeDiarioChart(data);
            renderLuminosidadeDiarioChart(data); //
        }
    });
});


function renderTemperaturaDiarioChart(data) {
    var ctxTemp = document.getElementById('temperaturaDiarioChart').getContext('2d');
    var temperaturaChart = new Chart(ctxTemp, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Temp. Máx.',
                data: data.temperaturas_maximas,
                lineTension: 0.3,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.05)', // Vermelho
                pointRadius: 3,
                pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                pointBorderColor: 'rgba(255, 99, 132, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
                pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                fill: false
            }, {
                label: 'Temp. Méd.',
                data: data.temperaturas_medias,
                lineTension: 0.3,
                borderColor: 'rgba(255, 206, 86, 1)',
                backgroundColor: 'rgba(255, 206, 86, 0.05)', // Amarelo
                pointRadius: 3,
                pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                pointBorderColor: 'rgba(255, 206, 86, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                fill: false
            }, {
                label: 'Temp. Mín.',
                data: data.temperaturas_minimas,
                lineTension: 0.3,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.05)', // Azul
                pointRadius: 3,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: 'rgba(54, 162, 235, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' °C';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + ' °C';
                    }
                }
            }
        }
    });
}

function renderHumidadeDiarioChart(data) {
    var ctxHum = document.getElementById('humidadeDiarioChart').getContext('2d');
    var humidadeChart = new Chart(ctxHum, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Hum. Máx.',
                data: data.humidades_maximas,
                lineTension: 0.3,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.05)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: 'rgba(54, 162, 235, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                fill: false
            }, {
                label: 'Hum. Méd.',
                data: data.humidades_medias,
                lineTension: 0.3,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.05)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointBorderColor: 'rgba(75, 192, 192, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                fill: false
            }, {
                label: 'Hum. Mín.',
                data: data.humidades_minimas,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(201, 203, 207, 0.05)',
                borderColor: 'rgba(201, 203, 207, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(201, 203, 207, 1)',
                pointBorderColor: 'rgba(201, 203, 207, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(201, 203, 207, 1)',
                pointHoverBorderColor: 'rgba(201, 203, 207, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + '%';
                    }
                }
            }
        }
    });
}

function renderLuminosidadeDiarioChart(data) {
    var ctxLux = document.getElementById('luminosidadeDiarioChart').getContext('2d');
    var luminosidadeDiarioChart = new Chart(ctxLux, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Lux Máx.',
                    data: data.lux_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(255, 206, 86, 0.05)', // yellow
                    borderColor: 'rgba(255, 206, 86, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Méd.',
                    data: data.lux_medias,
                    fill: false,
                    backgroundColor: 'rgba(75, 192, 192, 0.05)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    lineTensiontension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Mín.',
                    data: data.lux_minimas,
                    fill: false,
                    backgroundColor: 'rgba(54, 162, 235, 0.05)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value + ' lx';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel + ' lx';
                    }
                }
            }
        }
    });
}


// Area Chart Semanal

document.addEventListener("DOMContentLoaded", function () {
    $.ajax({
        url: '/api/dados/semanal',
        type: 'GET',
        success: function (data) {
            renderTemperaturaSemanalChart(data);
            renderHumidadeSemanalChart(data);
            renderLuminosidadeSemanalChart(data);
        }
    });
});

function renderTemperaturaSemanalChart(data) {
    var ctxTemp = document.getElementById('temperaturaSemanalChart').getContext('2d');
    var temperaturaSemanalChart = new Chart(ctxTemp, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Temp. Máx.',
                    data: data.temperaturas_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(255, 99, 132, 0.05)', // Vermelho claro
                    borderColor: 'rgba(255, 99, 132, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                    pointBorderColor: 'rgba(255, 99, 132, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
                    pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Temp. Méd. ',
                    data: data.temperaturas_medias,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(255, 206, 86, 0.05)', // Amarelo
                    borderColor: 'rgba(255, 206, 86, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointBorderColor: 'rgba(255, 206, 86, 0.05)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Temp. Mín.',
                    data: data.temperaturas_minimas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(54, 162, 235, 0.05)', // Azul
                    borderColor: 'rgba(54, 162, 235, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' °C';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + ' °C';
                    }
                }
            }
        }
    });
}

function renderHumidadeSemanalChart(data) {
    var ctxHum = document.getElementById('humidadeSemanalChart').getContext('2d');
    var humidadeSemanalChart = new Chart(ctxHum, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Hum. Máx.',
                    data: data.humidades_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(0, 123, 255, 0.05)', // Azul claro
                    borderColor: 'rgba(0, 123, 255, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(0, 123, 255, 1)',
                    pointBorderColor: 'rgba(0, 123, 255, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(0, 123, 255, 1)',
                    pointHoverBorderColor: 'rgba(0, 123, 255, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Hum. Méd.',
                    data: data.humidades_medias,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(75, 192, 192, 0.05)', // Verde água claro
                    borderColor: 'rgba(75, 192, 192, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Hum. Mín.',
                    data: data.humidades_minimas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(201, 203, 207, 0.05)', // Cinza claro
                    borderColor: 'rgba(201, 203, 207, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(201, 203, 207, 1)',
                    pointBorderColor: '#fff',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(201, 203, 207, 1)',
                    pointHoverBorderColor: 'rgba(201, 203, 207, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' %';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + ' %';
                    }
                }
            }
        }
    });
}
function renderLuminosidadeSemanalChart(data) {
    var ctxLux = document.getElementById('luminosidadeSemanalChart').getContext('2d');
    var luminosidadeSemanalChart = new Chart(ctxLux, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Lux Máx.',
                    data: data.lux_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(255, 206, 86, 0.05)', // yellow
                    borderColor: 'rgba(255, 206, 86, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Méd.',
                    data: data.lux_medias,
                    fill: false,
                    backgroundColor: 'rgba(75, 192, 192, 0.05)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Mín.',
                    data: data.lux_minimas,
                    fill: false,
                    backgroundColor: 'rgba(54, 162, 235, 0.05)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value + ' lx';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel + ' lx';
                    }
                }
            }
        }
    });
}

// Area Chart Mensal

document.addEventListener("DOMContentLoaded", function () {
    $.ajax({
        url: '/api/dados/mensal',
        type: 'GET',
        success: function (data) {
            renderTemperaturaMensalChart(data);
            renderHumidadeMensalChart(data);
            renderLuminosidadeMensalChart(data);
        }
    });
});

function renderTemperaturaMensalChart(data) {
    var ctxTemp = document.getElementById('temperaturaMensalChart').getContext('2d');
    var temperaturaMensalChart = new Chart(ctxTemp, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Temp. Máx.',
                data: data.temperaturas_maximas,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(255, 99, 132, 0.05)', // Vermelho claro
                borderColor: 'rgba(255, 99, 132, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                pointBorderColor: 'rgba(255, 99, 132, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
                pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }, {
                label: 'Temp. Méd.',
                data: data.temperaturas_medias,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(255, 206, 86, 0.05)', // Amarelo claro
                borderColor: 'rgba(255, 206, 86, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                pointBorderColor: 'rgba(255, 206, 86, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }, {
                label: 'Temp. Mín.',
                data: data.temperaturas_minimas,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(54, 162, 235, 0.05)', // Azul claro
                borderColor: 'rgba(54, 162, 235, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: 'rgba(54, 162, 235, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' °C';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + ' °C';
                    }
                }
            }
        }
    });
}

function renderHumidadeMensalChart(data) {
    var ctxHum = document.getElementById('humidadeMensalChart').getContext('2d');
    var humidadeMensalChart = new Chart(ctxHum, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Hum. Máx.',
                data: data.humidades_maximas,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(0, 123, 255, 0.05)', // Azul claro
                borderColor: 'rgba(0, 123, 255, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(0, 123, 255, 1)',
                pointBorderColor: 'rgba(0, 123, 255, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(0, 123, 255, 1)',
                pointHoverBorderColor: 'rgba(0, 123, 255, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }, {
                label: 'Hum. Méd.',
                data: data.humidades_medias,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(75, 192, 192, 0.05)', // Cyan
                borderColor: 'rgba(75, 192, 192, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointBorderColor: 'rgba(75, 192, 192, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }, {
                label: 'Hum. Mín.',
                data: data.humidades_minimas,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(201, 203, 207, 0.05)', // Cinza claro
                borderColor: 'rgba(201, 203, 207, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(201, 203, 207, 1)',
                pointBorderColor: '#fff',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(201, 203, 207, 1)',
                pointHoverBorderColor: 'rgba(201, 203, 207, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)', // Cor clara para as linhas de grade
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' %';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + ' %';
                    }
                }
            }
        }
    });
}

function renderLuminosidadeMensalChart(data) {
    var ctxLux = document.getElementById('luminosidadeMensalChart').getContext('2d');
    var luminosidadeMensalChart = new Chart(ctxLux, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Lux Máx.',
                    data: data.lux_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(255, 206, 86, 0.05)', // yellow
                    borderColor: 'rgba(255, 206, 86, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Méd.',
                    data: data.lux_medias,
                    fill: false,
                    backgroundColor: 'rgba(75, 192, 192, 0.05)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Mín.',
                    data: data.lux_minimas,
                    fill: false,
                    backgroundColor: 'rgba(54, 162, 235, 0.05)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value + ' lx';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel + ' lx';
                    }
                }
            }
        }
    });
}


// Area Chart Anual


document.addEventListener("DOMContentLoaded", function () {
    $.ajax({
        url: '/api/dados/anual',
        type: 'GET',
        success: function (data) {
            renderTemperaturaAnualChart(data);
            renderHumidadeAnualChart(data);
            renderLuminosidadeAnualChart(data);

        }
    });
});

function renderTemperaturaAnualChart(data) {
    var ctxTemp = document.getElementById('temperaturaAnualChart').getContext('2d');
    var temperaturaAnualChart = new Chart(ctxTemp, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Temp. Máx.',
                data: data.temperaturas_maximas,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(255, 99, 132, 0.05)', // red
                borderColor: 'rgba(255, 99, 132, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                pointBorderColor: 'rgba(255, 99, 132, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
                pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }, {
                label: 'Temp. Méd.',
                data: data.temperaturas_medias,
                fill: false,
                backgroundColor: 'rgba(255, 206, 86, 0.05)', // Amarelo
                borderColor: 'rgba(255, 206, 86, 1)',
                lineTension: 0.3,
                pointRadius: 3,
                pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                pointBorderColor: 'rgba(255, 206, 86, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }, {
                label: 'Temp. Mín.',
                data: data.temperaturas_minimas,
                fill: false,
                backgroundColor: 'rgba(54, 162, 235, 0.05)', // Blue
                borderColor: 'rgba(54, 162, 235, 1)',
                lineTension: 0.3,
                pointRadius: 3,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: 'rgba(54, 162, 235, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' °C';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + ' °C';
                    }
                }
            }
        }
    });
}
function renderLuminosidadeAnualChart(data) {
    var ctxLux = document.getElementById('luminosidadeAnualChart').getContext('2d');
    var luminosidadeAnualChart = new Chart(ctxLux, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Lux Máx.',
                    data: data.lux_maximas,
                    lineTension: 0.3,
                    fill: false,
                    backgroundColor: 'rgba(255, 206, 86, 0.05)', // yellow
                    borderColor: 'rgba(255, 206, 86, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(255, 206, 86, 1)',
                    pointHoverBorderColor: 'rgba(255, 206, 86, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Méd.',
                    data: data.lux_medias,
                    fill: false,
                    backgroundColor: 'rgba(75, 192, 192, 0.05)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                },
                {
                    label: 'Lux Mín.',
                    data: data.lux_minimas,
                    fill: false,
                    backgroundColor: 'rgba(54, 162, 235, 0.05)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    lineTension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 12
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value + ' lx';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel + ' lx';
                    }
                }
            }
        }
    });
}
function renderHumidadeAnualChart(data) {
    var ctxHum = document.getElementById('humidadeAnualChart').getContext('2d');
    var humidadeAnualChart = new Chart(ctxHum, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Hum. Máx.',
                data: data.humidades_maximas,
                lineTension: 0.3,
                fill: false,
                backgroundColor: 'rgba(0, 123, 255, 0.05)',
                borderColor: 'rgba(0, 123, 255, 1)',
                pointRadius: 3,
                pointBackgroundColor: 'rgba(0, 123, 255, 1)',
                pointBorderColor: 'rgba(0, 123, 255, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(0, 123, 255, 1)',
                pointHoverBorderColor: 'rgba(0, 123, 255, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }, {
                label: 'Hum. Méd.',
                data: data.humidades_medias,
                fill: false,
                backgroundColor: 'rgba(75, 192, 192, 0.05)',
                borderColor: 'rgba(75, 192, 192, 1)',
                lineTension: 0.3,
                pointRadius: 3,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointBorderColor: 'rgba(75, 192, 192, 1)',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }, {
                label: 'Hum. Mín.',
                data: data.humidades_minimas,
                fill: false,
                backgroundColor: 'rgba(201, 203, 207, 0.05)',
                borderColor: 'rgba(201, 203, 207, 1)',
                lineTension: 0.3,
                pointRadius: 3,
                pointBackgroundColor: 'rgba(201, 203, 207, 1)',
                pointBorderColor: '#fff',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: 'rgba(201, 203, 207, 1)',
                pointHoverBorderColor: 'rgba(201, 203, 207, 1)',
                pointHitRadius: 10,
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    gridLines: {
                        color: 'rgb(234, 236, 244)',
                        zeroLineColor: 'rgb(234, 236, 244)',
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    },
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        callback: function (value) {
                            return value.toFixed(1) + ' °C';
                        }
                    }
                }]
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: "#6e707e",
                titleFontSize: 14,
                borderColor: "#dddfeb",
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: "index",
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + tooltipItem.yLabel.toFixed(1) + ' °C';
                    }
                }
            }
        }
    });
}


