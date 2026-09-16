import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

session = boto3.Session()
embedding_function = AmazonBedrockEmbeddingFunction(
    session=session, model_name="amazon.titan-embed-text-v2:0"
)

client = chromadb.PersistentClient()
collection = client.get_or_create_collection(
    "autospec_collection", embedding_function=embedding_function
)

archivos = [
    "modelo_alpha_ficha_tecnica.txt",
    "modelo_beta_ficha_tecnica.txt",
    "modelo_gamma_ficha_tecnica.txt",
]

for i, nombre in enumerate(archivos):
    with open(nombre, encoding="utf-8") as f:
        texto = f.read()
    collection.add(ids=[str(i)], documents=[texto], metadatas=[{"source": nombre}])

print(f"Colección lista con {collection.count()} documentos")
