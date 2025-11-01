# 🚀 Guia Completo: Executar Detector de Smishing Localmente

Este guia fornece instruções passo a passo para executar o projeto **Detector de Smishing** em seu computador local, exatamente como funcionaria em produção.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

### Windows, macOS e Linux

1. **Python 3.8 ou superior**
   - Download: https://www.python.org/downloads/
   - Verifique: `python --version`

2. **Git** (opcional, mas recomendado)
   - Download: https://git-scm.com/

3. **Um editor de código** (opcional)
   - VS Code: https://code.visualstudio.com/
   - PyCharm Community: https://www.jetbrains.com/pycharm/

---

## 📂 Passo 1: Extrair o Projeto

1. Faça download do arquivo `detector-smishing-tcc-completo.zip`
2. Extraia o arquivo em um local de sua preferência
3. Abra uma janela do terminal/prompt de comando
4. Navegue até a pasta do projeto:

```bash
cd caminho/para/detector-smishing-tcc
```

---

## 🔧 Passo 2: Configurar o Backend

### 2.1 Criar Ambiente Virtual Python

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você deve ver `(venv)` no início da linha do terminal, indicando que o ambiente está ativo.

### 2.2 Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

Isso pode levar alguns minutos. Aguarde até que termine.

### 2.3 Verificar Modelos ML

Certifique-se de que os seguintes arquivos estão na pasta `backend/`:

- ✅ `tfidf_vectorizer.pkl`
- ✅ `random_forest.pkl`
- ✅ `complement_naive_bayes.pkl`
- ✅ `data_processed.csv`

Se algum arquivo estiver faltando, copie-o para a pasta `backend/`.

### 2.4 Executar o Backend

```bash
python main.py
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Deixe este terminal aberto!** O backend precisa estar rodando enquanto você testa.

---

## 🌐 Passo 3: Configurar o Frontend

### 3.1 Abrir Novo Terminal

Abra uma **nova janela** do terminal (mantenha o backend rodando na outra).

### 3.2 Navegar para o Frontend

```bash
cd caminho/para/detector-smishing-tcc/client/public
```

### 3.3 Iniciar Servidor Local

**Opção A: Com Python (Recomendado)**

```bash
python -m http.server 3000
```

**Opção B: Com Node.js (se tiver instalado)**

```bash
npx http-server -p 3000
```

**Saída esperada:**
```
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
```

---

## ✅ Passo 4: Acessar o Projeto

Abra seu navegador e acesse:

### Frontend (Página Principal)
```
http://localhost:3000
```

Você deve ver a página do Dashboard com:
- ✅ Título "Detector de Smishing"
- ✅ Gráficos e nuvem de palavras
- ✅ Navegação para outras páginas
- ✅ Botão "Ir para o Detector"

### Páginas Disponíveis

- **Dashboard:** http://localhost:3000/index.html
- **Detector:** http://localhost:3000/detector.html
- **Sobre Nós:** http://localhost:3000/sobre.html
- **Contato:** http://localhost:3000/contato.html

### API Backend (Documentação Interativa)

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🧪 Passo 5: Testar as Funcionalidades

### 5.1 Testar Análise de SMS

1. Acesse http://localhost:3000/detector.html
2. Copie e cole uma mensagem de teste:
   ```
   Clique aqui para confirmar sua conta: http://bit.ly/123abc
   ```
3. Clique em "Analisar Mensagem"
4. Você deve ver o resultado com:
   - ✅ Veredito (Smishing ou Legítima)
   - ✅ Barra de confiança
   - ✅ Lista de características detectadas
   - ✅ Botões de feedback (Sim/Não)

### 5.2 Testar Feedback

1. Após uma análise, clique em "Sim" ou "Não" para registrar feedback
2. Você deve ver a mensagem "Obrigado pelo seu feedback!"

### 5.3 Testar Formulário de Contato

1. Acesse http://localhost:3000/contato.html
2. Preencha o formulário com dados de teste
3. Clique em "Enviar Mensagem"
4. Você deve ver uma mensagem de sucesso (ou erro se o Formspree não estiver configurado)

---

## 🔍 Troubleshooting

### Erro: "Port 8000 already in use"

**Solução:**
```bash
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

Encontre o processo e finalize-o, ou use uma porta diferente:
```bash
python main.py --port 8001
```

