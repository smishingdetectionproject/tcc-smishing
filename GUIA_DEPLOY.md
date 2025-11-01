# Guia de Deploy - Detector de Smishing TCC

## 📋 Visão Geral

Este guia explica como publicar o projeto em produção, separando frontend e backend.

## 🎨 Frontend (Netlify)

### Opção 1: Deploy via Interface Web (Recomendado)

1. **Acesse o Netlify**
   - Vá para https://app.netlify.com
   - Faça login ou crie uma conta gratuita

2. **Crie um novo site**
   - Clique em "Add new site" > "Deploy manually"
   - Arraste a pasta `client/public` para a área de upload
   - Aguarde o deploy completar

3. **Configure a variável de ambiente**
   - Vá em "Site settings" > "Environment variables"
   - Adicione uma nova variável:
     - **Nome**: `VITE_API_URL`
     - **Valor**: URL do seu backend (ex: `https://seu-backend.onrender.com`)
   - Salve e faça redeploy

### Opção 2: Deploy via Git

1. **Conecte seu repositório**
   - No Netlify, clique em "Add new site" > "Import an existing project"
   - Conecte com GitHub/GitLab/Bitbucket
   - Selecione o repositório

2. **Configure o build**
   - **Base directory**: `client/public`
   - **Publish directory**: `.` (ponto)
   - **Build command**: (deixe vazio, são arquivos estáticos)

3. **Adicione variável de ambiente**
   - Mesma configuração da Opção 1

## 🐍 Backend (Render.com - Recomendado)

### Por que Render.com?
- ✅ Plano gratuito generoso
- ✅ Não precisa de cartão de crédito
- ✅ Suporta Python/FastAPI nativamente
- ✅ Não entra em modo sleep (750h/mês grátis)
- ✅ Deploy automático via Git

### Passo a Passo

1. **Acesse o Render**
   - Vá para https://render.com
   - Crie uma conta gratuita

2. **Crie um novo Web Service**
   - Clique em "New +" > "Web Service"
   - Conecte seu repositório Git
   - Selecione o repositório do projeto

3. **Configure o serviço**
   - **Name**: `detector-smishing-backend`
   - **Region**: Escolha a mais próxima (ex: Ohio)
   - **Branch**: `main` ou `master`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Configure variáveis de ambiente** (se necessário)
   - Adicione variáveis no painel "Environment"

5. **Deploy**
   - Clique em "Create Web Service"
   - Aguarde o build e deploy (5-10 minutos)
   - Copie a URL gerada (ex: `https://detector-smishing-backend.onrender.com`)

6. **Atualize o Frontend**
   - Volte no Netlify
   - Configure `VITE_API_URL` com a URL do Render
   - Faça redeploy do frontend

## 🔄 Alternativas de Backend

### Railway.app
```bash
# Instale o Railway CLI
npm install -g @railway/cli

# Faça login
railway login

# Crie um novo projeto
railway init

# Configure o backend
cd backend
railway up
```

### Fly.io
```bash
# Instale o Fly CLI
curl -L https://fly.io/install.sh | sh

# Faça login
fly auth login

# Crie e deploy
cd backend
fly launch
```

### PythonAnywhere (Mais simples, mas pode dormir)
1. Acesse https://www.pythonanywhere.com
2. Crie conta gratuita
3. Faça upload dos arquivos do backend
4. Configure um Web App com Flask/FastAPI
5. Use a URL gerada

## 🧪 Testando o Deploy

### Teste o Backend
```bash
# Substitua pela sua URL real
curl https://seu-backend.onrender.com/health

# Deve retornar:
# {"status":"ok","timestamp":"..."}
```

### Teste o Frontend
1. Acesse seu site no Netlify
2. Vá para a página "Detector"
3. Insira uma mensagem de teste
4. Clique em "Analisar"
5. Verifique se retorna resultado

## 📝 Checklist Final

- [ ] Backend publicado e funcionando
- [ ] URL do backend copiada
- [ ] Variável `VITE_API_URL` configurada no Netlify
- [ ] Frontend publicado
- [ ] Teste de análise funcionando
- [ ] Todas as páginas carregando corretamente

## ⚠️ Problemas Comuns

### "API indisponível"
- Verifique se a URL do backend está correta
- Confirme que o backend está rodando (acesse /health)
- Verifique CORS no backend (já está configurado)

### "Build failed" no Netlify
- Certifique-se de estar publicando `client/public`
- Não tente buildar, são arquivos estáticos

### Backend dormindo (Render free tier)
- O plano gratuito do Render pode dormir após 15 min de inatividade
- Primeira requisição pode demorar ~30s para "acordar"
- Para evitar: use um serviço de ping (ex: UptimeRobot)

## 🎓 Para o TCC

Recomendações para apresentação:

1. **Mantenha ambos os ambientes**
   - Local: para demonstrações offline
   - Online: para acesso dos avaliadores

2. **Documente as URLs**
   - Frontend: https://seu-site.netlify.app
   - Backend: https://seu-backend.onrender.com

3. **Prepare screenshots**
   - Tire prints do sistema funcionando
   - Inclua no relatório do TCC

4. **Backup dos dados**
   - Mantenha cópia dos modelos treinados
   - Documente as métricas (F1-Score)

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs no Render/Netlify
2. Teste localmente primeiro
3. Confirme que todas as dependências estão instaladas
4. Verifique as variáveis de ambiente

Boa sorte com o TCC! 🎉
