#!/bin/bash
curl -X 'POST' \
  'http://localhost:8000/api/search/query/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query_text": "Sample search query",
  "top_n": 3,
  "score_threshold": 0.5
}'
