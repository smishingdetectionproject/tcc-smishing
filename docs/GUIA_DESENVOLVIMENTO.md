# 💻 Guia de Desenvolvimento Local

Este guia fornece instruções para configurar o ambiente de desenvolvimento local e contribuir com o projeto Detector de Smishing.

---

## 📋 Pré-requisitos

- **Python 3.8+** (para o backend)
- **Git** (para controle de versão)
- **Um editor de código** (VS Code, PyCharm, etc.)
- **Navegador moderno** (Chrome, Firefox, etc.)

---

## 🔧 Configuração Inicial

### 1. Clonar o Repositório

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/detector-smishing-tcc.git

# Navegar para o diretório do projeto
cd detector-smishing-tcc
```

### 2. Estrutura do Projeto

```
detector-smishing-tcc/
├── backend/                    # API FastAPI
├── client/                     # Frontend HTML/CSS/JS
├── docs/                       # Documentação
├── README.md                   # Documentação principal
├── todo.md                     # Lista de tarefas
└── .gitignore                  # Arquivos ignorados
```

---

## 🚀 Executar o Backend Localmente

### Passo 1: Criar Ambiente Virtual

```bash
# Navegar para o diretório do backend
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Passo 2: Instalar Dependências

```bash
# Instalar dependências do requirements.txt
pip install -r requirements.txt
```

### Passo 3: Executar a API

```bash
# Executar a API
python main.py
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Passo 4: Testar a API

Abra seu navegador e acesse:

- **API Root:** http://localhost:8000/
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🌐 Executar o Frontend Localmente

### Opção 1: Abrir no Navegador (Mais Simples)

1. Abra o arquivo `client/public/index.html` diretamente no navegador
2. O site funcionará, mas sem servidor local

### Opção 2: Usar Servidor Local Python

```bash
# Navegar para o diretório do frontend
cd client/public

# Iniciar servidor local
python -m http.server 3000
```

Acesse: http://localhost:3000

### Opção 3: Usar http-server (Node.js)

```bash
# Instalar http-server globalmente
npm install -g http-server

# Navegar para o diretório do frontend
cd client/public

# Iniciar servidor
http-server -p 3000
```

Acesse: http://localhost:3000

---

## 🔗 Conectar Frontend e Backend Localmente

### Atualizar URL da API

1. Abra o arquivo `client/public/js/main.js`
2. Procure pela linha:
   ```javascript
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
   ```
3. Certifique-se de que está apontando para `http://localhost:8000`

### Testar Conexão

1. Abra o console do navegador (F12)
2. Acesse a página do detector
3. Insira uma mensagem e clique em "Analisar"
4. Verifique se a análise é realizada

---

## 📝 Estrutura do Código

### Backend

```
backend/
├── main.py                     # Arquivo principal da API
├── requirements.txt            # Dependências
├── tfidf_vectorizer.pkl        # Vetorizador
├── random_forest.pkl           # Modelo RF
├── complement_naive_bayes.pkl  # Modelo NB
├── data_processed.csv          # Dados de treinamento
├── data/                       # Diretório de dados gerados
└── README.md                   # Documentação
```

**Principais funções em `main.py`:**

- `analisar_mensagem()` - Endpoint POST `/analisar`
- `registrar_feedback()` - Endpoint POST `/feedback`
- `extrair_caracteristicas_smishing()` - Extrai características
- `analisar_com_modelo()` - Realiza predição

### Frontend

```
client/public/
├── index.html                  # Dashboard
├── detector.html               # Página do detector
├── sobre.html                  # Página Sobre Nós
├── contato.html                # Página de Contato
├── css/
│   └── style.css               # Estilos globais
└── js/
    ├── main.js                 # Scripts globais
    ├── charts.js               # Gráficos
    ├── detector.js             # Lógica do detector
    └── contato.js              # Lógica do formulário
```

---

## 🛠️ Tarefas Comuns

### Adicionar Nova Funcionalidade

1. Crie uma branch para sua feature:
   ```bash
   git checkout -b feature/minha-funcionalidade
   ```

2. Faça as mudanças necessárias

