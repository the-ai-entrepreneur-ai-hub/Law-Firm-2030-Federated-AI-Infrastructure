# Law Firm 2030: AI Document Processing System

This project provides a secure, robust, and automated system for processing legal documents. It leverages modern tools to handle sensitive information, ensuring that client data privacy is maintained at all times.

## Security and Privacy Architecture

The security of this system is its most critical feature. To address client concerns about sending sensitive data to an AI, this architecture is designed to **guarantee that no Personally Identifiable Information (PII) is ever exposed to the generative AI model (LLM).**

We achieve this by using two distinct, separate tools in a specific, secure sequence.

### The Two-Tool Process

1.  **Tool #1: The Automated Redaction Engine (`sanitizer` service)**
    -   **What it is:** A specialized, single-purpose tool that runs 100% locally within its own secure container on your server.
    -   **Technology:** It uses a well-established technique called **Natural Language Processing (NLP)**, similar to a grammar checker, to analyze sentence structure and identify entities like people, locations, and organizations.
    -   **It is NOT a Generative AI:** It cannot write text or have conversations. Its only job is to find and "black out" (redact) personal information. It is not connected to the internet and does not send data to any third party.

2.  **Tool #2: The Generative AI Model (LLM)**
    -   **What it is:** This is the powerful Large Language Model (e.g., Llama 3, Mixtral) that performs complex tasks like drafting, summarizing, and legal analysis.
    -   **The Security Guarantee:** This AI **NEVER** sees the original document. It only receives the safe, fully anonymized text that has already been cleaned by our local Redaction Engine.

### Visual Workflow

The following diagram illustrates the secure data flow, clearly separating the local, secure zone from the AI processing zone.

```mermaid
graph TD
    %% Define Nodes
    doc[📄 Raw Document<br>(Contains Private Client Data)]
    nlp_engine[⚙️ Local NLP Sanitizer]
    pii_map[🤫 Secret PII Map<br>(Never leaves this server)]
    ai_model[🧠 Performs Drafting/Summarizing]
    rehydrate[💧 Restore Original Data<br>(Local process)]
    final_doc[✅ Final, Complete Document<br>(Ready for review)]

    %% Grouping by Subgraphs (local zones)
    subgraph LocalZone[🔒 Your Secure Local Server]
        direction TD
        nlp_engine
        pii_map
        rehydrate
        final_doc
    end

    subgraph AIZone[🤖 The Generative AI (LLM)]
        ai_model
    end

    subgraph Input
        doc
    end

    %% Flow
    doc -->|1. Document enters your secure server| nlp_engine
    nlp_engine -->|2. PII is found and<br>stored in a secret map| pii_map
    nlp_engine -->|3. SAFE, ANONYMOUS text is sent to the AI| ai_model
    ai_model -->|4. Anonymized DRAFT is returned| rehydrate
    pii_map -->|5. Secret map is used to<br>restore original data| rehydrate
    rehydrate -->|6. Final document is created| final_doc

    %% Styling Nodes (cannot style subgraphs)
    style pii_map fill:#e6f7ff,stroke:#0077c2,stroke-width:2px
    style nlp_engine fill:#e6ffed,stroke:#2a7e3c,stroke-width:2px,stroke-dasharray: 5 5
    style rehydrate fill:#e6ffed,stroke:#2a7e3c,stroke-width:2px,stroke-dasharray: 5 5
    style final_doc fill:#e6ffed,stroke:#2a7e3c,stroke-width:2px,stroke-dasharray: 5 5
    style ai_model fill:#fff0e6,stroke:#d95f02,stroke-width:2px

    %% Emphasized Arrows
    linkStyle 2 stroke:green,stroke-width:4px
    linkStyle 3 stroke:red,stroke-width:2px,stroke-dasharray: 5 5

```

---

## System Setup Instructions

### Prerequisites

- **Docker Desktop**: You must have Docker Desktop installed and running on your system (Windows, Mac, or Linux).

### Step 1: Create the Project Structure

1.  Open your terminal or command prompt.

2.  Create a project directory and navigate into it:
    ```bash
    mkdir law-firm-ai
    cd law-firm-ai
    ```

