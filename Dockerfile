FROM python:3.9 AS build

WORKDIR /app

# Installing taipy and it's dependencies. Should be replace by a pip install
# after publishing to pypi
COPY Pipfile .
RUN pip install --upgrade pipenv
RUN pipenv install --dev --skip-lock

COPY ./ /app/install
WORKDIR /app/install

RUN python setup.py install
WORKDIR /app

RUN rm Pipfile
RUN rm -fr /app/install

CMD ["bash"]

FROM build as worker

COPY taipy/task/scheduler/executor/remote_pool_worker.py /worker.py
CMD ["python", "/worker.py"]
