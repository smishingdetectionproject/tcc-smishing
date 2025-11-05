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

let ultimaAnalise = null;
let feedbackRegistrado = false;

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do formulário
    const formularioAnalise = document.getElementById('formularioAnalise');
    const mensagemInput = document.getElementById('mensagemInput');
    const botaoNovaAnalise = document.getElementById('botaoNovaAnalise');
    
    // Elementos de feedback
    const feedbackSim = document.getElementById('feedbackSim');
    const feedbackNao = document.getElementById('feedbackNao');
    const enviarFeedbackBtn = document.getElementById('enviarFeedbackBtn');
    const pularFeedbackBtn = document.getElementById('pularFeedbackBtn');
    
    // Event listeners
    if (formularioAnalise) {
        formularioAnalise.addEventListener('submit', analisarMensagem);
    }
    
    if (botaoNovaAnalise) {
        botaoNovaAnalise.addEventListener('click', novaAnalise);
    }
    
    if (mensagemInput) {
        mensagemInput.addEventListener('input', atualizarContador);
    }
    
    // Event listeners para mostrar o formulário de comentário
    if (feedbackSim) {
        feedbackSim.addEventListener('click', function() {
            prepararFeedback(true);
        });
    }
    
    if (feedbackNao) {
        feedbackNao.addEventListener('click', function() {
            prepararFeedback(false);
        });
    }
    
    // Event listener para o botão de envio final
    if (enviarFeedbackBtn) {
        enviarFeedbackBtn.addEventListener('click', enviarFeedback);
    }
    
    // Event listener para o botão de pular
    if (pularFeedbackBtn) {
        pularFeedbackBtn.addEventListener('click', function() {
            enviarFeedback(true); // Passa true para indicar que é para pular o comentário
        });
    }
    
    // Inicializar contador
    // A função atualizarContador() é chamada no evento 'input'
});

// ============================================================================
// FUNÇÕES PRINCIPAIS
// ============================================================================

/**
 * Atualiza o contador de caracteres
 */
function atualizarContador() {
    const mensagemInput = document.getElementById('mensagemInput');
    const contadorCaracteres = document.getElementById('contadorCaracteres');
    
    if (mensagemInput && contadorCaracteres) {
        contadorCaracteres.textContent = mensagemInput.value.length;
    }
}

/**
 * Analisa a mensagem
 */
