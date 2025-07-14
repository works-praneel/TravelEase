from flask import Flask
app = Flask(__name__)

@app.route('/ping')
def ping():
    return "Flight Service Active"

@app.route('/search')
def search():
    return "Flights Found!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
