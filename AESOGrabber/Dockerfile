FROM python:3.10

RUN pip3 install --no-cache-dir --upgrade pip &&\
    adduser --system worker

USER worker
WORKDIR /home/worker

COPY --chown=worker:worker . .

RUN pip3 install --no-cache-dir --user -r requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"

ENTRYPOINT [ "python", "AESOGrabber.py" ]
