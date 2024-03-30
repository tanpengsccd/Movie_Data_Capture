import ddddocr

ocr = ddddocr.DdddOcr()

with open("./MDC/OtherScript/download1.gif", 'rb') as f:
    image = f.read()

res = ocr.classification(image)
print(res)
