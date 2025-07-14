from flask import Flask
app = Flask(__name__)

@app.route('/ping')
def ping():
    return "Booking Service Active"

@app.route('/book')
def book():
    return "Booking Confirmed!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)