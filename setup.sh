#!/bin/bash

# Script para configurar o ambiente de desenvolvimento

echo "🚀 Configurando ambiente de desenvolvimento do Carreira..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3.8+"
    exit 1
fi

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Por favor, instale o Node.js 16+"
    exit 1
fi

echo "✅ Python e Node.js encontrados"

# Criar ambiente virtual para o backend
echo "📦 Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências do backend
echo "📦 Instalando dependências do backend..."
pip install -r requirements.txt

# Configurar arquivo .env
if [ ! -f .env ]; then
    echo "⚙️  Configurando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Por favor, ajuste as configurações conforme necessário."
fi

# Inicializar banco de dados
echo "🗄️  Inicializando banco de dados..."
python backend/init_db.py

# Instalar dependências do frontend
echo "📦 Instalando dependências do frontend..."
cd frontend
npm install

# Build do frontend (opcional)
echo "🔨 Build do frontend..."
npm run build

cd ..

echo ""
echo "🎉 Ambiente configurado com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Ative o ambiente virtual: source venv/bin/activate"
echo "2. Inicie o backend: python carreira.py"
echo "3. Inicie o frontend (em outro terminal): cd frontend && npm start"
echo ""
echo "🔐 Credenciais de teste:"
echo "- Admin: admin / admin123"
echo "- RH: rh / rh123"
echo "- Usuário: joao.silva / joao123"