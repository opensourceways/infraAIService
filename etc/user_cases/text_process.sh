curl -X 'POST' \
  'http://localhost:8000/api/text/process/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "content": "Hello, world! This is a test@example.com with some [special] {characters} to remove."
}'
