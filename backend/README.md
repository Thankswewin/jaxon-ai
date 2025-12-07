# Jaxon AI

Jaxon is an AI chatbot with long-term memory, powered by [Mem0](https://mem0.ai/) and OpenAI. It uses your ChatGPT conversation history as its knowledge base.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Keys**:
    - Edit `.env` and add your `MEM0_API_KEY` and `OPENAI_API_KEY`.

3.  **Ingest Data**:
    - Place your `conversations.json` in the project root.
    - Run the ingestion script:
    ```bash
    python ingest.py
    ```
    - This will parse your chat history and store it in Mem0.

## Usage

Run the Jaxon chatbot:
```bash
python jaxon.py
```

Type your questions and Jaxon will answer using context from your past conversations.
Type `exit` or `quit` to stop.
