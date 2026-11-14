# Ingestão e Busca Semântica com LangChain e Postgres

## Como executar

Pré-requisitos: Python 3.11+, Docker e Docker Compose e uma API Key da OpenAI.

1. Crie e ative o ambiente virtual e instale as dependências:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Copie o template de variáveis de ambiente e preencha `OPENAI_API_KEY`:

    ```bash
    cp .env.example .env
    ```

    | Variável | Descrição |
    | --- | --- |
    | `OPENAI_API_KEY` | API Key da OpenAI |
    | `OPENAI_EMBEDDING_MODEL` | Modelo de embeddings (ex.: `text-embedding-3-small`) |
    | `OPENAI_CHAT_MODEL` | Modelo de chat usado para responder (ex.: `gpt-5-nano`) |
    | `DATABASE_URL` | URL de conexão com o Postgres (padrão aponta para o `docker-compose.yml`) |
    | `PG_VECTOR_COLLECTION_NAME` | Nome da collection de vetores |
    | `PDF_PATH` | Caminho do PDF a ser ingerido |

3. Suba o banco de dados:

    ```bash
    docker compose up -d
    ```

4. Execute a ingestão do PDF (cada execução recria a collection do zero):

    ```bash
    python src/ingest.py
    ```

5. Inicie o chat e faça suas perguntas. Digite `sair` (ou use Ctrl+C) para encerrar:

    ```bash
    python src/chat.py
    ```

Execute os comandos a partir da raiz do projeto, pois `PDF_PATH` é relativo ao diretório atual.
