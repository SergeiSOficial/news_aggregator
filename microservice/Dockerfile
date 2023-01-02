FROM continuumio/miniconda3:master

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app

ADD main.py main.py
ADD utils.py utils.py
ADD configs/config.py configs/config.py
ADD user_agents.py user_agents.py
ADD telegram_parser.py telegram_parser.py
ADD rss_parser.py rss_parser.py
ADD site_parser.py site_parser.py

ADD bot.session bot.session
ADD traleeparser.session traleeparser.session
ADD kerryparser.session kerryparser.session

ENTRYPOINT ["python","./main.py"]