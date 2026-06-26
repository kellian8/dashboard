FROM anaconda/miniconda:latest
WORKDIR /usr/home/app

COPY ./dash/ ./dash/
COPY ./utils/ ./utils/
COPY ./__main__.py ./__main__.py
COPY ./environment.yml ./environment.yml
COPY ./logging.yml ./logging.yml
COPY ./readme.md ./readme.md

# Accept ToS via environment variable, create environment, and set it as default
ENV CONDA_PLUGINS_AUTO_ACCEPT_TOS=true
RUN conda env create -f environment.yml && \
    conda config --set default_activation_env dash-env

RUN useradd app
USER app

CMD ["python", "./"]
