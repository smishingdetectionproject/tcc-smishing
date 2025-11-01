# 🛡️ Detector de Smishing - TCC UNIVESP

## 📋 Descrição do Projeto

> **Um Trabalho de Conclusão de Curso (TCC) de Ciência de Dados**

Seja bem-vindo (a) ao nosso repositório do Trabalho de Conclusão de Curso (TCC).
Este é o Detector de Smishing, uma ferramenta desenvolvida para identificar e se proteger contra tentativas de fraude via SMS (phishing por SMS). Este projeto combina Machine Learning, análise de texto e segurança da informação para oferecer uma solução prática e acessível.

O objetivo principal é **analisar mensagens fraudulentas do tipo smishing em língua portuguesa**, utilizando técnicas de Ciência de Dados com algoritmos clássicos de aprendizado de máquina, comparando o desempenho entre Complement Naive Bayes e Random Forest, de modo a demonstrar a viabilidade da aplicação em ambiente operacional e contribuir para a proteção dos usuários de serviços SMS.

---

## 📋 Visão Geral

O **Detector de Smishing** é um sistema web que utiliza modelos de Machine Learning para classificar mensagens SMS como legítimas ou fraudulentas (smishing). O projeto foi desenvolvido como parte do Trabalho de Conclusão de Curso (TCC) de Ciência de Dados da Universidade Virtual do Estado de São Paulo (UNIVESP).

### 🎯 Objetivo

Democratizar o conhecimento sobre segurança digital e fornecer uma ferramenta gratuita que ajude qualquer pessoa a se proteger contra ataques de smishing, um tipo de fraude cada vez mais comum no Brasil e no mundo.

### 📊 Resultados

- **Acurácia do Modelo Principal:** 97,86%
- **Dataset:** 3.189 mensagens SMS (1.689 smishing, 1.500 legítimas)
- **Modelos Treinados:** Random Forest e Complement Naive Bayes
- **Linguagem:** Português (Brasileiro)

---

## 👥 Equipe

Este projeto foi desenvolvido por estudantes da UNIVESP como parte do TCC:

| Membro | Função |
|--------|--------|
| DEIVID RODRIGO CORREIA DE MELO | Desenvolvimento do Vídeo explicativo do projeto |
| JOICE CRISTINA DA SILVA | Revisão da Documentação Teórica |
| MAGNO BRUNO CAMARGO PROENÇA | Desenvolvimento Documentação Teórica |
| OBRIEN PINEDA TEIXEIRA | Revisão da Documentação Teórica |
| TELMA FÁTIMA CLARITA DE CARVALHO | Desenvolvimento do treinamento de ML e Coleta de resultados |
| VAGNER SOUSA DOS SANTOS | Desenvolvimento Frontend e Backend da Aplicação |
| WELLINGTON PEREIRA DA SILVA | Desenvolvimento Documentação Teórica |

**Orientador(a):** Me. William Lima Quintiliano

---

## 🚀 Funcionalidades Principais

### 1. **Dashboard Interativo**
- Visualização de gráficos de desempenho dos modelos
- Nuvem de palavras das mensagens de smishing
- Informações sobre a metodologia do projeto
- Timeline visual do processo de desenvolvimento

### 2. **Detector de Smishing**
- Análise em tempo real de mensagens SMS
- Dois modelos disponíveis (Random Forest e Naive Bayes)
- Explicação detalhada das características detectadas
- Sistema de feedback para aprendizado contínuo
- Dicas de segurança integradas

### 3. **Página Sobre Nós**
- Descrição completa do projeto
- Metodologia e tecnologias utilizadas
- Informações sobre a equipe
- Estatísticas dos dados de treinamento

### 4. **Página de Contato**
- Formulário de contato com validação
- Integração com Formspree
- Aviso de privacidade
- Links para redes sociais

---

## 📱 Compatibilidade

### Navegadores Suportados
- ✅ Chrome/Chromium (versão 90+)
- ✅ Firefox (versão 88+)
- ✅ Safari (versão 14+)
- ✅ Edge (versão 90+)
- ✅ Opera (versão 76+)

### Dispositivos
- ✅ Desktop (1920x1080 e acima)
- ✅ Tablet (768px a 1024px)
- ✅ Mobile (até 768px)

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11** - Linguagem de programação
- **FastAPI** - Framework web moderno e rápido
- **Scikit-learn** - Biblioteca de Machine Learning
- **Pandas & NumPy** - Processamento de dados

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Estilos modernos e responsivos
- **JavaScript** - Interatividade
- **Bootstrap 5** - Framework CSS
- **Chart.js** - Visualização de gráficos
- **WordCloud.js** - Nuvem de palavras

### Hospedagem
- **Backend:** PythonAnywhere (gratuito, sem modo suspenso)
- **Frontend:** Netlify (gratuito com CI/CD)

### Ferramentas
- **Git & GitHub** - Controle de versão
- **Formspree** - Processamento de formulários

---

## 📁 Estrutura do Projeto

```
detector-smishing-tcc/
├── backend/                          # API Backend em Python
│   ├── main.py                       # Arquivo principal da API
│   ├── requirements.txt              # Dependências Python
│   ├── tfidf_vectorizer.pkl          # Vetorizador TF-IDF
│   ├── random_forest.pkl             # Modelo Random Forest
│   ├── complement_naive_bayes.pkl    # Modelo Naive Bayes
│   ├── data_processed.csv            # Dados de treinamento
│   ├── data/                         # Diretório de dados gerados
│   └── README.md                     # Documentação do backend
│
├── client/                           # Frontend Web
│   ├── public/                       # Arquivos estáticos
│   │   ├── index.html                # Dashboard
│   │   ├── detector.html             # Página do detector
│   │   ├── sobre.html                # Página Sobre Nós
│   │   ├── contato.html              # Página de Contato
│   │   ├── css/
│   │   │   └── style.css             # Estilos globais
│   │   └── js/
│   │       ├── main.js               # Scripts globais
│   │       ├── charts.js             # Gráficos e visualizações
│   │       ├── detector.js           # Lógica do detector
│   │       └── contato.js            # Lógica do formulário
│   └── README.md                     # Documentação do frontend
│
├── README.md                         # Este arquivo
└── .gitignore                        # Arquivos ignorados pelo Git
```

