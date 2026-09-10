import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

archivos = [
    "modelo_alpha_ficha_tecnica.txt",
    "modelo_beta_ficha_tecnica.txt",
    "modelo_gamma_ficha_tecnica.txt",
]

documentos = []
for nombre in archivos:
    with open(nombre, encoding="utf-8") as f:
        texto = f.read()
    documentos.append(Document(page_content=texto, metadata={"source": nombre}))

splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
chunks = splitter.split_documents(documentos)

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.environ["GEMINI_API_KEY"],
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_langchain",
    collection_name="autospec_collection_v3",
)

print(f"Colección lista con {vectorstore._collection.count()} fragmentos")
