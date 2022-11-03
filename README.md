# docs-proxy

App for making certain documents available via a GET request:

- Indiana: make available without API key
    - e.g. `curl -o bill.pdf docs-proxy.openstates.org/in/2015/bills/hb1001/versions/hb1001.02.comh`
    - becomes `https://api.iga.in.gov/2015/bills/hb1001/versions/hb1001.02.comh?format=pdf`
- California: make available with a GET vs. POST
    - e.g. `curl -o bill.pdf "docs-proxy.openstates.org/ca?bill_id=1234tr&version=2"`
    - becomes a POST to the CA website

## Deploy

docker buildx build --tag openstates/doc-proxy:latest --push .

gcloud run deploy --port 8080 --cpu 1 --memory 256Mi \
    --timeout 300s --min-instances 0 --max-instances 100 \
    --concurrency 3 --project <> --image <> --region <> \
    openstates-docs-proxy
