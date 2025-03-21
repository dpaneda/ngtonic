FROM python:3.13

RUN pip install -U pdm
ENV PDM_CHECK_UPDATE=false
COPY pyproject.toml pdm.lock README.md /app/
COPY src/ /app/src
WORKDIR /app
RUN pdm install --check --prod --no-editable
CMD ["ngtonic"]