async function analisarMensagem(evento) {
    evento.preventDefault();
    
    const mensagemInput = document.getElementById('mensagemInput');
    const modeloSelect = document.getElementById('modeloSelect');
    const botaoAnalisar = document.getElementById('botaoAnalisar');
    const carregando = document.getElementById('carregando');
    const resultadoContainer = document.getElementById('resultadoContainer');
    
    // Validar entrada
    if (!mensagemInput.value.trim()) {
        mostrarNotificacao('Por favor, insira uma mensagem', 'warning');
        return;
    }
    
    // Desabilitar botão e mostrar carregamento
    botaoAnalisar.disabled = true;
    carregando.style.display = 'block';
    resultadoContainer.style.display = 'none';
    feedbackRegistrado = false;
    
    try {
        // Fazer requisição para a API (usando função global de main.js)
        const resposta = await fazerRequisicaoAPI('/analisar', 'POST', {
            mensagem: mensagemInput.value.trim(),
            modelo: modeloSelect.value
        });
        
        // Armazenar resultado
        ultimaAnalise = resposta;
        
        // Exibir resultado
        exibirResultado(resposta);
        resultadoContainer.style.display = 'block';
        
        // Scroll para resultado
        resultadoContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (erro) {
        console.error('Erro ao analisar:', erro);
        // Usando função global de main.js
        mostrarNotificacao(`Erro ao analisar a mensagem. Detalhe: ${erro.message}`, 'danger');
    } finally {
        // Reabilitar botão e esconder carregamento
        botaoAnalisar.disabled = false;
        carregando.style.display = 'none';
    }
}

/**
 * Exibe o resultado da análise
 */
function exibirResultado(resultado) {
    const resultadoCard = document.getElementById('resultadoCard');
    const veredito = document.getElementById('veredito');
    const barraConfianca = document.getElementById('barraConfianca');
    const textoConfianca = document.getElementById('textoConfianca');
    const explicacao = document.getElementById('explicacao');
    const caracteristicasContainer = document.getElementById('caracteristicasContainer');
    const explicacaoContainer = document.getElementById('explicacaoContainer');
    
    // Determinar classe CSS baseado no veredito
    const isSmishing = resultado.veredito.includes('Smishing');
    const classe = isSmishing ? 'smishing' : 'legitima';
    
    // Atualizar classe do card
    resultadoCard.className = `card border-0 shadow-lg mb-5 resultado-card ${classe}`;
    
    // Atualizar veredito
    const icone = isSmishing ? '⚠️' : '✅';
    veredito.innerHTML = `<span class="resultado-icone">${icone}</span> ${resultado.veredito}`;
    veredito.className = `resultado-veredito ${classe} mb-3`;
    
    // Atualizar barra de confiança
    const confiancaPercentual = Math.round(resultado.confianca * 100);
    barraConfianca.style.width = confiancaPercentual + '%';
    barraConfianca.className = `progress-bar ${isSmishing ? 'bg-danger' : 'bg-success'}`;
    textoConfianca.textContent = confiancaPercentual + '%';
    
    // Atualizar explicação
    // Corrigir a renderização de Markdown (substituir **texto** por <strong>texto</strong>)
    let explicacaoHtml = resultado.explicacao.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    explicacao.innerHTML = explicacaoHtml;
    explicacaoContainer.className = `alert ${isSmishing ? 'alert-danger' : 'alert-success'} mb-4`;
    
    // Atualizar características
    caracteristicasContainer.innerHTML = '';
    
    if (resultado.caracteristicas && resultado.caracteristicas.length > 0) {
        resultado.caracteristicas.forEach(caracteristica => {
            const elemento = document.createElement('div');
            elemento.className = 'caracteristica-item';
            elemento.innerHTML = `
                <div class="caracteristica-icone">${sanitizarTexto(caracteristica.icone)}</div>
                <div class="caracteristica-conteudo">
                    <h6>${sanitizarTexto(caracteristica.nome)}</h6>
                    <p>${sanitizarTexto(caracteristica.descricao)}</p>
                    <small class="text-muted">
                        Confiança: ${Math.round(caracteristica.confianca * 100)}%
                    </small>
                </div>
            `;
            caracteristicasContainer.appendChild(elemento);
        });
    } else {
        caracteristicasContainer.innerHTML = `
            <p class="text-muted">Nenhuma característica suspeita detectada.</p>
        `;
    }
    
    // Resetar feedback
    resetarFeedback();
}

/**
 * Prepara a interface para o envio de feedback
 */
function prepararFeedback(util) {
    if (!ultimaAnalise || feedbackRegistrado) {
        return;
    }
    
    const feedbackButtonsContainer = document.getElementById('feedbackButtonsContainer');
    const feedbackFormContainer = document.getElementById('feedbackFormContainer');
    const feedbackMensagemConscientizacao = document.getElementById('feedbackMensagemConscientizacao');
    const feedbackUtilInput = document.getElementById('feedbackUtilInput');
    const comentarioFeedback = document.getElementById('comentarioFeedback');
    
    // 1. Esconder botões de Sim/Não
    feedbackButtonsContainer.style.display = 'none';
    
    // 2. Limpar campo de comentário e armazenar o valor de util
    comentarioFeedback.value = '';
    feedbackUtilInput.value = util;
    
    // 3. Atualizar mensagem de conscientização
    if (util) {
        feedbackMensagemConscientizacao.innerHTML = '<strong>Análise Útil!</strong> Seu feedback positivo reforça o aprendizado do modelo. Se desejar, adicione um comentário para nos ajudar a entender o que funcionou bem.';
    } else {
        feedbackMensagemConscientizacao.innerHTML = '<strong>Análise Não Útil!</strong> Seu feedback negativo é crucial. Por favor, adicione um comentário explicando por que a análise não foi útil. Isso nos ajuda a identificar e corrigir os erros do modelo.';
    }
    
    // 4. Mostrar o formulário de comentário
    feedbackFormContainer.style.display = 'block';
    
    // 5. Scroll para o formulário
    feedbackFormContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Envia o feedback final para a API
 * @param {boolean} pular - Indica se o usuário clicou em "Pular e Finalizar"
 */
async function enviarFeedback(pular = false) {
    if (!ultimaAnalise || feedbackRegistrado) {
        return;
    }
    
    const enviarFeedbackBtn = document.getElementById('enviarFeedbackBtn');
    const pularFeedbackBtn = document.getElementById('pularFeedbackBtn');
    const comentarioFeedback = document.getElementById('comentarioFeedback');
    const feedbackUtilInput = document.getElementById('feedbackUtilInput');
    const feedbackFormContainer = document.getElementById('feedbackFormContainer');
    
    const util = feedbackUtilInput.value === 'true';
    
    // Desabilitar botões para evitar duplo envio
    enviarFeedbackBtn.disabled = true;
    pularFeedbackBtn.disabled = true;
    
    try {
        // Fazer requisição para registrar feedback (usando função global de main.js)
        await fazerRequisicaoAPI('/feedback', 'POST', {
            mensagem: document.getElementById('mensagemInput').value.trim(),
            veredito_original: ultimaAnalise.veredito,
            feedback_util: util,
            comentario_usuario: comentarioFeedback.value.trim() // pode ser vazio
        });
        
        // Atualizar estado
        feedbackRegistrado = true;
        
        // Esconder formulário de feedback
        feedbackFormContainer.style.display = 'none';
        
        // Mostrar notificação de sucesso
        mostrarNotificacao('Obrigado! Seu feedback foi registrado com sucesso.', 'success');
        
    } catch (erro) {
        console.error('Erro ao enviar feedback:', erro);
        mostrarNotificacao(`Erro ao enviar feedback. Detalhe: ${erro.message}`, 'danger');
    } finally {
        // Reabilitar botões (embora o feedbackRegistrado=true impeça novo envio)
        enviarFeedbackBtn.disabled = false;
        pularFeedbackBtn.disabled = false;
    }
}

/**
 * Reseta a interface de feedback para o estado inicial
 */
function resetarFeedback() {
    const feedbackButtonsContainer = document.getElementById('feedbackButtonsContainer');
    const feedbackFormContainer = document.getElementById('feedbackFormContainer');
    
    if (feedbackButtonsContainer) {
        feedbackButtonsContainer.style.display = 'flex'; // Assume que o display padrão é flex
    }
    
    if (feedbackFormContainer) {
        feedbackFormContainer.style.display = 'none';
    }
    
    feedbackRegistrado = false;
}

/**
 * Inicia uma nova análise, limpando o formulário e o resultado
 */
function novaAnalise() {
    const formularioAnalise = document.getElementById('formularioAnalise');
    const resultadoContainer = document.getElementById('resultadoContainer');
    const mensagemInput = document.getElementById('mensagemInput');
    
    if (formularioAnalise) {
        formularioAnalise.reset();
    }
    
    if (resultadoContainer) {
        resultadoContainer.style.display = 'none';
    }
    
    if (mensagemInput) {
        mensagemInput.focus();
        atualizarContador();
    }
    
    ultimaAnalise = null;
    feedbackRegistrado = false;
    
    // Scroll para o topo da seção de análise
    const cardAnalise = document.querySelector('.card.shadow-lg');
    if (cardAnalise) {
        cardAnalise.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}