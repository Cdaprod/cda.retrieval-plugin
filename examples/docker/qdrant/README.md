# Running the Retrieval Plugin with Qdrant in Docker Containers

To set up the ChatGPT retrieval plugin with a single instance of a Qdrant vector database, follow these steps:

## Set Environment Variables

Set the following environment variables:

```bash
# Provide your own OpenAI API key in order to start.
export OPENAI_API_KEY="<your_OpenAI_API_key>"
# This is an example of a minimal token generated by https://jwt.io/
export BEARER_TOKEN="<your_bearer_token>"
```

## Run Qdrant and the Retrieval Plugin in Docker Containers

Both Docker containers might be launched with docker-compose:

```bash
docker-compose up -d
```

## Store the Documents

Store an initial batch of documents by calling the `/upsert` endpoint:

```bash
curl -X POST \
  -H "Content-type: application/json" \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  --data-binary '@documents.json' \
  "http://localhost:80/upsert"
```

## Send a Test Query

You can query Qdrant to find relevant document chunks by calling the `/query` endpoint:

```bash
curl -X POST \
  -H "Content-type: application/json" \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  --data-binary '@queries.json' \
  "http://localhost:80/query"
```
