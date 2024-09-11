#!/bin/bash
curl -X 'POST' \
  'http://localhost:8000/api/embedding/embed/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "content": "This is a sample text for embedding."
}'
