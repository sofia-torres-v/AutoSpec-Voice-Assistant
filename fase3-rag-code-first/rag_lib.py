import os
import itertools
import sqlite3
import datetime
import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction
from google import genai

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "bedrock")  # "bedrock" o "gemini"


def init_db(db_path="../../data/conversation_logs.db"):
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
        """INSERT INTO conversation_logs (timestamp, question, answer, retrieved_chunks)
        VALUES (?, ?, ?, ?)""",
        (
            datetime.datetime.now().isoformat(),
            question,
            answer,
            "\n---\n".join(retrieved_chunks),
        ),
    )
    conn.commit()
    conn.close()


def get_collection(path, collection_name):
    session = boto3.Session()
    embedding_function = AmazonBedrockEmbeddingFunction(
        session=session, model_name="amazon.titan-embed-text-v2:0"
    )
    client = chromadb.PersistentClient(path=path)
    collection = client.get_collection(
        collection_name, embedding_function=embedding_function
    )
    return collection


def get_vector_search_results(collection, question):
    return collection.query(query_texts=[question], n_results=3)


def generar_respuesta(rag_content, question):
    prompt = f"""Eres un asistente experto en fichas técnicas automotrices. A
continuación tienes fragmentos de distintas fichas técnicas, que pueden corresponder
a diferentes modelos de vehículo:
{rag_content}
Instrucciones: Responde ÚNICAMENTE con información del fragmento que
corresponda al modelo mencionado en la pregunta. Si hay fragmentos de otros
modelos en el contexto, ignóralos por completo. Si la información solicitada no aparece
en los fragmentos proporcionados, responde exactamente: 'No tengo esa información
en las fichas técnicas disponibles.' No inventes datos.
Pregunta: {question}"""

    if LLM_PROVIDER == "gemini":
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )
        return response.text
    else:  # bedrock (por defecto)
        session = boto3.Session()
        bedrock = session.client(service_name="bedrock-runtime")
        message = {"role": "user", "content": [{"text": prompt}]}
        response = bedrock.converse(
            modelId="us.amazon.nova-2-lite-v1:0",
            messages=[message],
            inferenceConfig={"maxTokens": 2000, "stopSequences": []},
        )
        return response["output"]["message"]["content"][0]["text"]


def get_rag_response(question):
    collection = get_collection("../../data/chroma", "autospec_collection")
    search_results = get_vector_search_results(collection, question)
    flattened_results_list = list(itertools.chain(*search_results["documents"]))
    rag_content = "\n\n".join(flattened_results_list)
    answer = generar_respuesta(rag_content, question)
    log_interaction(question, answer, flattened_results_list)
    return answer, flattened_results_list
