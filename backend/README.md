# Backend

API em FastAPI para servir o frontend e processar requisições.

## Como iniciar

1. Crie um ambiente virtual (opcional, mas recomendado):
   python -m venv venv
2. Ative o ambiente virtual:
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate  # Windows
3. Instale as dependências:
   pip install -r requirements.txt
4. Rode o servidor:
   uvicorn main:app --reload
