/**
 * DETECTOR DE SMISHING - SCRIPT PRINCIPAL
 * 
 * Este arquivo contém funções globais e inicializações
 */

// ============================================================================
// CONFIGURAÇÃO GLOBAL
// ============================================================================

// URL da API Backend (detecta automaticamente ambiente)
// Em produção, defina a variável VITE_API_URL ou use a URL padrão
const API_BASE_URL = (
    window.location.hostname === 'localhost' || 
    window.location.hostname === '127.0.0.1'
) 
    ? 'http://localhost:8000'  // Desenvolvimento local
    : (import.meta?.env?.VITE_API_URL || 'https://detector-smishing-backend.onrender.com' );  // Produção


// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/**
 * Faz uma requisição para a API
 */
async function fazerRequisicaoAPI(endpoint, metodo = 'GET', dados = null ) {
    try {
        const opcoes = {
            method: metodo,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        if (dados) {
            opcoes.body = JSON.stringify(dados);
        }
        
        const resposta = await fetch(`${API_BASE_URL}${endpoint}`, opcoes);
        
        if (!resposta.ok) {
            throw new Error(`Erro na requisição: ${resposta.status}`);
        }
        
        return await resposta.json();
    } catch (erro) {
        console.error('Erro ao fazer requisição:', erro);
        throw erro;
    }
}

/**
 * Mostra uma notificação toast
 */
function mostrarNotificacao(mensagem, tipo = 'info') {
    // Usar Bootstrap Toast se disponível
    const container = document.getElementById('toast-container');
    
    if (!container) {
        // Criar container se não existir
        const novoContainer = document.createElement('div');
        novoContainer.id = 'toast-container';
        novoContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(novoContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${tipo} alert-dismissible fade show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    
    // Remover após 5 segundos
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Sanitiza texto para evitar XSS
 */
function sanitizarTexto(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
}

/**
 * Valida um email
 */
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Valida um telefone (formato brasileiro)
 */
function validarTelefone(telefone) {
    const regex = /^\(?[1-9]{2}\)?[\s]?9?[\s]?[6-9][0-9]{3}-?[0-9]{4}$/;
    return regex.test(telefone.replace(/\D/g, ''));
}

// ============================================================================
// INICIALIZAÇÃO GLOBAL
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Adicionar classe 'active' ao link de navegação atual
    const paginaAtual = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        if (link.getAttribute('href') === paginaAtual) {
            link.classList.add('active');
        }
    });
});

// ============================================================================
// ACESSIBILIDADE
// ============================================================================

/**
 * Suporte para navegação por teclado
 */
document.addEventListener('keydown', function(evento) {
    // ESC para fechar modais
    if (evento.key === 'Escape') {
        const modaisAbertos = document.querySelectorAll('.modal.show');
        modaisAbertos.forEach(modal => {
            bootstrap.Modal.getInstance(modal)?.hide();
        });
    }
    
    // Enter em botões com role="button"
    if (evento.key === 'Enter') {
        const elemento = document.activeElement;
        if (elemento.getAttribute('role') === 'button') {
            elemento.click();
        }
    }
});

// ============================================================================
// TRATAMENTO DE ERROS GLOBAL
// ============================================================================

window.addEventListener('error', function(evento) {
    console.error('Erro não capturado:', evento.error);
    mostrarNotificacao('Ocorreu um erro. Por favor, tente novamente.', 'danger');
});

window.addEventListener('unhandledrejection', function(evento) {
    console.error('Promise rejeitada:', evento.reason);
    mostrarNotificacao('Ocorreu um erro. Por favor, tente novamente.', 'danger');
});

// ============================================================================
// VERIFICAÇÃO DE CONECTIVIDADE
// ============================================================================

/**
 * Verifica se a API está disponível
 */
async function verificarConectividadeAPI() {
    try {
        const resposta = await fazerRequisicaoAPI('/health');
        console.log('✓ API disponível:', resposta);
        return true;
    } catch (erro) {
        console.warn('✗ API indisponível:', erro);
        return false;
    }
}

// Verificar conectividade ao carregar a página
document.addEventListener('DOMContentLoaded', async function() {
    const apiDisponivel = await verificarConectividadeAPI();
    
    if (!apiDisponivel) {
        console.warn('Aviso: A API backend não está disponível. Algumas funcionalidades podem não funcionar.');
    }
});

// ============================================================================
// MODO DESENVOLVIMENTO
// ============================================================================

// Expor funções globais para testes no console
window.API = {
    fazerRequisicaoAPI,
    mostrarNotificacao,
    sanitizarTexto,
    validarEmail,
    validarTelefone,
    verificarConectividadeAPI
};

console.log('%cDetector de Smishing', 'font-size: 20px; font-weight: bold; color: #003366;');
console.log('%cAPI disponível em: ' + API_BASE_URL, 'color: #666;');
console.log('%cUse window.API para acessar funções globais', 'color: #999; font-style: italic;');
