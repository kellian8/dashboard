FROM conda/miniconda3:latest
WORKDIR /usr/home/app

COPY ./dash/ ./dash/
COPY ./__main__.py ./__main__.py
COPY ./environment.yml ./environment.yml
COPY ./logging.yml ./logging.yml
COPY ./readme.md ./readme.md

RUN conda env create -f environment.yml

RUN useradd app
USER app

CMD ["python", "./"]
