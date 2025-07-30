FROM python:3.9-slim
WORKDIR /Payment_Service_App
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5003
CMD ["python", "Payment_Service_App.py"]