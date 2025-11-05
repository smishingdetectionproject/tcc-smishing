/**
 * DETECTOR DE SMISHING - GRÁFICOS E VISUALIZAÇÕES
 * 
 * Este arquivo contém a lógica para criar gráficos interativos
 * usando Chart.js e WordCloud.js
 */

// ============================================================================
// DADOS DOS MODELOS
// ============================================================================

// INSTRUÇÕES: Substitua os valores abaixo pelos dados reais do seu modelo.
// Se os arrays matrizConfusaoData e aucData estiverem vazios, o site exibirá "Em Breve...".

const modelosData = {
    models: ['Random Forest', 'Complement Naive Bayes'],
    acuracia: [97.86, 94.54],
    precisao: [95.45, 80.29],
    recall: [94.59, 99.10],
    f1Score: [95.02, 88.71]
};

// Matriz de Confusão: [ [VN, FP], [FN, VP] ]
// Exemplo: const matrizConfusaoData = [ [2000, 9], [3, 549] ];
const matrizConfusaoData = []; // DEIXE VAZIO PARA EXIBIR "EM BREVE..."

// Curva AUC: { auc: valor, fpr: [array de fpr], tpr: [array de tpr] }
// Exemplo: const aucData = { auc: 0.99, fpr: [0.0, 0.1, 0.2, 1.0], tpr: [0.0, 0.9, 0.95, 1.0] };
const aucData = {}; // DEIXE VAZIO PARA EXIBIR "EM BREVE..."

// ============================================================================
// FUNÇÕES DE EXIBIÇÃO DE MÉTRICAS AVANÇADAS
// ============================================================================

function exibirMatrizConfusao() {
    const container = document.getElementById('confusionMatrixContainer');
    if (!container) return;

    // Se os dados não estiverem disponíveis (array vazio), exibe o placeholder
    if (!matrizConfusaoData || matrizConfusaoData.length === 0) {
        container.innerHTML = '<p class="text-muted">Em breve...</p>';
        return;
    }

    // Cria a tabela da Matriz de Confusão
    const tabela = `
        <table class="table table-bordered text-center" style="max-width: 300px; margin: 20px auto;">
            <thead>
                <tr>
                    <th></th>
                    <th colspan="2">Predito</th>
                </tr>
                <tr>
                    <th></th>
                    <th>Legítima (0)</th>
                    <th>Smishing (1)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th rowspan="2">Real</th>
                    <td>${matrizConfusaoData[0][0]} (VN)</td>
                    <td class="text-danger">${matrizConfusaoData[0][1]} (FP)</td>
                </tr>
                <tr>
                    <td>${matrizConfusaoData[1][0]} (FN)</td>
                    <td class="text-success">${matrizConfusaoData[1][1]} (VP)</td>
                </tr>
            </tbody>
        </table>
        <p class="text-muted small">VN: Verdadeiro Negativo, FP: Falso Positivo, FN: Falso Negativo, VP: Verdadeiro Positivo</p>
    `;
    container.innerHTML = tabela;
}

function criarGraficoCurvaAUC() {
    const container = document.getElementById('aucCurveContainer');
    if (!container) return;

    // Se os dados não estiverem disponíveis (objeto vazio ou sem fpr), exibe o placeholder
    if (!aucData || !aucData.fpr || aucData.fpr.length === 0) {
        container.innerHTML = '<p class="text-muted">Em breve...</p>';
        return;
    }

    // Cria o canvas para o gráfico
    container.innerHTML = '<canvas id="aucChart"></canvas>';
    const ctx = document.getElementById('aucChart');

    // Cria o gráfico da Curva ROC
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: aucData.fpr.map(f => f.toFixed(2)), // Usar FPR como labels (eixo X)
            datasets: [
                {
                    label: `Curva ROC (AUC: ${aucData.auc.toFixed(2)})`,
                    data: aucData.tpr.map((tpr, index) => ({ x: aucData.fpr[index], y: tpr })),
                    borderColor: '#E74C3C',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.1
                },
                {
                    label: 'Linha de Base (AUC: 0.5)',
                    data: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
                    borderColor: '#95A5A6',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: `Curva ROC (AUC: ${aucData.auc.toFixed(2)})`
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Taxa de Falso Positivo (FPR)'
                    },
                    min: 0,
                    max: 1
                },
                y: {
                    title: {
                        display: true,
                        text: 'Taxa de Verdadeiro Positivo (TPR)'
                    },
                    min: 0,
                    max: 1
                }
            }
        }
    });
}

// ============================================================================
// GRÁFICO DE COMPARAÇÃO DE MÉTRICAS
// ============================================================================

const distribuicaoData = {
    labels: ['Mensagens Legítimas', 'Mensagens de Smishing'],
    data: [2009, 552],
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
    // Limpar o container antes de criar a nova nuvem
    container.innerHTML = '';
    
    WordCloud(container, {
        list: palavras,
        gridSize: 18,
        weightFactor: 1,
        fontFamily: "'Poppins', sans-serif",
        color: function() {
            return cores[Math.floor(Math.random() * cores.length)];
        },
        backgroundColor: '#f8f9fa',
        click: function(item) {
            console.log('Palavra clicada:', item[0]);
        },
        // Adicionar responsividade
        minSize: 0, // Permitir tamanhos muito pequenos
        shuffle: true, // Melhor distribuição em telas pequenas
        rotateRatio: 0.5, // Rotação para melhor preenchimento
        drawOutOfBound: false // Não desenhar fora do limite
    });
}

// ============================================================================
// INICIALIZAÇÃO (MANTIDO)
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Criar gráficos quando a página carregar
    criarGraficoMetricas();
    criarGraficoDistribuicao();
    criarNuvemPalavras();
    exibirMatrizConfusao(); // Novo
    criarGraficoCurvaAUC(); // Novo
    
    // Recriar gráficos ao redimensionar a janela (responsividade)
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // Recriar a nuvem de palavras para ajustar ao novo tamanho
            criarNuvemPalavras();
            // Recriar a curva AUC para ajustar ao novo tamanho
            criarGraficoCurvaAUC(); 
        }, 250);
    });
});

// ============================================================================
// FUNÇÕES AUXILIARES (MANTIDO)
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