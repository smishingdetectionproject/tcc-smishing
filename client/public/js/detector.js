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
    
    if (feedbackSim) {
        feedbackSim.addEventListener('click', function() {
            registrarFeedback(true);
        });
    }
    
    if (feedbackNao) {
        feedbackNao.addEventListener('click', function() {
            registrarFeedback(false);
        });
    }
    
    // Inicializar contador
    atualizarContador();
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
    const isSmishing = resultado.veredito === 'Smishing';
    const classe = isSmishing ? 'smishing' : 'legitima';
    
    // Atualizar classe do card
    resultadoCard.className = `card border-0 shadow-lg mb-5 resultado-card ${classe}`;
    
    // Atualizar veredito
    const icone = isSmishing ? '⚠️' : '✅';
    veredito.textContent = `${icone} ${resultado.veredito}`;
    veredito.className = `resultado-veredito ${classe} mb-3`;
    
    // Atualizar barra de confiança
    const confiancaPercentual = Math.round(resultado.confianca * 100);
    barraConfianca.style.width = confiancaPercentual + '%';
    barraConfianca.className = `progress-bar ${isSmishing ? 'bg-danger' : 'bg-success'}`;
    textoConfianca.textContent = confiancaPercentual + '%';
    
    // Atualizar explicação
    explicacao.textContent = resultado.explicacao;
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
 * Registra o feedback do usuário
 */
async function registrarFeedback(util) {
    if (!ultimaAnalise || feedbackRegistrado) {
        return;
    }
    
    const feedbackSim = document.getElementById('feedbackSim');
    const feedbackNao = document.getElementById('feedbackNao');
    
    try {
        // Fazer requisição para registrar feedback (usando função global de main.js)
        await fazerRequisicaoAPI('/feedback', 'POST', {
            mensagem: document.getElementById('mensagemInput').value.trim(),
            veredito_original: ultimaAnalise.veredito,
            feedback_util: util,
            feedback_usuario: null
        });
        
        // Atualizar estado dos botões
        feedbackRegistrado = true;
        feedbackSim.classList.remove('active');
        feedbackNao.classList.remove('active');
        
        if (util) {
            feedbackSim.classList.add('active');
        } else {
            feedbackNao.classList.add('active');
        }
        
        // Usando função global de main.js
        mostrarNotificacao('Obrigado pelo seu feedback!', 'success');
        
    } catch (erro) {
        console.error('Erro ao registrar feedback:', erro);
        // Usando função global de main.js
        mostrarNotificacao(`Erro ao registrar feedback. Detalhe: ${erro.message}`, 'danger');
    }
}

/**
 * Reseta os botões de feedback
 */
function resetarFeedback() {
    const feedbackSim = document.getElementById('feedbackSim');
    const feedbackNao = document.getElementById('feedbackNao');
    
    if (feedbackSim) feedbackSim.classList.remove('active');
    if (feedbackNao) feedbackNao.classList.remove('active');
    
    feedbackRegistrado = false;
}

/**
 * Prepara para uma nova análise
 */
function novaAnalise() {
    const formularioAnalise = document.getElementById('formularioAnalise');
    const mensagemInput = document.getElementById('mensagemInput');
    const resultadoContainer = document.getElementById('resultadoContainer');
    
    // Limpar formulário
    if (formularioAnalise) {
        formularioAnalise.reset();
    }
    
    // Atualizar contador
    if (mensagemInput) {
        mensagemInput.focus();
        atualizarContador();
    }
    
    // Esconder resultado
    resultadoContainer.style.display = 'none';
    
    // Scroll para o formulário
    formularioAnalise.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================================
// EXEMPLOS DE TESTE
// ============================================================================

/**
 * Carrega um exemplo de mensagem de smishing
 */
function carregarExemploSmishing() {
    const exemplos = [
        'Clique aqui para confirmar sua conta: http://bit.ly/123abc',
        'URGENTE: Sua conta foi bloqueada. Confirme seus dados: http://banco.fake.com',
        'Transferência de R$ 1000 pendente. Clique para confirmar: http://link.suspeito.com',
        'Seu CPF foi comprometido. Envie seu número de cartão para verificação.',
        'Parabéns! Você ganhou um prêmio. Clique aqui para receber: http://premio.fake.com'
    ];
    
    const exemplo = exemplos[Math.floor(Math.random() * exemplos.length)];
    const mensagemInput = document.getElementById('mensagemInput');
    
    if (mensagemInput) {
        mensagemInput.value = exemplo;
        atualizarContador();
    }
}

/**
 * Carrega um exemplo de mensagem legítima
 */
function carregarExemploLegitima() {
    const exemplos = [
        'Seu pedido foi confirmado. Acompanhe em: www.loja.com.br/pedidos',
        'Bem-vindo! Seu código de ativação é 123456',
        'Sua compra foi aprovada. Obrigado por comprar conosco!',
        'Lembrete: Sua consulta é amanhã às 14h. Confirme presença.',
        'Seu extrato está disponível. Acesse seu banco normalmente.'
    ];
    
    const exemplo = exemplos[Math.floor(Math.random() * exemplos.length)];
    const mensagemInput = document.getElementById('mensagemInput');
    
    if (mensagemInput) {
        mensagemInput.value = exemplo;
        atualizarContador();
    }
}

// Expor funções para uso externo
window.Detector = {
    carregarExemploSmishing,
    carregarExemploLegitima
};

console.log('%cDetector de Smishing Carregado', 'font-size: 14px; font-weight: bold; color: #003366;');
console.log('%cNota: As funções de comunicação são fornecidas pelo main.js.', 'color: #999; font-style: italic;');