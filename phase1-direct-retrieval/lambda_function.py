import json
import boto3

# Cliente para la API de ejecucion de Bedrock Agents/KB
bedrock_agent_client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

# Knowledge Base ID asignado por AWS
KNOWLEDGE_BASE_ID = "FZTIBQAOEW"


def lambda_handler(event, context):
    try:
        # 1. Capturar la pregunta del evento
        if isinstance(event, dict) and "prompt" in event:
            user_query = event["prompt"]
        elif isinstance(event, dict) and "inputTranscript" in event:
            user_query = event["inputTranscript"]
        else:
            user_query = (
                "¿Cuáles son las especificaciones de seguridad del modelo Alpha?"
            )

        print(f"--> Pregunta recibida: {user_query}")

        # 2. Búsqueda Vectorial Pura (Retrieval Directo sin LLM - Fase 1)
        kb_response = bedrock_agent_client.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID, retrievalQuery={"text": user_query}
        )

        # 3. Procesar fragmentos devueltos por la Knowledge Base
        retrieved_results = kb_response.get("retrievalResults", [])

        extracted_chunks = []
        for index, result in enumerate(retrieved_results):
            text_chunk = result["content"]["text"]
            score = result.get("score", 0)
            extracted_chunks.append(
                f"[Resultado {index+1} - Relevancia: {score:.2f}]:\n{text_chunk}"
            )

        if not extracted_chunks:
            final_answer = (
                "No se encontró información técnica relevante en las fichas de S3."
            )
        else:
            final_answer = "\n\n---\n\n".join(extracted_chunks)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"pregunta": user_query, "respuesta_recuperada": final_answer},
                ensure_ascii=False,
            ),
        }

    except Exception as e:
        print(f"Error en el proceso de Retrieval: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}