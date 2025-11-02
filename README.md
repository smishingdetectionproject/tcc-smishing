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
tcc-smishing/
├── .git/                     # Arquivos de controle de versão
├── backend/                  # Backend Python (FastAPI)
│   ├── main.py               # Lógica principal e endpoints da API
│   ├── requirements.txt      # Dependências Python
│   ├── models/               # Modelos de Machine Learning (PKL)
│   ├── data/                 # Dados de treinamento/processamento
│   ├── build.sh              # Script de build para o Render
│   └── ...                   # Outros arquivos de configuração e modelo
├── client/                   # Frontend Estático
│   └── public/               # Conteúdo estático (HTML, CSS, JS)
│       ├── index.html        # Página principal
│       ├── detector.html     # Página do detector
│       ├── contato.html      # Página de contato
│       ├── css/              # Arquivos CSS
│       └── js/               # Arquivos JavaScript
├── docs/                     # Documentação do projeto
├── notebooks/                # Jupyter Notebooks (Processamento de dados e treinamento)
├── .gitignore                # Arquivos ignorados pelo Git
├── netlify.toml              # Configuração de deploy do Frontend (Netlify)
└── README.md                 # Este arquivo
```

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
- **URL**: [Entre em Contato Conosco](https://detectordesmishing.netlify.app/contato)

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
**Versão**: 2.0.0 
**Status**: Em Produção e Testes Contínuos
