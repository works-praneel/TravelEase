from flask import Flask

app = Flask(__name__)

# This route will handle requests for the root path '/'
# When you hit http://ALB_DNS/flight, the ALB strips '/flight',
# so your app receives a request for '/'
@app.route('/flight')
def home():
    return "Flight Service Root Path Active!"


@app.route('/search')
@app.route('/api/search')
def search():
    return "Flights Found!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
