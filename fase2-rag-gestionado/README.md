# Fase 2 — RAG con AWS (Titan Embeddings + Nova Lite)

⬅️ [Volver al README principal](../README.md)

## Estado: ✅ Completada

Ciclo RAG completo usando Amazon Titan Text Embeddings V2 para la búsqueda vectorial y Amazon Nova Lite para la generación de la respuesta final, con un guardrail anti-alucinación validado.

## Archivos

- `populate_autospec.py` — genera embeddings de las 3 fichas técnicas y las guarda en una colección Chroma.
- `rag_lib.py` — lógica de retrieval (Chroma) + armado del prompt + generación con Nova Lite (Converse API).
- `rag_app.py` — interfaz de chat con Streamlit.

## Cómo probarlo

1. Instalar dependencias:

`pip install boto3 chromadb streamlit`

2. Generar la colección de embeddings (una sola vez):

   `python populate_autospec.py`

    Resultado esperado: `Colección lista con 3 documentos`

    ![Terminal Colección](../docs/screenshots/fase2/fase2_terminal_collection.png)

3. Levantar la interfaz:

    `streamlit run rag_app.py`

4. Probar con una pregunta real:

    > ¿Cuáles son las especificaciones de seguridad del modelo Alpha?

    ![Respuesta Alpha](../docs/screenshots/fase2/fase2_respuesta_alpha.png)

5. Probar con una pregunta sin respuesta en los datos (validación anti-alucinación):

   > ¿Cuál es la garantía extendida del modelo Alpha?

    Resultado esperado: *"No tengo esa información en las fichas técnicas disponibles."*

    ![Guardrail Alucinación](../docs/screenshots/fase2/fase2_guardrail_alucinacion.png)

## Guardrail anti-alucinación

El prompt instruye explícitamente al modelo a:

- Usar solo el fragmento del modelo de vehículo mencionado en la pregunta, ignorando fragmentos de otros modelos aunque estén en el contexto recuperado.
- Responder con un mensaje fijo cuando la información no esté disponible, en vez de inventar datos.

## Nota técnica

Con solo 3 documentos en la colección, la búsqueda vectorial (`n_results=3`) siempre devuelve los 3 fragmentos completos, sin importar la pregunta; el filtro real de "solo el modelo correcto" lo aplica el LLM al redactar gracias a la instrucción del prompt. Con un corpus más grande, el retrieval mismo traería solo los fragmentos relevantes.