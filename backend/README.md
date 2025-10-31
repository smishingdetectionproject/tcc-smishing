# Backend - Detector de Smishing

Este diretório contém a API backend desenvolvida em Python com FastAPI para o projeto de detecção de smishing.

## 📋 Descrição

A API fornece endpoints para:

- **Análise de SMS:** Classifica mensagens como "Legítima" ou "Smishing"
- **Extração de Características:** Identifica padrões suspeitos na mensagem
- **Feedback Contínuo:** Armazena feedback do usuário para melhoria do modelo
- **Estatísticas:** Fornece dados sobre o treinamento do modelo

## 🚀 Como Executar Localmente

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Instalação

1. **Navegue até o diretório do backend:**
   ```bash
   cd backend
   ```

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   # No Windows
   python -m venv venv
   venv\Scripts\activate

   # No macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

### Executar a API

```bash
python main.py
```

A API estará disponível em `http://localhost:8000`

### Acessar a Documentação Interativa

Abra seu navegador e acesse:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 📁 Estrutura de Arquivos

```
backend/
├── main.py                      # Arquivo principal da API
├── requirements.txt             # Dependências Python
├── README.md                    # Este arquivo
├── tfidf_vectorizer.pkl         # Vetorizador TF-IDF treinado
├── random_forest.pkl            # Modelo Random Forest
├── complement_naive_bayes.pkl   # Modelo Complement Naive Bayes
├── data_processed.csv           # Dados de treinamento
├── data/                        # Diretório para dados gerados
│   └── feedback.csv            # Feedback dos usuários (gerado automaticamente)
└── models/                      # Diretório para modelos adicionais
```

## 🔌 Endpoints da API

### 1. GET `/`
Verifica se a API está funcionando e retorna informações sobre os modelos carregados.

**Resposta:**
```json
{
  "nome": "Detector de Smishing",
  "versao": "1.0.0",
  "status": "ativo",
  "modelos_carregados": {
    "random_forest": true,
    "naive_bayes": true,
    "tfidf_vectorizer": true
  }
}
```

### 2. GET `/health`
Verifica a saúde da API.

**Resposta:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-30T10:00:00"
}
```

### 3. POST `/analisar`
Analisa uma mensagem SMS para detectar smishing.

**Requisição:**
```json
{
  "mensagem": "Clique aqui para confirmar sua conta: http://bit.ly/123abc",
  "modelo": "random_forest"
}
```

**Resposta:**
```json
{
  "veredito": "Smishing",
  "confianca": 0.95,
  "caracteristicas": [
    {
      "nome": "Presença de Links",
      "descricao": "Contém links que podem levar a sites maliciosos.",
      "icone": "🔗",
      "confianca": 0.75
    }
  ],
  "explicacao": "Esta mensagem foi classificada como uma potencial tentativa de smishing...",
  "modelo_usado": "random_forest"
}
```

### 4. POST `/feedback`
Registra o feedback do usuário sobre a análise.

**Requisição:**
```json
{
  "mensagem": "Clique aqui para confirmar sua conta",
  "veredito_original": "Smishing",
  "feedback_util": true,
  "feedback_usuario": "Realmente era smishing!"
}
```

**Resposta:**
```json
{
  "sucesso": true,
  "mensagem": "Feedback registrado com sucesso. Obrigado por ajudar a melhorar o modelo!"
}
```

### 5. GET `/estatisticas`
Retorna estatísticas sobre os dados de treinamento.

**Resposta:**
```json
{
  "total_mensagens": 3189,
  "contagem_classes": {
    "Legitimate": 1500,
    "Smishing": 1689
  },
  "colunas": ["id", "type", "message", "label", "length", "cleaned_message"],
  "timestamp": "2025-10-30T10:00:00"
}
```

## 🔐 Segurança

- **CORS:** Configurado para aceitar requisições de qualquer origem (ajustar em produção)
- **Validação:** Todas as entradas são validadas
- **Sanitização:** Mensagens são processadas com segurança
- **Limite de Tamanho:** Mensagens limitadas a 500 caracteres

## 🧠 Modelos de Machine Learning

### Random Forest
- **Acurácia:** ~97.86%
- **Precisão (Smishing):** ~95.45%
- **Recall (Smishing):** ~94.59%
- **F1-Score:** ~95.02%

### Complement Naive Bayes
- **Acurácia:** ~94.54%
- **Precisão (Smishing):** ~80.29%
- **Recall (Smishing):** ~99.10%
- **F1-Score:** ~88.71%

## 📊 Dados de Treinamento

Os dados utilizados para treinar os modelos incluem:

- **Total de Mensagens:** 3.189
- **Mensagens Legítimas:** ~1.500
- **Mensagens de Smishing:** ~1.689
- **Idioma:** Português (Moçambique)
- **Fonte:** Dataset de SMS com rótulos manuais

## 🔄 Aprendizado Contínuo

O sistema registra o feedback dos usuários em `data/feedback.csv`. Esses dados podem ser utilizados para:

1. Avaliar a performance do modelo em produção
2. Identificar falsos positivos/negativos
3. Retreinar o modelo periodicamente com novos dados

## 🛠️ Desenvolvimento

### Estrutura do Código

- **Carregamento de Modelos:** Os modelos são carregados na inicialização
- **Vetorização:** Mensagens são convertidas em vetores TF-IDF
- **Predição:** Ambos os modelos podem ser usados para análise
- **Características:** Padrões são extraídos para explicabilidade

### Adicionar Novos Endpoints

Para adicionar um novo endpoint, siga o padrão:

```python
@app.post("/novo-endpoint")
async def novo_endpoint(request: NovoRequest):
    """Descrição do endpoint"""
    try:
        # Lógica aqui
        return NovoResponse(...)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do backend com:

```
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
RELOAD=True
```

## 🚀 Deploy em Produção

### PythonAnywhere

1. Faça upload dos arquivos para o PythonAnywhere
2. Configure um web app com Python 3.11
3. Configure o WSGI para apontar para `main.py`
4. Instale as dependências com pip
5. Recarregue o web app

### Considerações de Segurança

- Alterar `allow_origins` no CORS para domínios específicos
- Implementar rate limiting
- Adicionar autenticação se necessário
- Usar HTTPS em produção

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação interativa em `/docs` ou entre em contato através do formulário de contato do site.

---

**Desenvolvido com ❤️ para o TCC da UNIVESP**
