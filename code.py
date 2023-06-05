import requests
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from binance.client import Client
from flask import Flask, render_template, jsonify
import webbrowser
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__)

api_key = 's1uXhhwpGNDbhipIZnaOAKnzQYAjRM1sxMXcDPtO7vhSfR4cl7Ds56ssUaPgs8Yk'
api_secret = 'Y3gR9R36dtBv3HCQiI0XHHCDw6fvATalRYxjl0Yl79822XkbUvp1kYNWUBDOtCIS'

client = Client(api_key, api_secret, tld='us')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/crypto_data')
def get_crypto_data():

    symbol = 'BTCUSDT'
    ticker = client.get_ticker(symbol=symbol)

    if ticker:
        close_price = ticker['lastPrice']
        volume = ticker['volume']
        price_change = ticker['priceChange']

        # use another method to get market cap since binance does not provide
        coin_id = 'bitcoin'
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            market_cap = data['market_data']['market_cap']['usd']

            klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
            price_history = [float(kline[4]) for kline in klines]  # Closing prices of the past 24 hours
            volatility = np.std(price_history)

            # plot 24hr price history
            plt.plot(price_history)
            plt.xlabel('Hour')
            plt.ylabel('Price')
            plt.title('BTCUSDT 24-Hour Price History')
            plt.grid(True)

            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)

            # convert image to base64 string
            img_string = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

            plt.clf()

            return jsonify({
                'symbol': symbol,
                'close_price': close_price,
                'volume': volume,
                'price_change': price_change,
                'volatility': volatility,
                'market_cap': market_cap,
                'plot_image': img_string
            })
        else:
            return jsonify({'error': f'Failed to fetch market cap for {symbol}'})
    else:
        return jsonify({'error': f'Failed to fetch data for {symbol}'})


if __name__ == '__main__':
    url = 'http://127.0.0.1:5000'  # publish to a live url
    webbrowser.open(url)
    app.run()

