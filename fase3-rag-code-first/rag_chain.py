import os
import sqlite3
import datetime
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

PROMPT_TEMPLATE = """Eres un asistente experto en fichas técnicas automotrices.
A continuación tienes fragmentos que pueden corresponder a diferentes modelos de vehículo:

{context}

Instrucciones: Responde ÚNICAMENTE con información del fragmento que corresponda al
modelo mencionado en la pregunta. Si hay fragmentos de otros modelos, ignóralos por
completo. Si la información no aparece en los fragmentos, responde exactamente:
'No tengo esa información en las fichas técnicas disponibles.' No inventes datos.

Pregunta: {question}"""


def init_db(db_path="./conversation_logs.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            question TEXT,
            answer TEXT,
            retrieved_chunks TEXT
        )
    """)
    conn.commit()
    return conn


def log_interaction(question, answer, retrieved_chunks):
    conn = init_db()
    conn.execute(
        "INSERT INTO conversation_logs (timestamp, question, answer, retrieved_chunks) VALUES (?, ?, ?, ?)",
        (
            datetime.datetime.now().isoformat(),
            question,
            answer,
            "\n---\n".join(retrieved_chunks),
        ),
    )
    conn.commit()
    conn.close()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_response(question):
    api_key = os.environ["GEMINI_API_KEY"]

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001", google_api_key=api_key
    )
    vectorstore = Chroma(
        persist_directory="./chroma_langchain",
        collection_name="autospec_collection_v3",
        embedding_function=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Recuperamos los documentos por separado (no solo dentro de la cadena)
    # para poder guardarlos en el log junto con la respuesta.
    retrieved_docs = retriever.invoke(question)
    retrieved_texts = [doc.page_content for doc in retrieved_docs]

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=api_key)

    chain = (
        {
            "context": lambda x: format_docs(retrieved_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(question)

    log_interaction(question, answer, retrieved_texts)

    return answer
