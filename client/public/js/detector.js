/**
 * DETECTOR DE SMISHING - LÓGICA DA PÁGINA DETECTOR
 * 
 * Este arquivo contém a lógica para análise de mensagens SMS
 * 
 * **NOTA:** As funções globais `fazerRequisicaoAPI`, `mostrarNotificacao` e `sanitizarTexto`
 * são assumidas como definidas no `main.js` e são usadas diretamente aqui.
 */

// ============================================================================
// VARIÁVEIS GLOBAIS
// ============================================================================

let ultimaMensagem = "";
let ultimoVereditoOriginal = "";

// Função para formatar a explicação (substituindo **texto** por <strong>texto</strong>)
function formatarExplicacao(texto) {
    // Substitui **texto** por <strong>texto</strong>
    return texto.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

// Função para exibir o resultado da análise
function exibirResultado(data) {
    // Armazenar para o feedback
    ultimaMensagem = data.mensagem;
    ultimoVereditoOriginal = data.veredito;

    // Elementos de resultado
    const resultadoDiv = document.getElementById('resultado-analise');
    const vereditoTitulo = document.getElementById('veredito-titulo');
    const barraConfianca = document.getElementById('barra-confianca');
    const explicacaoTexto = document.getElementById('explicacao-texto');
    const caracteristicasLista = document.getElementById('caracteristicas-lista');
    const feedbackSection = document.getElementById('feedback-section');

    // 1. Veredito e Confiança
    const isSmishing = data.veredito.includes("Smishing");
    const cor = isSmishing ? 'danger' : 'success';
    const confiancaPercentual = (data.confianca * 100).toFixed(2);

    vereditoTitulo.innerHTML = `<span class="text-${cor}">${data.veredito}</span>`;
    barraConfianca.innerHTML = `
        <div class="progress-bar bg-${cor}" role="progressbar" style="width: ${confiancaPercentual}%;" aria-valuenow="${confiancaPercentual}" aria-valuemin="0" aria-valuemax="100">
            ${confiancaPercentual}%
        </div>
    `;

    // 2. Explicação (com correção de Markdown)
    explicacaoTexto.innerHTML = `
        <div class="alert alert-${isSmishing ? 'danger' : 'success'} mt-3" role="alert">
            <i class="bi bi-info-circle-fill"></i> ${formatarExplicacao(data.explicacao)}
        </div>
    `;

    // 3. Características Detectadas
    caracteristicasLista.innerHTML = '';
    if (data.caracteristicas.length > 0) {
        data.caracteristicas.forEach(caracteristica => {
            const item = document.createElement('div');
            item.className = 'card mb-3 shadow-sm';
            item.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title"><i class="bi bi-lightbulb-fill me-2"></i> ${caracteristica.nome}</h5>
                    <p class="card-text">${caracteristica.descricao}</p>
                    <small class="text-muted">Confiança: ${(caracteristica.confianca * 100).toFixed(0)}%</small>
                </div>
            `;
            caracteristicasLista.appendChild(item);
        });
    } else {
        caracteristicasLista.innerHTML = '<p class="text-muted">Nenhuma característica suspeita detectada.</p>';
    }

    // 4. Exibir a seção de resultado e feedback
    resultadoDiv.classList.remove('d-none');
    feedbackSection.classList.remove('d-none');
    document.getElementById('feedback-form').classList.add('d-none'); // Esconder o formulário de feedback inicialmente
}

// Função para analisar a mensagem
async function analisarMensagem() {
    const mensagem = document.getElementById('mensagem-sms').value;
    const modelo = document.getElementById('modelo-ia').value;
    const btnAnalise = document.getElementById('btn-analisar');
    const loadingSpinner = document.getElementById('loading-spinner');

    if (mensagem.length < 10) {
        alert("Por favor, insira uma mensagem com pelo menos 10 caracteres.");
        return;
    }

    // Desabilitar botão e mostrar loading
    btnAnalise.disabled = true;
    btnAnalise.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analisando...';
    loadingSpinner.classList.remove('d-none');
    document.getElementById('resultado-analise').classList.add('d-none');
    document.getElementById('feedback-section').classList.add('d-none');
    document.getElementById('feedback-form').classList.add('d-none'); // Esconder o formulário de feedback

    try {
        const response = await fetch('https://seu-backend-render.onrender.com/analisar', { // ATUALIZE ESTA URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mensagem: mensagem, modelo: modelo })
        });

        const data = await response.json();

        if (response.ok) {
            exibirResultado(data);
        } else {
            alert(`Erro na análise: ${data.detail}`);
        }

    } catch (error) {
        console.error('Erro ao conectar com a API:', error);
        alert('Erro ao conectar com o servidor de análise. Verifique a URL da API.');
    } finally {
        // Reabilitar botão e esconder loading
        btnAnalise.disabled = false;
        btnAnalise.innerHTML = 'Analisar Mensagem';
        loadingSpinner.classList.add('d-none');
    }
}

// Função para exibir o formulário de feedback
function exibirFormularioFeedback(util) {
    const feedbackForm = document.getElementById('feedback-form');
    const feedbackUtilInput = document.getElementById('feedback-util-input');
    const feedbackMessage = document.getElementById('feedback-message');
    
    // Esconder botões Sim/Não
    document.getElementById('feedback-buttons').classList.add('d-none');

    // Preencher o campo hidden com o valor booleano
    feedbackUtilInput.value = util;

    // Ajustar a mensagem de conscientização
    if (util === 'true') {
        feedbackMessage.innerHTML = 'Obrigado! Seu feedback positivo reforça o aprendizado do modelo. Se desejar, adicione um comentário para nos ajudar a entender o que funcionou bem.';
    } else {
        feedbackMessage.innerHTML = 'Seu feedback negativo é crucial! Por favor, adicione um comentário explicando por que a análise não foi útil. Isso nos ajuda a identificar e corrigir os erros do modelo.';
    }

    // Exibir o formulário
    feedbackForm.classList.remove('d-none');
}

// Função para enviar o feedback
async function enviarFeedback() {
    const feedbackUtil = document.getElementById('feedback-util-input').value;
    const comentario = document.getElementById('comentario-feedback').value;
    const btnEnviar = document.getElementById('btn-enviar-feedback');

    // Desabilitar botão
    btnEnviar.disabled = true;
    btnEnviar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';

    try {
        const response = await fetch('https://seu-backend-render.onrender.com/feedback', { // ATUALIZE ESTA URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mensagem: ultimaMensagem,
                veredito_original: ultimoVereditoOriginal,
                feedback_util: feedbackUtil === 'true', // Converte a string de volta para booleano
                comentario_usuario: comentario
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Feedback enviado com sucesso! Obrigado por sua contribuição.");
            // Esconder a seção de feedback após o envio
            document.getElementById('feedback-section').classList.add('d-none');
        } else {
            alert(`Erro ao enviar feedback: ${data.detail}`);
        }

    } catch (error) {
        console.error('Erro ao enviar feedback:', error);
        alert('Erro ao conectar com o servidor de feedback. Verifique a URL da API.');
    } finally {
        // Reabilitar botão
        btnEnviar.disabled = false;
        btnEnviar.innerHTML = 'Enviar Feedback';
    }
}

// Adicionar listeners aos botões de feedback
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-sim-util').addEventListener('click', () => exibirFormularioFeedback('true'));
    document.getElementById('btn-nao-util').addEventListener('click', () => exibirFormularioFeedback('false'));
    document.getElementById('btn-enviar-feedback').addEventListener('click', enviarFeedback);
});