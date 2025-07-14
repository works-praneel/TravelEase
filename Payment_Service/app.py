from flask import Flask
app = Flask(__name__)

@app.route('/ping')
def ping():
    return "Payment Service Active"

@app.route('/pay')
def pay():
    return "Payment Processed!"

if __name__ == '_main_':
    app.run(host='0.0.0.0', port=5001)