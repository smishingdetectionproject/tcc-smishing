/**
 * DETECTOR DE SMISHING - LÓGICA DA PÁGINA CONTATO
 * 
 * Este arquivo contém a lógica para o formulário de contato
 */

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const formularioContato = document.getElementById('formularioContato');
    const mensagem = document.getElementById('mensagem');
    const contadorMensagem = document.getElementById('contadorMensagem');
    const email = document.getElementById('email');
    const nome = document.getElementById('nome');
    const telefone = document.getElementById('telefone');
    
    // Event listeners
    if (formularioContato) {
        formularioContato.addEventListener('submit', enviarFormulario);
    }
    
    if (mensagem) {
        mensagem.addEventListener('input', atualizarContadorMensagem);
        mensagem.setAttribute('maxlength', '1000');
    }
    
    if (email) {
        email.addEventListener('blur', validarEmail);
    }
    
    if (telefone) {
        telefone.addEventListener('input', formatarTelefone);
    }
});

// ============================================================================
// FUNÇÕES PRINCIPAIS
// ============================================================================

/**
 * Atualiza o contador de caracteres da mensagem
 */
function atualizarContadorMensagem() {
    const mensagem = document.getElementById('mensagem');
    const contadorMensagem = document.getElementById('contadorMensagem');
    
    if (mensagem && contadorMensagem) {
        contadorMensagem.textContent = mensagem.value.length;
    }
}

/**
 * Valida o email
 */
function validarEmail() {
    const email = document.getElementById('email');
    
    if (!email.value) return;
    
    if (!validarEmailRegex(email.value)) {
        email.classList.add('is-invalid');
        mostrarNotificacao('Email inválido', 'warning');
    } else {
        email.classList.remove('is-invalid');
    }
}

/**
 * Formata o telefone
 */
function formatarTelefone() {
    const telefone = document.getElementById('telefone');
    
    if (!telefone.value) return;
    
    // Remover caracteres não numéricos
    let valor = telefone.value.replace(/\D/g, '');
    
    // Limitar a 11 dígitos
    valor = valor.substring(0, 11);
    
    // Formatar como (XX) XXXXX-XXXX
    if (valor.length > 0) {
        if (valor.length <= 2) {
            valor = `(${valor}`;
        } else if (valor.length <= 7) {
            valor = `(${valor.substring(0, 2)}) ${valor.substring(2)}`;
        } else {
            valor = `(${valor.substring(0, 2)}) ${valor.substring(2, 7)}-${valor.substring(7)}`;
        }
    }
    
    telefone.value = valor;
}

/**
 * Envia o formulário
 */
async function enviarFormulario(evento) {
    evento.preventDefault();
    
    const formularioContato = document.getElementById('formularioContato');
    const botaoEnviar = document.getElementById('botaoEnviar');
    const carregandoFormulario = document.getElementById('carregandoFormulario');
    
    // Validar campos obrigatórios
    if (!validarFormulario()) {
        mostrarNotificacao('Por favor, preencha todos os campos obrigatórios', 'warning');
        return;
    }
    
    // Desabilitar botão e mostrar carregamento
    botaoEnviar.disabled = true;
    carregandoFormulario.style.display = 'block';
    
    try {
        // Submeter formulário
        // O Formspree será acionado automaticamente pelo action do formulário
        // Aguardar um pouco para permitir o envio
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mostrar mensagem de sucesso
        mostrarNotificacao('Mensagem enviada com sucesso! Obrigado pelo contato.', 'success');
        
        // Limpar formulário
        formularioContato.reset();
        atualizarContadorMensagem();
        
        // Scroll para o topo
        formularioContato.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (erro) {
        console.error('Erro ao enviar formulário:', erro);
        mostrarNotificacao('Erro ao enviar mensagem. Tente novamente.', 'danger');
    } finally {
        // Reabilitar botão e esconder carregamento
        botaoEnviar.disabled = false;
        carregandoFormulario.style.display = 'none';
    }
}

// ============================================================================
// FUNÇÕES AUXILIARES DE VALIDAÇÃO
// ============================================================================

/**
 * Valida o formulário completo
 */
function validarFormulario() {
    const nome = document.getElementById('nome').value.trim();
    const email = document.getElementById('email').value.trim();
    const assunto = document.getElementById('assunto').value;
    const mensagem = document.getElementById('mensagem').value.trim();
    const consentimento = document.getElementById('consentimento').checked;
    
    // Validar campos obrigatórios
    if (!nome || nome.length < 3) {
        mostrarNotificacao('Nome deve ter pelo menos 3 caracteres', 'warning');
        return false;
    }
    
    if (!email || !validarEmailRegex(email)) {
        mostrarNotificacao('Email inválido', 'warning');
        return false;
    }
    
    if (!assunto) {
        mostrarNotificacao('Selecione um assunto', 'warning');
        return false;
    }
    
    if (!mensagem || mensagem.length < 10) {
        mostrarNotificacao('Mensagem deve ter pelo menos 10 caracteres', 'warning');
        return false;
    }
    
    if (!consentimento) {
        mostrarNotificacao('Você deve concordar com a política de privacidade', 'warning');
        return false;
    }
    
    return true;
}

/**
 * Valida um email usando regex
 */
function validarEmailRegex(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// ============================================================================
// INTEGRAÇÃO COM FORMSPREE
// ============================================================================

/**
 * Nota: O Formspree é integrado através do atributo 'action' do formulário.
 * Para usar o Formspree:
 * 
 * 1. Acesse https://formspree.io
 * 2. Crie uma conta e um novo projeto
 * 3. Copie o ID do formulário (exemplo: f/YOUR_FORM_ID)
 * 4. Substitua 'YOUR_FORM_ID' no atributo 'action' do formulário em contato.html
 * 
 * Exemplo:
 * action="https://formspree.io/f/xyzabc123"
 */

console.log('%cFormulário de Contato Carregado', 'font-size: 14px; font-weight: bold; color: #003366;');
console.log('%cNota: Configure o Formspree ID no atributo action do formulário', 'color: #999; font-style: italic;');
