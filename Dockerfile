FROM python:3.6-slim
WORKDIR /quiz_app
ADD . /quiz_app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 80 
ENV SECRET_KEY extremely_secure_secret
CMD ["python", "main.py"] 

