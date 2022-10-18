# docs-proxy

App for making certain documents available via a GET request:

- Indiana: make available without API key
- California: make available with a GET vs. POST

## Deploy

docker buildx build --tag openstates/doc-proxy:latest --load .

docker push openstates/doc-proxy:latest

gcloud run deploy --port 8080 --cpu 1 --memory 256Mi \
    --timeout 300s --min-instances 0 --max-instances 100 \
    --concurrency 3 --project <> --image <> --region <> \
    openstates-docs-proxy
