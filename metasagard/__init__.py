import datetime

import MetaTrader5 as mt5
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
# Set up Swagger documentation
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'MetaTrader5 API'
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
CORS(app)

# Load data from MetaTrader
login = 00000000
password = "password"
server = "Broker"
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M1
start_date = datetime.datetime(2020, 2, 5, 9)
end_date = datetime.datetime(2020, 2, 14, 13)


class Logger:
    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def error(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ERROR: {message}")


class Application:

    def __int__(self, logger: Logger):
        self.logger = logger
        self.logger.log("APPLICATION INITIATION")
        # connect to MetaTrader 5
        if not mt5.initialize():
            self.logger.error("initialize() failed")
            mt5.shutdown()
            exit(1)

        # login to MetaTrader 5
        if not mt5.login(login, password, server):
            self.logger.error("login() failed")
            mt5.shutdown()
            exit(1)
        self.logger.log("SUCCESFULLY INITIALIZED AND LOGGED IN TO MT5")

    def __del__(self):
        mt5.shutdown()

    def getAccountInfo(self):

        account = mt5.account_info()
        self.logger.log("READING ACCOUNT;")
        self.logger.log(account)
        account_dict = {
            'login': account.login,
            'currency': account.currency,
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'margin_free': account.margin_free,
            'margin_level': account.margin_level,
            'margin_so_call': account.margin_so_call,
            'margin_so_mode': account.margin_so_mode
        }
        self.logger.log("RETURNING ACCOUNT")
        self.logger.log(account_dict)
        return jsonify(account_dict)

    def getPositions(self):
        self.logger.log("READING POSITIONS")
        # Get all open positions
        positions = mt5.positions_get()
        self.logger.log(positions)

        # Convert positions to a list of dictionaries
        positions_list = [position._asdict() for position in positions]
        self.logger.log("RETURNING POSITIONS")
        self.logger.log(positions_list)
        # Return positions as a JSON response
        return jsonify(positions_list)

    def getDealsHistory(self, start_time, end_time):
        self.logger.log("READING DEALS HISTORY")
        # Define time range
        from_date = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        to_date = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

        # Get order history within time range
        orders = mt5.history_deals_get(from_date, to_date)
        self.logger.log(orders)
        # Convert orders to a list of dictionaries
        deals_list = [order._asdict() for order in orders]
        self.logger.log(deals_list)
        # Return orders as a JSON response
        return jsonify(deals_list)
    def getOrdersFrom(self, start_time, end_time):
        self.logger.log("READING ORDER HISTORY")
        # Define time range
        from_date = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        to_date = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

        # Get order history within time range
        orders = mt5.history_orders_get(from_date, to_date)
        self.logger.log(orders)
        # Convert orders to a list of dictionaries
        orders_list = [order._asdict() for order in orders]
        self.logger.log(orders_list)
        # Return orders as a JSON response
        return jsonify(orders_list)

    def getNet(self, start_time, end_time):
        # Define time range
        from_date = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        to_date = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

        total = mt5.history_orders_total(from_date,to_date)
        return jsonify(total)


logger = Logger()
application = Application()


@app.route('/info', methods=['GET'])
def info():
    message = "is Alive"
    logger.log(message)
    return message


@app.route('/mt/get-account', methods=['GET'])
def getAccount():
    message = application.getAccountInfo()
    logger.log(message)

    return message

@app.route('/mt/get-positions', methods=['GET'])
def getPositions():
    message = application.getPositions()
    logger.log(message)
    return message
@app.route('/mt/get-total-from', methods=['POST'])
def getTotal():
    start = request.json['start']
    end = request.json['end']
    logger.log(start)
    logger.log(end)

    orders = application.getNet(start, end)
    logger.log("GET TOTAL")
    logger.log(orders)
    return orders

@app.route('/hello')
def hello():
    """
    A simple hello world endpoint.

    ---
    responses:
      200:
        description: A simple JSON response.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Hello, world!"
    """
    return jsonify({'message': 'Hello, world!'})

@app.route('/mt/get-deals-from', methods=['POST'])
def getDealsFrom():
    start = request.json['start']
    end = request.json['end']
    logger.log(start)
    logger.log(end)

    deals = application.getDealsHistory(start, end)
    logger.log("GET DEALS")
    logger.log(deals)
    return deals

@app.route('/mt/get-orders-from', methods=['POST'])
def getOrdersFrom():
    start = request.json['start']
    end = request.json['end']
    logger.log(start)
    logger.log(end)

    orders = application.getOrdersFrom(start, end)
    logger.log("GET ORDERS")
    logger.log(orders)
    return orders


if __name__ == '__main__':
    print("Application Init started...")
    try:
        Application.__int__(application, logger=logger)
    except KeyboardInterrupt:
        pass
    app.run(debug=True, port=5025, host="0.0.0.0")
