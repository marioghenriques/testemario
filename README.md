# Sistema de Carreira - MVP (Streamlit Edition)

## Visão Geral

Este é um sistema completo de desenvolvimento de carreira com visualização de matriz de competências, autoavaliação e registro de intenções de cursos. Construído com Streamlit e SQLite para um MVP rápido e eficiente.

## Funcionalidades

### ✅ Funcionalidades Implementadas

1. **📊 Dashboard Visual de Matriz de Competências**
   - Visualização clara do caminho de carreira FC-03 → FC-04 → FC-05 → FC-06
   - Indicadores visuais de status (✅ Dominada, 🟡 Em desenvolvimento, 🔴 Necessária)
   - Métricas de progresso e conclusão
   - Interface responsiva e intuitiva

2. **📝 Sistema de Autoavaliação**
   - Questionário estruturado com escala de 1-5
   - Progresso visual do preenchimento
   - Cálculo automático de lacunas de competências
   - Salvamento automático de respostas

3. **📚 Registro de Intenção de Cursos**
   - Recomendações personalizadas baseadas em lacunas identificadas
   - Sistema de priorização de cursos
   - Visualização de cursos já registrados
   - Interface amigável para seleção

4. **⚙️ Administração Básica**
   - Estatísticas do sistema (usuários, avaliações, intenções)
   - Visualizações de dados em gráficos
   - Distribuição de usuários por nível hierárquico
   - Análise de scores de avaliação

## Arquitetura

### Tecnologias Utilizadas
- **Frontend:** Streamlit (interface web completa)
- **Banco de Dados:** SQLite (leve, sem servidor)
- **Visualização:** Plotly (gráficos interativos)
- **Dados:** Pandas (manipulação de dados)
- **Python:** 3.8+ (versão mínima)

### Estrutura do Projeto
```
carreira/
├── carreira.py          # Aplicação principal Streamlit
├── database.py          # Modelo de dados e gerenciamento do SQLite
├── requirements.txt     # Dependências do projeto
└── career_development.db # Banco de dados SQLite (criado automaticamente)
```

## Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Passo 1: Clonar/Preparar o Projeto
```bash
# Navegar para o diretório do projeto
cd /Users/marioghenriques/bmad/carreira
```

### Passo 2: Criar Ambiente Virtual (Recomendado)
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Executar a Aplicação
```bash
# Executar o Streamlit
streamlit run carreira.py

# Ou diretamente com Python
python carreira.py
```

### Passo 5: Acessar a Aplicação
- Abra o navegador no endereço: `http://localhost:8501`
- A aplicação abrirá na página de login

## 🔐 Autenticação

O sistema utiliza JWT tokens para autenticação:

- **Usuário Comum**: Acesso ao dashboard e funcionalidades pessoais
- **RH**: Acesso administrativo limitado (aprovações, estatísticas)
- **Admin**: Acesso completo ao sistema

## 📊 Modelos de Dados

### Usuários
- Informações pessoais e profissionais
- Nível atual e alvo de carreira
- Role-based access control

### Competências
- Organizadas por níveis (FC-03, FC-04, FC-05/FC-06)
- Categorias: Técnica, Comportamental, Estratégica
- Sistema de prioridade e peso

### Avaliações
- Autoavaliação com escala 1-5
- Cálculo automático de status
- Histórico de evolução

### Cursos
- Catálogo completo com metadados
- Associação com competências
- Sistema de intenções e aprovação

## 🔄 Fluxos de Trabalho

### 1. Autoavaliação
1. Usuário acessa o sistema
2. Realiza autoavaliação de competências
3. Sistema calcula status e identifica lacunas
4. Gera recomendações de cursos

### 2. Desenvolvimento
1. Usuário explora catálogo de cursos
2. Registra intenções para cursos desejados
3. RH/Admin aprova as inscrições
4. Usuário acompanha progresso

### 3. Administração
1. Admin configura competências e cursos
2. RH aprova intenções de cursos
3. Ambos acessam estatísticas e relatórios
4. Exportam dados para análise

## 🧪 Testes

```bash
# Backend
python -m pytest

# Frontend
npm test
```

## 🚀 Deploy

### Backend (Produção)
```bash
# Variáveis de ambiente necessárias
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET_KEY=sua-chave-jwt

# Usar servidor WSGI (ex: Waitress)
waitress-serve --host=0.0.0.0 --port=5000 carreira:app
```

### Frontend (Produção)
```bash
# Build para produção
npm run build

# Servir arquivos estáticos
# Pode usar nginx, Apache, ou qualquer servidor web
```

## 📝 Variáveis de Ambiente

### Backend (.env)
```env
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///carreira.db
JWT_SECRET_KEY=sua-chave-jwt-aqui
JWT_ACCESS_TOKEN_EXPIRES=3600
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000/api
```

## 🔧 Configuração Adicional

### Banco de Dados
- **Desenvolvimento**: SQLite (padrão)
- **Produção**: PostgreSQL recomendado
- Configure no arquivo `.env`

### CORS
- Configurado para aceitar requisições do frontend
- Ajuste `FRONTEND_URL` no config.py para produção

## 📈 Monitoramento

O sistema inclui:

- Health check endpoint: `/api/admin/system/health`
- Logging estruturado
- Métricas de performance
- Tratamento de erros centralizado

## 🤝 Contribuição

1. Faça fork do projeto
2. Crie branch para sua feature (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT - veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

Para suporte, entre em contato:

- Email: suporte@carreira.com
- Issues: GitHub Issues
- Documentação: Wiki do projeto

---

**Desenvolvido com ❤️ para gestão de competências e desenvolvimento profissional**