3.  Inside the `law-firm-ai` folder, create the four required empty files:

    **On Mac or Linux:**
    ```bash
    touch docker-compose.yml Dockerfile requirements.txt sanitizer_app.py
    ```

    **On Windows:**
    ```bash
    type nul > docker-compose.yml
    type nul > Dockerfile
    type nul > requirements.txt
    type nul > sanitizer_app.py
    ```

### Step 2: Configure the Sanitizer Service

1.  **`sanitizer_app.py`**: Open this file and paste the following Python code for the local Redaction Engine.

    ```python
    # In file: sanitizer_app.py
    import spacy
    from flask import Flask, request, jsonify

    try:
        nlp = spacy.load("de_core_news_sm")
    except OSError:
        print("Downloading 'de_core_news_sm' model...")
        spacy.cli.download("de_core_news_sm")
        nlp = spacy.load("de_core_news_sm")

    PII_LABELS = ["PER", "LOC", "ORG"]
    app = Flask(__name__)

    @app.route('/sanitize', methods=['POST'])
    def sanitize_text():
        if not request.is_json: return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()
        if 'text' not in data: return jsonify({"error": "Missing 'text' key in request"}), 400

        raw_text = data['text']
        doc = nlp(raw_text)
        sanitized_text = raw_text
        pii_map = {}
        placeholder_index = 1

        for ent in reversed(doc.ents):
            if ent.label_ in PII_LABELS:
                placeholder = f"[{ent.label_}_{placeholder_index}]"
                placeholder_index += 1
                pii_map[placeholder] = ent.text
                sanitized_text = sanitized_text[:ent.start_char] + placeholder + sanitized_text[ent.end_char:]
                
        return jsonify({"sanitizedText": sanitized_text, "piiMap": pii_map})

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001)
    ```

2.  **`requirements.txt`**: Open this file and add the required Python libraries.

    ```txt
    # In file: requirements.txt
    flask
    spacy==3.7.2
    ```

3.  **`Dockerfile`**: Open this file and paste the build instructions for the Redaction Engine's Docker image.

    ```Dockerfile
    # In file: Dockerfile
    FROM python:3.10-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY sanitizer_app.py .
    EXPOSE 5001
    CMD ["python", "sanitizer_app.py"]
    ```

### Step 3: Configure Docker Compose

The `docker-compose.yml` file orchestrates both the `sanitizer` service and the `n8n` service.

1.  Open `docker-compose.yml` and paste the following configuration:

    ```yaml
    # In file: docker-compose.yml
    version: '3.8'

    services:
      sanitizer:
        build: .
        container_name: pii_sanitizer_service
        restart: unless-stopped

      n8n:
        image: n8nio/n8n
        container_name: n8n_workflow_engine
        restart: unless-stopped
        ports:
          - "5678:5678"
        volumes:
          - n8n_data:/home/node/.n8n
        environment:
          - TZ=Europe/Berlin
        depends_on:
          - sanitizer

    volumes:
      n8n_data:
    ```

### Step 4: Build and Run the Application

1.  Ensure you are in the `law-firm-ai` directory in your terminal.

2.  Execute the following command to build and launch the system:
    ```bash
    docker-compose up --build -d
    ```

### Step 5: Final Setup and Verification

1.  **Set Up n8n Owner Account**:
    - Open your web browser and navigate to `http://localhost:5678`.
    - Complete the on-screen form to create your owner account. This is a mandatory one-time step.

2.  **Test the End-to-End Connection**:
    - In the n8n canvas, create a new workflow and add an **HTTP Request** node.
    - Configure it to test the `sanitizer` service:
        - **Method**: `POST`
        - **URL**: `http://sanitizer:5001/sanitize`
        - **Body Content Type**: `JSON`
        - **Body**:
          ```json
          {
            "text": "Ein Brief von Stefanie Jordan aus Tostedt."
          }
          ```
    - Execute the node and verify you receive a successful JSON response with the redacted text.

### Managing Your Application

- **Check container status**: `docker-compose ps`
- **View logs for a service**: `docker-compose logs sanitizer`
- **Stop and remove all containers**: `docker-compose down`