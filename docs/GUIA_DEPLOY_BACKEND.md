# 🚀 Guia de Deploy do Backend no PythonAnywhere

Este guia fornece instruções passo a passo para fazer deploy da API FastAPI do Detector de Smishing no PythonAnywhere, uma plataforma de hospedagem Python gratuita que **não entra em modo de suspensão** e **não exige cartão de crédito**.

---

## 📋 Pré-requisitos

- Conta no GitHub (para clonar o repositório)
- Conta no PythonAnywhere (gratuita em https://www.pythonanywhere.com)
- Acesso ao terminal/prompt de comando

---

## 🔧 Passo 1: Criar Conta no PythonAnywhere

1. Acesse [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Clique em **"Sign up"** (Inscrever-se)
3. Escolha o plano **"Beginner"** (gratuito)
4. Preencha o formulário com seus dados
5. Confirme seu email
6. Faça login na sua conta

---

## 📂 Passo 2: Clonar o Repositório

1. No painel do PythonAnywhere, clique em **"Consoles"** no menu superior
2. Clique em **"Bash"** para abrir um terminal
3. Execute os comandos abaixo:

```bash
# Navegar para o diretório home
cd ~

# Clonar o repositório (substitua pela URL do seu repositório)
git clone https://github.com/seu-usuario/detector-smishing-tcc.git

# Navegar para o diretório do backend
cd detector-smishing-tcc/backend

# Listar os arquivos para confirmar
ls -la
```

---

## 🐍 Passo 3: Criar Ambiente Virtual

No mesmo terminal Bash:

```bash
# Criar ambiente virtual
mkvirtualenv --python=/usr/bin/python3.11 detector-api

# O ambiente será ativado automaticamente
# Você verá (detector-api) no início da linha

# Instalar dependências
pip install -r requirements.txt
```

**Nota:** Se receber erro sobre Python 3.11, use a versão disponível:
```bash
mkvirtualenv --python=/usr/bin/python3.10 detector-api
```

---

## 🌐 Passo 4: Configurar Web App

1. No painel do PythonAnywhere, clique em **"Web"** no menu superior
2. Clique em **"Add a new web app"**
3. Selecione **"Manual configuration"**
4. Escolha **"Python 3.10"** (ou a versão que você usou)
5. Clique em **"Next"**

---

## ⚙️ Passo 5: Configurar WSGI

1. Você será redirecionado para a página de configuração do Web App
2. Procure pela seção **"Code"** e clique em **"WSGI configuration file"**
3. Será aberto um editor de texto com um arquivo WSGI
4. **Apague todo o conteúdo** e substitua pelo código abaixo:

```python
# ============================================================================
# WSGI Configuration para Detector de Smishing
# ============================================================================

import sys
import os

# Adicionar o diretório do projeto ao path
project_home = '/home/{seu_username}/detector-smishing-tcc/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Ativar o ambiente virtual
activate_this = '/home/{seu_username}/.virtualenvs/detector-api/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), {'__file__': activate_this})

# Importar a aplicação FastAPI
from main import app

# Criar aplicação WSGI
application = app
```

**IMPORTANTE:** Substitua `{seu_username}` pelo seu nome de usuário do PythonAnywhere (você pode encontrar no canto superior direito do painel).

5. Clique em **"Save"**

---

## 📁 Passo 6: Configurar Diretório Estático

1. Na página de configuração do Web App, procure por **"Static files"**
2. Clique em **"Add a new static files entry"**
3. Preencha:
   - **URL:** `/static/`
   - **Directory:** `/home/{seu_username}/detector-smishing-tcc/backend/static`
4. Clique em **"Save"**

---

## 🔄 Passo 7: Recarregar a Aplicação

1. Na página de configuração do Web App, procure pelo botão **"Reload"** (verde)
2. Clique em **"Reload {seu_username}.pythonanywhere.com"**
3. Aguarde alguns segundos

---

## ✅ Passo 8: Testar a API

1. Abra seu navegador
2. Acesse `https://{seu_username}.pythonanywhere.com/`
3. Você deve ver uma resposta JSON com as informações da API

**Exemplos de URLs para testar:**

- **Health Check:** `https://{seu_username}.pythonanywhere.com/health`
- **Swagger UI:** `https://{seu_username}.pythonanywhere.com/docs`
- **ReDoc:** `https://{seu_username}.pythonanywhere.com/redoc`

---

## 🔗 Passo 9: Obter URL da API

Sua API estará disponível em:

```
https://{seu_username}.pythonanywhere.com
```

**Guarde esta URL**, pois você precisará dela para configurar o frontend.

---

## 🛠️ Troubleshooting

### Erro: "ModuleNotFoundError"

**Solução:**
1. Verifique se o ambiente virtual foi ativado corretamente
2. Reinstale as dependências:
   ```bash
   workon detector-api
   pip install -r requirements.txt
   ```

### Erro: "Permission denied"

**Solução:**
1. Verifique as permissões dos arquivos:
   ```bash
   chmod 755 /home/{seu_username}/detector-smishing-tcc/backend
   ```

### API retorna erro 500

**Solução:**
1. Verifique o log de erros:
   - No painel do PythonAnywhere, clique em **"Web"**
   - Procure por **"Error log"**
   - Verifique as mensagens de erro

### Modelos não carregam

**Solução:**
1. Verifique se os arquivos `.pkl` estão no diretório correto:
   ```bash
   ls -la /home/{seu_username}/detector-smishing-tcc/backend/*.pkl
   ```
2. Se os arquivos não existirem, faça upload deles via SFTP

---

## 📤 Fazer Upload de Arquivos (se necessário)

Se os arquivos `.pkl` não estiverem no repositório:

1. No painel do PythonAnywhere, clique em **"Files"**
2. Navegue até `/home/{seu_username}/detector-smishing-tcc/backend/`
3. Clique em **"Upload"** e selecione os arquivos:
   - `tfidf_vectorizer.pkl`
   - `random_forest.pkl`
   - `complement_naive_bayes.pkl`
   - `data_processed.csv`

---

## 🔄 Atualizar a API

Quando você fizer mudanças no código:

1. Faça push das mudanças para o GitHub
2. No terminal Bash do PythonAnywhere:
   ```bash
   cd ~/detector-smishing-tcc/backend
   git pull origin main
   ```
3. Se houver novas dependências:
   ```bash
   workon detector-api
   pip install -r requirements.txt
   ```
4. No painel do PythonAnywhere, clique em **"Reload"** para recarregar a aplicação

---

## 🔐 Configurações de Segurança

### Ativar HTTPS

1. No painel do PythonAnywhere, clique em **"Web"**
2. Procure por **"Security"**
3. Ative **"Force HTTPS"**

### Configurar CORS

No arquivo `main.py`, você pode ajustar o CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.netlify.app"],  # Seu domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitorar a API

### Ver Logs

1. No painel do PythonAnywhere, clique em **"Web"**
2. Clique em **"Error log"** ou **"Server log"**
3. Verifique as mensagens de erro

### Ver Uso de CPU

1. No painel do PythonAnywhere, clique em **"Consoles"**
2. Veja o uso de CPU em tempo real

---

## 💡 Dicas Importantes

1. **Plano Gratuito:** O PythonAnywhere gratuito tem limitações, mas é suficiente para este projeto
2. **Sem Suspensão:** Diferentemente do Render, o PythonAnywhere não suspende aplicações
3. **Sem Cartão de Crédito:** Não é necessário cartão de crédito para a conta gratuita
4. **Backup:** Faça backup regular dos seus dados

---

## 🎉 Pronto!

Sua API está agora em produção! 

**URL da API:** `https://{seu_username}.pythonanywhere.com`

Próximo passo: [Fazer deploy do Frontend no Netlify](GUIA_DEPLOY_FRONTEND.md)

---

## 📞 Suporte

Se encontrar problemas:

1. Consulte a [documentação do PythonAnywhere](https://help.pythonanywhere.com/)
2. Verifique os logs de erro
3. Teste a API localmente para isolar o problema

---

**Desenvolvido com ❤️ para o TCC da UNIVESP**
