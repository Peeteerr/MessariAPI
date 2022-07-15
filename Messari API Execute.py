import json5
import requests
import ujson
from messari.messari import Messari
import pandas as pd
from pandas.io.json import to_json
from messari.defillama import DeFiLlama, format_df, time_filter_df
import time

dl = DeFiLlama()

##########
# You NEED to input your Messari Key here
##########
messari = Messari('1b3f4551-8512-4b3b-8c71-b6ff634a1bf7')

#Input all the project slugs you want to look at here
game_slugs = ['axie-infinity','decentraland','illuvium',
              'thesandbox','yield-guild-games','enjincoin',
              'gala','immutable-x','alien-worlds','league-of-kingdoms'
]

#All the metrics to get timeseries data of
metrics = ['mcap.circ','sply.circ','mcap.dom','new.iss.ntv','real.vol','reddit.subscribers','reddit.active.users']
            #cirulating market cap, circulating supply, market cap dominance, # of reddit subs, # of active subreddit users
            #new.iss.ntv = Sum of new native units issued that interval by a protocol-mandated continuous emission schedule
            #real.vol = the total volume on the exchanges that Messari believes are free of wash trading activities
##########
#for more, see:
#https://github.com/messari/messari-python-api/blob/master/examples/notebooks/Messari%20API%20Tutorial.ipynb
##########

#Start and end of timeseries
start = '2020-11-10'
end = '2022-07-01'

#base URL for querying and checking data presence
BASE_URL = "https://data.messari.io"

def __init__(self, key=None):
    """
    Initialize the object
    :param key: API key
    """
    self.key = key
    self.session = requests.Session()
    if self.key:
        self.session.headers.update({'x-messari-api-key': key})

def _send_message(method, endpoint, params=None, data=None):
    """
    Send API request.
    :param method: HTTP method (get, post, delete, etc.)
    :param endpoint: Endpoint (to be added to base URL)
    :param params: HTTP request parameters
    :param data: JSON-encoded string payload for POST
    :return: dict/list: JSON response
    """
    url = BASE_URL + endpoint
    response = messari.session.request(method, url, params=params, data=data, timeout=30)
    return response.json()

def _get(endpoint, params=None):
    """
    Get API request
    :param endpoint: Endpoint (to be added to base URL)
    :param params: HTTP request parameters
    :return:
    """
    return _send_message('GET', endpoint, params=params)

#checks whether metric data is available for a given asset
def check_url(asset_key,metric_id):
    path = '/api/v1/assets/{}/metrics/{}/time-series?interval=1w&start=2020-11-10&end=2022-07-01'.format(asset_key, metric_id)
    list = str(_get(path))
    return ('404' in list)

#get all the weekly timeseries data for a given project
###if you want daily, replace '1w' with '1d'
def get_all_metrics2(slug):
    df1 = messari.get_metric_timeseries(asset_slugs=slug, asset_metric=metrics[0],
                                        start=start, end=end,interval='1w')
    df1 = pd.DataFrame.from_dict(df1)

    list = [metrics[0]]

    for metric in metrics[1:]:
        if check_url(slug,metric):
            print('Metric Data Unavailable')
        else:
            df2 = messari.get_metric_timeseries(asset_slugs=slug, asset_metric=metric, start=start, end=end,
                                                    interval='1w')
            df2 = pd.DataFrame.from_dict(df2)
            df1 = pd.concat((df1,df2) , axis =1)
            list.append(metric)
        time.sleep(3)

    #rename columns to their metric names
    df1.columns = list

    return df1

##########
# Fetch data for projects and print to different excel sheets >> use this format for whatever projects you want to look at
##########

# axie = get_all_metrics2(game_slugs[0])
# axie.to_excel(('M1-axie.xlsx'), sheet_name=('axie'))
# # time.sleep(30)

# decentraland = get_all_metrics2(game_slugs[1])
# decentraland.to_excel(('M-decentraland.xlsx'), sheet_name=('decentraland'))
# time.sleep(30)