3. Teste localmente

4. Faça commit:
   ```bash
   git add .
   git commit -m "Adiciona minha funcionalidade"
   ```

5. Faça push:
   ```bash
   git push origin feature/minha-funcionalidade
   ```

6. Abra um Pull Request no GitHub

### Corrigir um Bug

1. Crie uma branch para o bug:
   ```bash
   git checkout -b bugfix/descricao-do-bug
   ```

2. Corrija o problema

3. Teste a correção

4. Faça commit e push

5. Abra um Pull Request

### Atualizar Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Atualizar todas as dependências
pip install --upgrade -r requirements.txt

# Gerar novo requirements.txt
pip freeze > requirements.txt
```

---

## 🧪 Testes

### Testar Análise de Mensagens

Use o Swagger UI em http://localhost:8000/docs:

1. Clique em **POST /analisar**
2. Clique em **"Try it out"**
3. Insira um JSON:
   ```json
   {
     "mensagem": "Clique aqui para confirmar sua conta: http://bit.ly/123",
     "modelo": "random_forest"
   }
   ```
4. Clique em **"Execute"**
5. Verifique a resposta

### Testar Feedback

1. Clique em **POST /feedback**
2. Clique em **"Try it out"**
3. Insira um JSON:
   ```json
   {
     "mensagem": "Teste",
     "veredito_original": "Smishing",
     "feedback_util": true,
     "feedback_usuario": "Estava correto"
   }
   ```
4. Clique em **"Execute"**

---

## 🐛 Debugging

### Backend

1. Adicione prints no código:
   ```python
   print(f"Debug: {variavel}")
   ```

2. Use o debugger do Python:
   ```python
   import pdb; pdb.set_trace()
   ```

3. Verifique os logs na saída do terminal

### Frontend

1. Abra o console do navegador (F12)
2. Procure por erros em vermelho
3. Use `console.log()` para debug:
   ```javascript
   console.log("Debug:", variavel);
   ```

---

## 📚 Recursos Úteis

### Documentação

- [FastAPI](https://fastapi.tiangolo.com/) - Framework backend
- [Scikit-learn](https://scikit-learn.org/) - Machine Learning
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [Chart.js](https://www.chartjs.org/) - Gráficos

### Ferramentas

- [Postman](https://www.postman.com/) - Testar APIs
- [VS Code](https://code.visualstudio.com/) - Editor de código
- [Git](https://git-scm.com/) - Controle de versão

---

## 📋 Checklist de Desenvolvimento

Antes de fazer um commit:

- [ ] Código testado localmente
- [ ] Sem erros no console
- [ ] Sem warnings
- [ ] Código formatado
- [ ] Comentários adicionados (se necessário)
- [ ] Documentação atualizada (se necessário)

Antes de fazer um Pull Request:

- [ ] Branch atualizada com `main`
- [ ] Sem conflitos de merge
- [ ] Testes passando
- [ ] Descrição clara do PR

---

## 🔄 Workflow Git

```bash
# 1. Criar branch
git checkout -b feature/minha-feature

# 2. Fazer mudanças e testar

# 3. Adicionar mudanças
git add .

# 4. Fazer commit
git commit -m "Descrição clara das mudanças"

# 5. Fazer push
git push origin feature/minha-feature

# 6. Abrir Pull Request no GitHub

# 7. Após merge, deletar branch local
git checkout main
git branch -d feature/minha-feature
```

---

## 💡 Boas Práticas

1. **Commits Claros:** Use mensagens descritivas
2. **Branches Pequenas:** Cada branch deve resolver um problema
3. **Testes:** Sempre teste antes de fazer push
4. **Documentação:** Mantenha a documentação atualizada
5. **Código Limpo:** Siga as convenções de código

---

## 🤝 Contribuindo

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Faça push para a branch
5. Abra um Pull Request

---

## 📞 Suporte

Se tiver dúvidas:

1. Consulte a documentação
2. Abra uma issue no GitHub
3. Procure por exemplos similares no código

---

**Desenvolvido com ❤️ para o TCC da UNIVESP**
