# Approach
- Use model Typhoon OCR (VLM)
    - VLM based lightweight model
    - Support Thai
    - Support pdf, png
    - Layout, handwriting recognize
    https://opentyphoon.ai/blog/en/typhoon-ocr-release
- Use ollama image for model runtime
    - CPU only support
    - Typhoon officially support 
- Expose API for text extracting
- Add function 

# Mocking Implementation

## 1. Ollama + Typhoon Image

## Dockerfile
``` bash
cat > ollama-ocr-Dockerfile <<EOF
FROM ollama/ollama:latest

# default path of model store
ENV OLLAMA_MODELS=/root/.ollama/models

# Use Typhoon official ollama mode
RUN nohup bash -c "ollama serve &" && \
    sleep 5 && \
    ollama pull scb10x/typhoon-ocr1.5-3b && \
    pkill ollama

ENTRYPOINT ["ollama", "serve"]
EOF
```
## Build image
``` bash
export IMAGE_TAG="quay.io/gunoh/edwin/typhoon-ocr-ollama:1.5-3b"

# x86
podman build --platform linux/amd64 -t $IMAGE_TAG -f ./ollama-ocr-Dockerfile

podman login -u $(oc whoami) -p $(oc whoami -t) $(oc registry info)
podman push $IMAGE_TAG
```

## Test Image

```
podman run -d --name typhoon-test -p 11434:11434 typhoon-ollama:latest
podman logs -f typhoon-test
podman exec -it typhoon-test ollama list
podman exec -it typhoon-test ollama run scb10x/typhoon-ocr1.5-3b "안녕, 너는 누구니?"
podman stop typhoon-test
podman rm typhoon-test
```




# Inferencing OCR

## Dev Env
```
uv init
uv add fastapi uvicorn python-multipart


```

## Test in local
```
uv run uvicorn src.ocr-mocking.main:app --reload --port 8000

curl -X POST http://localhost:8000/ocr \
  -F "file=@Marriage Cert.pdf" \
  -F "file_id=doc-001" \
  -F "file_type=pdf" \
  -F "document_type=certificate"
```