### Erro: "ModuleNotFoundError: No module named 'fastapi'"

**Solução:**
```bash
pip install -r requirements.txt
```

Certifique-se de que o ambiente virtual está ativado.

### Frontend não conecta com Backend

**Solução:**
1. Verifique se o backend está rodando em http://localhost:8000
2. Abra o console do navegador (F12)
3. Procure por erros CORS
4. Verifique se a URL da API está correta em `js/main.js`

### Modelos ML não carregam

**Solução:**
1. Verifique se os arquivos `.pkl` estão na pasta `backend/`
2. Verifique se os nomes dos arquivos estão corretos
3. Tente reexecutar o backend

### Página em branco

**Solução:**
1. Limpe o cache do navegador (Ctrl+Shift+Delete)
2. Recarregue a página (Ctrl+F5)
3. Verifique se o servidor está rodando
4. Abra o console (F12) e procure por erros

---

## 📊 Estrutura de Pastas

```
detector-smishing-tcc/
├── backend/
│   ├── main.py                    # ← Execute este arquivo
│   ├── requirements.txt
│   ├── tfidf_vectorizer.pkl
│   ├── random_forest.pkl
│   ├── complement_naive_bayes.pkl
│   └── data_processed.csv
│
├── client/
│   └── public/                    # ← Abra este diretório no navegador
│       ├── index.html
│       ├── detector.html
│       ├── sobre.html
│       ├── contato.html
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── main.js
│           ├── charts.js
│           ├── detector.js
│           └── contato.js
│
├── docs/
│   ├── GUIA_DEPLOY_BACKEND.md
│   ├── GUIA_DEPLOY_FRONTEND.md
│   └── GUIA_DESENVOLVIMENTO.md
│
└── README.md
```

---

## 🔧 Modificar Configurações

### Mudar Porta do Backend

No arquivo `backend/main.py`, procure por:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

Mude `8000` para a porta desejada.

### Mudar Porta do Frontend

Ao executar o servidor:
```bash
python -m http.server 3001  # Muda para porta 3001
```

### Atualizar URL da API no Frontend

No arquivo `client/public/js/main.js`, procure por:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

Mude para a URL desejada.

---

## 📝 Fazer Mudanças no Código

### Backend

1. Edite o arquivo em `backend/main.py`
2. Salve o arquivo
3. O servidor deve recarregar automaticamente
4. Recarregue a página no navegador

### Frontend

1. Edite os arquivos em `client/public/`
2. Salve o arquivo
3. Recarregue a página no navegador (Ctrl+F5)

---

## 🚀 Próximos Passos

Depois de testar localmente:

1. **Personalize o projeto:**
   - Adicione informações da sua equipe em `sobre.html`
   - Configure o Formspree em `contato.html`
   - Ajuste as cores conforme necessário

2. **Faça testes completos:**
   - Teste todas as páginas
   - Teste a análise com diferentes mensagens
   - Teste o feedback

3. **Prepare para deploy:**
   - Siga o `GUIA_DEPLOY_BACKEND.md` para o PythonAnywhere
   - Siga o `GUIA_DEPLOY_FRONTEND.md` para o Netlify

---

## 💡 Dicas Importantes

1. **Mantenha ambos os terminais abertos:** Backend em um, frontend em outro
2. **Recarregue com Ctrl+F5:** Garante que o cache não interfira
3. **Verifique o console:** Pressione F12 para ver erros
4. **Teste com diferentes mensagens:** Use exemplos de smishing reais
5. **Backup:** Faça backup de suas mudanças regularmente

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs no terminal
2. Abra o console do navegador (F12)
3. Procure por mensagens de erro
4. Verifique se as portas estão corretas
5. Tente reiniciar os servidores

---

## ✅ Checklist de Execução

- [ ] Python 3.8+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Modelos ML presentes na pasta `backend/`
- [ ] Backend rodando em http://localhost:8000
- [ ] Frontend rodando em http://localhost:3000
- [ ] Dashboard carrega corretamente
- [ ] Detector funciona com análise de SMS
- [ ] Feedback registra corretamente
- [ ] Formulário de contato funciona

---

**Desenvolvido com ❤️ para o TCC da UNIVESP**

*Última atualização: Outubro de 2025*
