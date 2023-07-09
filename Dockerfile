FROM python:3.9

WORKDIR /app

RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

RUN apt install wget
RUN apt install unzip

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb RUN apt -y install ./google-chrome-stable_current_amd64.deb
RUN apt -y install ./google-chrome-stable_current_amd64.deb
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/ curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE /chromedriver_linux64.zip
RUN mkdir chrome
RUN unzip /tmp/chromedriver.zip chromedriver -d /app/chrome

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
