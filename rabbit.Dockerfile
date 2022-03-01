FROM rabbitmq

# for pdf2image
RUN apt-get update && apt-get -y install poppler-utils poppler-data
