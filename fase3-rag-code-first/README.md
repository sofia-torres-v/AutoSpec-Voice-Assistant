# Fase 3 - RAG "Code-First" con LangChain

⬅️ [Volver al README principal](../README.md)

## Estado: ✅ Completada

Reconstrucción del pipeline RAG completo en código con LangChain, usando Google Gemini tanto para embeddings como para generación, con logging de conversaciones en SQLite.

## Por qué Gemini en vez de Bedrock/Titan

El diseño original contemplaba Titan/Bedrock para los embeddings, igual que en Fase 2. Para esta fase se usó Gemini de punta a punta para demostrar en la práctica el objetivo central: portabilidad multi-cloud. Gracias a que LangChain abstrae tanto los embeddings (`Embeddings`) como los modelos de chat (`BaseChatModel`) detrás de interfaces comunes, este mismo pipeline podría apuntar a Titan/Bedrock cambiando solo 2 líneas en `rag_chain.py`, sin tocar el resto del código.

## Archivos

- `ingest.py` — fragmenta los documentos, genera embeddings con Gemini y los guarda en Chroma.
- `rag_chain.py` — cadena RAG completa con LangChain (retriever + prompt + LLM), más logging en SQLite.
- `app.py` — interfaz de chat con Streamlit.

## Cómo probarlo

1. Instalar dependencias:

```bash
   pip install -r requirements.txt
```

2. Generar la colección de embeddings (una sola vez):

```bash
   export GEMINI_API_KEY="clave-real"
   python ingest.py
```

Resultado esperado: `Colección lista con N fragmentos`

3. Levantar la interfaz:

```bash
   streamlit run app.py
```

4. Probar con una pregunta real:

   > ¿Cuáles son las especificaciones de seguridad del modelo Alpha?

5. Probar con una pregunta sin respuesta en los datos (validación anti-alucinación):

   > ¿Cuál es la garantía extendida del modelo Alpha?

   Resultado esperado: _"No tengo esa información en las fichas técnicas disponibles."_

6. Verificar el logging en SQLite:

```bash
   python -c "
   import sqlite3
   conn = sqlite3.connect('conversation_logs.db')
   for row in conn.execute('SELECT timestamp, question, answer FROM conversation_logs'):
       print(row)
   "
```

## Evidencia

**1. Ingesta completada:**

![Terminal Colección](../docs/screenshots/fase3/fase3_terminal_collection.png)

**2. Pregunta real (modelo Alpha):**

![Respuesta Alpha](../docs/screenshots/fase3/fase3_respuesta_alpha.png)

**3. Pregunta sin respuesta en los datos (guardrail anti-alucinación):**

![Guardrail Alucinación](../docs/screenshots/fase3/fase3_guardrail_alucinacion.png)

**4. Verificación del logging en SQLite:**

![Logs de SQLite](../docs/screenshots/fase3/fase3_respuesta_sqlite.png)

## Guardrail anti-alucinación

El mismo prompt de Fase 2 (usar solo el fragmento del modelo mencionado, responder con mensaje fijo si no hay información) se reutilizó tal cual en `rag_chain.py`, dentro de un `ChatPromptTemplate` de LangChain.

## Comparación con Fase 2

|                     | Fase 2                                          | Fase 3                                  |
| ------------------- | ----------------------------------------------- | --------------------------------------- |
| Orquestación        | Llamadas manuales (`boto3`, `chromadb` directo) | Cadena declarativa con LangChain (LCEL) |
| Cambio de proveedor | Reescribir función con `if/else`                | Cambiar 2 líneas de configuración       |
| Embeddings          | Titan (AWS)                                     | Gemini                                  |
| Generación          | Nova Lite (AWS)                                 | Gemini                                  |
