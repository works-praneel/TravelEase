FROM python:3.9-slim
WORKDIR /Flight_Service_App
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5002
CMD ["python", "Flight_Service_App.py"]

