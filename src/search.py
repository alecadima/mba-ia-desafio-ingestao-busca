import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector

load_dotenv()

REQUIRED_ENV_VARS = (
    "OPENAI_API_KEY",
    "OPENAI_EMBEDDING_MODEL",
    "OPENAI_CHAT_MODEL",
    "DATABASE_URL",
    "PG_VECTOR_COLLECTION_NAME",
)

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def search_prompt(question=None):
    """Build the RAG chain. If a question is given, return its answer instead of the chain."""
    for k in REQUIRED_ENV_VARS:
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL"))

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    def buscar_contexto(pergunta):
        results = store.similarity_search_with_score(pergunta, k=10)
        return "\n\n".join(doc.page_content for doc, _score in results)

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

    model = ChatOpenAI(temperature=0.0, model=os.getenv("OPENAI_CHAT_MODEL"))

    rag_chain = (
        {"contexto": RunnableLambda(buscar_contexto), "pergunta": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    if question is None:
        return rag_chain

    return rag_chain.invoke(question)
