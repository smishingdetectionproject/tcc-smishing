# 🚀 Guia de Deploy do Frontend no Netlify

Este guia fornece instruções passo a passo para fazer deploy do frontend do Detector de Smishing no Netlify, uma plataforma de hospedagem gratuita com CI/CD automático e HTTPS incluído.

---

## 📋 Pré-requisitos

- Conta no GitHub (com o repositório do projeto)
- Conta no Netlify (gratuita em https://www.netlify.com)
- Acesso ao seu repositório no GitHub

---

## 🔧 Passo 1: Preparar o Frontend

### 1.1 Estrutura de Arquivos

Certifique-se de que o frontend está estruturado assim:

```
client/public/
├── index.html
├── detector.html
├── sobre.html
├── contato.html
├── css/
│   └── style.css
└── js/
    ├── main.js
    ├── charts.js
    ├── detector.js
    └── contato.js
```

### 1.2 Configurar URL da API

No arquivo `client/public/js/main.js`, verifique a URL da API:

```javascript
// URL da API Backend (ajustar conforme necessário)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://seu-username.pythonanywhere.com';
```

**Substitua `seu-username` pela URL real do seu backend no PythonAnywhere.**

### 1.3 Atualizar Formspree (Página de Contato)

No arquivo `client/public/contato.html`, procure pelo formulário e atualize o `action`:

```html
<form id="formularioContato" method="POST" action="https://formspree.io/f/YOUR_FORM_ID">
```

**Substitua `YOUR_FORM_ID` pelo seu ID do Formspree:**

1. Acesse [https://formspree.io](https://formspree.io)
2. Crie uma conta
3. Crie um novo projeto
4. Copie o ID do formulário
5. Substitua no arquivo HTML

---

## 📤 Passo 2: Fazer Push para o GitHub

1. No seu computador, abra o terminal na pasta do projeto
2. Execute os comandos abaixo:

```bash
# Adicionar todos os arquivos
git add .

# Fazer commit
git commit -m "Deploy frontend no Netlify"

# Fazer push para o GitHub
git push origin main
```

---

## 🌐 Passo 3: Criar Conta no Netlify

1. Acesse [https://www.netlify.com](https://www.netlify.com)
2. Clique em **"Sign up"** (Inscrever-se)
3. Escolha **"Sign up with GitHub"**
4. Autorize o Netlify a acessar sua conta do GitHub
5. Complete o registro

---

## 🔗 Passo 4: Conectar Repositório GitHub

1. No painel do Netlify, clique em **"Add new site"**
2. Clique em **"Import an existing project"**
3. Selecione **"GitHub"**
4. Autorize o Netlify a acessar seus repositórios
5. Selecione o repositório **"detector-smishing-tcc"**

---

## ⚙️ Passo 5: Configurar Build

1. Na próxima página, você verá as configurações de build
2. Preencha os campos:

   | Campo | Valor |
   |-------|-------|
   | **Branch to deploy** | `main` |
   | **Build command** | (deixe vazio) |
   | **Publish directory** | `client/public` |

3. Clique em **"Deploy site"**

---

## ⏳ Passo 6: Aguardar Deploy

1. O Netlify começará a fazer o deploy automaticamente
2. Você verá uma barra de progresso
3. Quando terminar, você receberá uma URL como:
   ```
   https://seu-site-aleatorio.netlify.app
   ```

---

## ✅ Passo 7: Testar o Frontend

1. Clique na URL fornecida pelo Netlify
2. Verifique se o site carrega corretamente
3. Teste as funcionalidades:
   - Navegação entre páginas
   - Análise de mensagens (se o backend estiver configurado)
   - Formulário de contato
   - Responsividade (redimensione a janela)

---

## 🎯 Passo 8: Configurar Domínio Personalizado (Opcional)

Se você tiver um domínio próprio:

1. No painel do Netlify, clique em **"Domain settings"**
2. Clique em **"Add custom domain"**
3. Digite seu domínio (ex: `detector-smishing.com`)
4. Siga as instruções para configurar os registros DNS
5. O Netlify fornecerá certificado HTTPS automaticamente

---

## 🔄 Passo 9: Configurar Deploys Automáticos

O Netlify já está configurado para fazer deploy automático quando você fizer push para o GitHub.

Quando você fizer mudanças:

1. Faça as alterações no seu computador
2. Execute:
   ```bash
   git add .
   git commit -m "Descrição das mudanças"
   git push origin main
   ```
3. O Netlify detectará as mudanças automaticamente
4. Um novo deploy será iniciado em alguns segundos
5. Você pode acompanhar o progresso no painel do Netlify

---

## 🔗 Conectar Frontend e Backend

### Atualizar URL da API

1. No painel do Netlify, clique em **"Site settings"**
2. Clique em **"Build & deploy"**
3. Clique em **"Environment"**
4. Clique em **"Edit variables"**
5. Adicione uma variável:
   - **Key:** `REACT_APP_API_URL`
   - **Value:** `https://seu-username.pythonanywhere.com`
6. Clique em **"Save"**
7. Faça um novo deploy:
   - Clique em **"Deploys"**
   - Clique em **"Trigger deploy"**
   - Selecione **"Deploy site"**

---

## 🔐 Configurações de Segurança

### 1. Ativar HTTPS

O Netlify ativa HTTPS automaticamente com certificado Let's Encrypt.

### 2. Configurar Headers de Segurança

1. Crie um arquivo `_headers` na pasta `client/public/`:

```
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
```

2. Faça commit e push:
   ```bash
   git add client/public/_headers
   git commit -m "Adiciona headers de segurança"
   git push origin main
   ```

### 3. Configurar Redirects

Se necessário, crie um arquivo `_redirects` na pasta `client/public/`:

```
/* /index.html 200
```

---

## 📊 Monitorar o Site

### Ver Logs de Deploy

1. No painel do Netlify, clique em **"Deploys"**
2. Clique no deploy mais recente
3. Verifique os logs

### Ver Estatísticas

1. No painel do Netlify, clique em **"Analytics"**
2. Veja as estatísticas de tráfego

---

## 🛠️ Troubleshooting

### Página em branco

**Solução:**
1. Abra o console do navegador (F12)
2. Verifique se há erros
3. Verifique se a URL da API está correta
4. Verifique se o backend está online

### Erro ao conectar com a API

**Solução:**
1. Verifique se o backend está online
2. Verifique se a URL da API está correta
3. Verifique se o CORS está configurado corretamente no backend
4. Abra o console do navegador e procure por erros CORS

### Formulário não envia

**Solução:**
1. Verifique se o Formspree ID está correto
2. Teste o formulário localmente
3. Verifique os logs do Formspree

### Estilos não carregam

**Solução:**
1. Verifique se os arquivos CSS estão no diretório correto
2. Verifique os caminhos dos arquivos
3. Limpe o cache do navegador (Ctrl+Shift+Delete)

---

## 💡 Dicas Importantes

1. **Deploy Automático:** Sempre que você fizer push para o GitHub, um novo deploy será iniciado
2. **Rollback:** Você pode reverter para um deploy anterior no painel do Netlify
3. **Preview:** Netlify cria previews automáticos para pull requests
4. **Variáveis de Ambiente:** Use variáveis de ambiente para configurações sensíveis
5. **Performance:** O Netlify oferece CDN global para melhor performance

---

## 🎉 Pronto!

Seu frontend está agora em produção!

**URL do Frontend:** `https://seu-site-aleatorio.netlify.app`

---

## 📋 Checklist Final

- [ ] Frontend está em produção no Netlify
- [ ] Backend está em produção no PythonAnywhere
- [ ] URL da API está configurada no frontend
- [ ] Formspree está configurado para o formulário de contato
- [ ] HTTPS está ativado
- [ ] Domínio personalizado configurado (opcional)
- [ ] Testes funcionais realizados
- [ ] Analytics configurado (opcional)

---

## 🔗 Próximos Passos

1. Compartilhe o link do seu site com amigos e família
2. Colete feedback dos usuários
3. Monitore o desempenho
4. Faça melhorias contínuas
5. Considere adicionar mais recursos

---

## 📞 Suporte

Se encontrar problemas:

1. Consulte a [documentação do Netlify](https://docs.netlify.com/)
2. Verifique os logs de deploy
3. Teste o site localmente
4. Abra uma issue no GitHub

---

**Desenvolvido com ❤️ para o TCC da UNIVESP**
