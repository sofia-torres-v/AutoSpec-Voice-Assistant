import itertools
import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction


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

    results = collection.query(query_texts=[question], n_results=3)

    return results


def get_rag_response(question):

    session = boto3.Session()
    bedrock = session.client(service_name="bedrock-runtime")

    collection = get_collection("../../data/chroma", "autospec_collection")

    search_results = get_vector_search_results(collection, question)

    flattened_results_list = list(itertools.chain(*search_results["documents"]))

    rag_content = "\n\n".join(flattened_results_list)
    print(rag_content)

    message = {
        "role": "user",
        "content": [
            {
                "text": "Eres un asistente experto en fichas técnicas automotrices. A continuación tienes fragmentos de distintas fichas técnicas, que pueden corresponder a diferentes modelos de vehículo:"
            },
            {"text": rag_content},
            {
                "text": "Instrucciones: Responde ÚNICAMENTE con información del fragmento que corresponda al modelo mencionado en la pregunta. Si hay fragmentos de otros modelos en el contexto, ignóralos por completo — no los mezcles en tu respuesta. Si la información solicitada no aparece en los fragmentos proporcionados, responde exactamente: 'No tengo esa información en las fichas técnicas disponibles.' No inventes ni completes datos que no estén en el contexto."
            },
            {"text": f"Pregunta: {question}"},
        ],
    }

    response = bedrock.converse(
        modelId="us.amazon.nova-2-lite-v1:0",
        messages=[message],
        inferenceConfig={"maxTokens": 2000, "stopSequences": []},
    )

    return response["output"]["message"]["content"][0]["text"], flattened_results_list
