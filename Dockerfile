# set base image (host OS)
FROM python:3.7

# copy the dependencies file to the working directory
COPY ./ .

# install dependencies
RUN pip install -r requirements.txt

# set envrionment
ENV PYTHONUNBUFFERED=1
ENV YOUTUBE_API_KEY=AIzaSyBgvr1hWhfeaWcmMXlbztqoP0UGzBpAsoo
ENV AWS_ACCESS_KEY_ID=AKIA3MY774HHIYC2GDXX
ENV AWS_SECRET_ACCESS_KEY=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

EXPOSE 9000

# command to run on container start
ENTRYPOINT [ "python", "./manager.py", "run"]