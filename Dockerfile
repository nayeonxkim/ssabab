FROM python:3

WORKDIR /usr/src
RUN apt-get -y update
RUN apt install wget
RUN apt install unzip  
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -y install ./google-chrome-stable_current_amd64.deb
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/` curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN mkdir chrome
RUN unzip /tmp/chromedriver.zip chromedriver -d /opt/chrome/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY Happiness-Sans-Bold.ttf /var/task/
COPY .env /var/task/
COPY main.py /var/task/
WORKDIR /var/task

CMD [ "python", "main.py" ]

# docker build --platform linux/x86_64 -t "이미지명" -f Dockerfile .

# aws configure
# export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
# echo "export ACCOUNT_ID=${ACCOUNT_ID}" | tee -a ~/.bash_profile

# docker tag "이미지명" $ACCOUNT_ID.dkr.ecr."리전명".amazonaws.com/"리포지토리 이름"
# aws ecr get-login-password --region "리전명" | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr."리전명".amazonaws.com
# docker push $ACCOUNT_ID.dkr.ecr."리전명".amazonaws.com/"리포지토리 이름"
