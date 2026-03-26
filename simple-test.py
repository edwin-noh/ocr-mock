from typhoon_ocr import ocr_document

markdown = ocr_document("Marriage Cert.pdf", base_url="http://localhost:11434/v1", api_key="ollama", model='scb10x/typhoon-ocr1.5-3b')
print(markdown)
