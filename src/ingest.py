import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
for k in ("OPENAI_API_KEY", "PDF_PATH", "OPENAI_EMBEDDING_MODEL", "DATABASE_URL", "PG_VECTOR_COLLECTION_NAME"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

PDF_PATH = os.getenv("PDF_PATH")


def ingest_pdf():
    docs = PyPDFLoader(PDF_PATH).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=False)

    chunks = splitter.split_documents(docs)

    if not chunks:
        raise ValueError("No chunks generated from the PDF")

    print(f"{len(chunks)} chunks created.")

    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in chunks
    ]

    ids = [f"doc-{i}" for i in range(len(enriched))]

    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL"))

    # pre_delete_collection evita que chunks de uma ingestão anterior permaneçam no banco
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
        pre_delete_collection=True,
    )

    print("Store created.")

    store.add_documents(documents=enriched, ids=ids)

    print("Embeddings generated and documents added to store.")


if __name__ == "__main__":
    ingest_pdf()