---

## 🔧 Como Executar Localmente

### Pré-requisitos

- **Python 3.8+** (para o backend)
- **Node.js 14+** (opcional, para servir o frontend)
- **Git** (para clonar o repositório)

### Backend

1. **Navegue até o diretório do backend:**
   ```
   cd backend
   ```

2. **Crie um ambiente virtual:**
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```
   pip install -r requirements.txt
   ```

4. **Execute a API:**
   ```
   python main.py
   ```

   A API estará disponível em `http://localhost:8000`

   **Documentação interativa:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Frontend

1. **Abra o arquivo `client/public/index.html` em um navegador** ou use um servidor local:

   ```
   # Com Python
   cd client/public
   python -m http.server 3000

   # Com Node.js (http-server)
   npm install -g http-server
   http-server client/public -p 3000
   ```

   O frontend estará disponível em `http://localhost:3000`

---

## 📊 Dados de Treinamento

O projeto utiliza um dataset de **3.189 mensagens SMS** em português (Brasileiro):

| Classe | Quantidade | Percentual |
|--------|-----------|-----------|
| Legítimas | 1.500 | 47,1% |
| Smishing | 1.689 | 52,9% |
| **Total** | **3.189** | **100%** |

**Fonte:** Dataset coletado de fontes públicas e validado manualmente

### Características do Dataset

- **Idioma:** Português (Brasileiro)
- **Tipo de Mensagens:** SMS reais
- **Validação:** Manual por especialistas
- **Balanceamento:** Aproximadamente equilibrado

---

## 🧠 Modelos de Machine Learning

### Random Forest (Modelo Principal)

- **Acurácia:** 97,86%
- **Precisão (Smishing):** 95,45%
- **Recall (Smishing):** 94,59%
- **F1-Score:** 95,02%

**Características:**
- Ensemble de árvores de decisão
- Robusto a overfitting
- Excelente generalização

### Complement Naive Bayes

- **Acurácia:** 94,54%
- **Precisão (Smishing):** 80,29%
- **Recall (Smishing):** 99,10%
- **F1-Score:** 88,71%

**Características:**
- Mais sensível a smishing (alto recall)
- Mais falsos positivos
- Rápido e leve

---

## 🔐 Segurança

### Medidas Implementadas
- ✅ Validação de formulário no cliente
- ✅ Uso de HTTPS (automático no Netlify)
- ✅ Sem armazenamento de dados sensíveis
- ✅ Proteção contra XSS (sanitização de inputs)
- ✅ CORS configurado corretamente

### Privacidade
- Os dados do formulário são processados apenas pelo Formspree
- Nenhuma informação é armazenada no servidor
- Consulte a política de privacidade do Formspree
- Conformidade com LGPD (Lei Geral de Proteção de Dados)

---

## 🚀 Deploy em Produção

### Backend - PythonAnywhere

1. Crie uma conta em [PythonAnywhere](https://www.pythonanywhere.com)
2. Faça upload dos arquivos do backend
3. Configure um web app com Python 3.11
4. Instale as dependências
5. Configure o WSGI para apontar para `main.py`

**Vantagens:**
- Gratuito
- Sem modo de suspensão
- Sem necessidade de cartão de crédito

### Frontend - Netlify

1. Crie uma conta em [Netlify](https://www.netlify.com)
2. Conecte seu repositório GitHub
3. Configure o build (se necessário)
4. Deploy automático

**Vantagens:**
- Gratuito
- CI/CD automático
- CDN global
- HTTPS incluído

---

### Código-Fonte
Todo o código está documentado com comentários explicativos em português.

---

## 🤝 Contribuições

Este é um projeto acadêmico. Para sugestões ou melhorias, entre em contato através da página de contato do site.

---

## 📝 Licença

Este projeto é fornecido como material educacional. Todos os direitos reservados ao grupo de desenvolvimento.

---

## 📞 Contato

Para dúvidas, sugestões ou feedback, utilize o formulário de contato disponível em:
- **URL**: [URL DISPONÍVEL NO FUTURO](https://dashboardipcaecombustiveis.netlify.app/contato)

---

## 🙏 Agradecimentos

- **UNIVESP** - Universidade Virtual do Estado de São Paulo pelo apoio
- **Orientador Me. William Lima Quintiliano** - Pelos ensinamentos e orientação
- **Comunidade de Machine Learning e segurança digital**
- **Todos os que contribuíram com feedback e sugestões**

---

## 📖 Referências

1. **Machine Learning:**
   - Scikit-learn Documentation: https://scikit-learn.org/
   - TF-IDF: https://en.wikipedia.org/wiki/Tf%E2%80%93idf

2. **Segurança Digital:**
   - OWASP: https://owasp.org/
   - LGPD: https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd

3. **Desenvolvimento Web:**
   - MDN Web Docs: https://developer.mozilla.org/
   - Bootstrap: https://getbootstrap.com/

---

**Desenvolvido com ❤️ para a comunidade brasileira**

**Criado em**: Outubro de 2025  
**Versão**: 1.1.0  
**Status**: Em Desenvolvimento e Teste
