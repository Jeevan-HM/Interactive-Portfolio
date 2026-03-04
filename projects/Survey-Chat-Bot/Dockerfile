FROM python

WORKDIR /app

COPY requirements.txt /app 

RUN pip3 install -r requirements.txt

COPY . /app 

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]