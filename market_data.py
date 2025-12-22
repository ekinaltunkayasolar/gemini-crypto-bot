from binance.client import Client
import pandas as pd

def get_historical_data(symbol, interval, lookback):
    client = Client()
    klines = client.get_historical_klines(symbol, interval, lookback)
    
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
    ])
    
    # Sayısal çevirme
    cols = ['open', 'high', 'low', 'close', 'volume']
    df[cols] = df[cols].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    return df
