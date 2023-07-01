FROM python:3.11-slim
COPY ./ /app
WORKDIR /app
# Install python requirements

RUN pip install --upgrade pip
RUN pip install nativeAPI_wheel/intersystems_irispython-3.2.0-py3-none-any.whl
RUN pip  install flask
RUN pip install cryptography
RUN pip install python-dotenv
RUN pip install flask-login
RUN pip install flask-bcrypt
RUN pip install flask-cors
RUN pip install dnspython
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]