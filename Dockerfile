FROM python:alpine3.10
WORKDIR /app 
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5001
CMD python ./Manufacture_controller_5001.py
#COPY requirements.txt /app/requirements.txt
#ENTRYPOINT ["python", "./Manufacture_controller_5001.py"]
