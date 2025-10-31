/**
 * DETECTOR DE SMISHING - GRÁFICOS E VISUALIZAÇÕES
 * 
 * Este arquivo contém a lógica para criar gráficos interativos
 * usando Chart.js e WordCloud.js
 */

// ============================================================================
// DADOS DOS MODELOS
// ============================================================================

const modelosData = {
    models: ['Random Forest', 'Complement Naive Bayes'],
    acuracia: [97.86, 94.54],
    precisao: [95.45, 80.29],
    recall: [94.59, 99.10],
    f1Score: [95.02, 88.71]
};

const distribuicaoData = {
    labels: ['Mensagens Legítimas', 'Mensagens de Smishing'],
    data: [1500, 1689],
    colors: ['#27AE60', '#E74C3C']
};

// Palavras mais frequentes em smishing (extraído do dataset)
const palavrasSmishing = [
    { text: 'transferir', weight: 95 },
    { text: 'confirmar', weight: 88 },
    { text: 'urgente', weight: 85 },
    { text: 'clique', weight: 82 },
    { text: 'link', weight: 80 },
    { text: 'dados', weight: 78 },
    { text: 'conta', weight: 75 },
    { text: 'senha', weight: 72 },
    { text: 'código', weight: 70 },
    { text: 'número', weight: 68 },
    { text: 'banco', weight: 65 },
    { text: 'cartão', weight: 63 },
    { text: 'valor', weight: 60 },
    { text: 'imediato', weight: 58 },
    { text: 'ação', weight: 55 },
    { text: 'enviar', weight: 52 },
    { text: 'receber', weight: 50 },
    { text: 'pagar', weight: 48 },
    { text: 'depósito', weight: 45 },
    { text: 'verificar', weight: 42 }
];

// ============================================================================
// GRÁFICO DE COMPARAÇÃO DE MÉTRICAS
// ============================================================================

function criarGraficoMetricas() {
    const ctx = document.getElementById('metricsChart');
    
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Acurácia', 'Precisão', 'Recall', 'F1-Score'],
            datasets: [
                {
                    label: 'Random Forest',
                    data: [
                        modelosData.acuracia[0],
                        modelosData.precisao[0],
                        modelosData.recall[0],
                        modelosData.f1Score[0]
                    ],
                    borderColor: '#003366',
                    backgroundColor: 'rgba(0, 51, 102, 0.1)',
                    borderWidth: 2,
                    pointRadius: 5,
                    pointBackgroundColor: '#003366',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                },
                {
                    label: 'Complement Naive Bayes',
                    data: [
                        modelosData.acuracia[1],
                        modelosData.precisao[1],
                        modelosData.recall[1],
                        modelosData.f1Score[1]
                    ],
                    borderColor: '#FFA500',
                    backgroundColor: 'rgba(255, 165, 0, 0.1)',
                    borderWidth: 2,
                    pointRadius: 5,
                    pointBackgroundColor: '#FFA500',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12,
                            weight: '500'
                        },
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        font: {
                            family: "'Inter', sans-serif",
                            size: 11
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// ============================================================================
// GRÁFICO DE DISTRIBUIÇÃO
// ============================================================================

function criarGraficoDistribuicao() {
    const ctx = document.getElementById('distributionChart');
    
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: distribuicaoData.labels,
            datasets: [{
                data: distribuicaoData.data,
                backgroundColor: distribuicaoData.colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12,
                            weight: '500'
                        },
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// ============================================================================
// NUVEM DE PALAVRAS
// ============================================================================

function criarNuvemPalavras() {
    const container = document.getElementById('wordcloud');
    
    if (!container) return;
    
    // Preparar dados para WordCloud
    const palavras = palavrasSmishing.map(p => [p.text, p.weight]);
    
    // Configurar cores
    const cores = [
        '#E74C3C', '#C0392B', '#E67E22', '#D35400',
        '#F39C12', '#F1C40F', '#E74C3C', '#C0392B'
    ];
    
    // Criar nuvem de palavras
    WordCloud(container, {
        list: palavras,
        gridSize: 18,
        weightFactor: 3,
        fontFamily: "'Poppins', sans-serif",
        color: function() {
            return cores[Math.floor(Math.random() * cores.length)];
        },
        backgroundColor: '#f8f9fa',
        click: function(item) {
            console.log('Palavra clicada:', item[0]);
        }
    });
}

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Criar gráficos quando a página carregar
    criarGraficoMetricas();
    criarGraficoDistribuicao();
    criarNuvemPalavras();
    
    // Recriar gráficos ao redimensionar a janela (responsividade)
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Recarregar página para recriar gráficos
            // Ou usar Chart.js resize() se necessário
        }, 250);
    });
});

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/**
 * Formata um número como percentual
 */
function formatarPercentual(valor) {
    return (valor).toFixed(2) + '%';
}

/**
 * Retorna cor baseada em valor
 */
function obterCorPorValor(valor) {
    if (valor >= 95) return '#27AE60'; // Verde
    if (valor >= 90) return '#F39C12'; // Laranja
    return '#E74C3C'; // Vermelho
}
