FROM python:slim

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app

ADD main.py main.py
ADD utils.py utils.py
ADD config.py config.py
ADD user_agents.py user_agents.py
ADD telegram_parser.py telegram_parser.py
ADD rss_parser.py rss_parser.py
ADD bcs_parser.py bcs_parser.py

ADD bot.session bot.session
ADD Traleetoday.session Traleetoday.session

ENTRYPOINT ["python","./main.py"]