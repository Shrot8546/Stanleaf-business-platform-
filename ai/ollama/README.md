# Stanleaf Local AI Layer (Ollama & NLP)

Houses local LLM integration and prompt orchestration (using Ollama and Hugging Face Transformers).

## Architecture

- **Ollama**: Self-hosted local inference engine for privacy-preserving business data analysis.
- **Model Target**: Llama 3.1 / Mistral / Qwen for generating qualitative risk narratives and recommendations based on the quantitative scores produced by the Data Engine.

## Local Running (Docker template)

Run the included `docker-compose.ollama.yml` when ready:
```bash
docker compose -f ai/ollama/docker-compose.ollama.yml up -d
docker exec -it stanleaf-ollama ollama pull llama3.1
```
