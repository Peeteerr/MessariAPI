import json5
import requests
import ujson
from messari.messari import Messari
import pandas as pd
from pandas.io.json import to_json
from messari.defillama import DeFiLlama, format_df, time_filter_df
import time

#Could choose to integrate defillama for TVL tracking
dl = DeFiLlama()

##########
# You NEED to input your Messari Key here
##########
messari = Messari('YOUR MESSAR KEY')

#Input all the project slugs you want to look at here. Ex:
slugs = ['axie-infinity','decentraland','illuvium',
              'thesandbox','yield-guild-games','enjincoin',
              'gala','immutable-x','alien-worlds','league-of-kingdoms'
]

#All the metrics to get timeseries data of. Ex:
metrics = ['mcap.circ','sply.circ','mcap.dom','new.iss.ntv','real.vol','reddit.subscribers','reddit.active.users']
            # mcap.circ            = cirulating market cap, 
            # sply.circ            = circulating supply, market cap dominance, # of reddit subs, # of active subreddit users
            # mcap.dom             = market cap dominance, # of reddit subs, # of active subreddit users
            # new.iss.ntv          = Sum of new native units issued that interval by a protocol-mandated continuous emission schedule
            # real.vol             = the total volume on the exchanges that Messari believes are free of wash trading activities
            # reddit.subscribers   = # of reddit subs
            # reddit.active.users  = # of active subreddit users within 48hrs of date
            ##########
            #for more, see:
            #https://github.com/messari/messari-python-api/blob/master/examples/notebooks/Messari%20API%20Tutorial.ipynb
            ##########

#Start and end of timeseries, inout dates in "year/month/day" format
start = '2020-11-10'
end = '2022-07-01'

#base URL for querying and checking data presence
BASE_URL = "https://data.messari.io"

#Initialize the object
def __init__(self, key=None):
    """
    :param key: API key
    """
    self.key = key
    self.session = requests.Session()
    if self.key:
        self.session.headers.update({'x-messari-api-key': key})

#Send API request
def _send_message(method, endpoint, params=None, data=None):
    """
    :param method: HTTP method (get, post, delete, etc.)
    :param endpoint: Endpoint (to be added to base URL)
    :param params: HTTP request parameters
    :param data: JSON-encoded string payload for POST
    :return: dict/list: JSON response
    """
    url = BASE_URL + endpoint
    response = messari.session.request(method, url, params=params, data=data, timeout=30)
    return response.json()

#Get API request
def _get(endpoint, params=None):
    """
    :param endpoint: Endpoint (to be added to base URL)
    :param params: HTTP request parameters
    :return:
    """
    return _send_message('GET', endpoint, params=params)

#check whether metric data is available for a given asset
def check_url(asset_key,metric_id):
    path = '/api/v1/assets/{}/metrics/{}/time-series?interval=1w&start=2020-11-10&end=2022-07-01'.format(asset_key, metric_id)
    list = str(_get(path))
    return ('404' in list) #error code if data isn't available

#get all the weekly timeseries data for a given project; if you want daily, replace '1w' with '1d'
def get_all_metrics2(slug):
  
    #use the first metric for a given slug and create a pandas dataframe to add subsequent metric dataframes to.
    df1 = messari.get_metric_timeseries(asset_slugs=slug, asset_metric=metrics[0],
                                        start=start, end=end,interval='1w')
    df1 = pd.DataFrame.from_dict(df1)
    list = [metrics[0]]
    
    #loop to query all metrics for a given slug and combine them into one dataset
    for metric in metrics[1:]:
        if check_url(slug,metric):
            print('Metric Data Unavailable')
        else:
            df2 = messari.get_metric_timeseries(asset_slugs=slug, asset_metric=metric, start=start, end=end,
                                                    interval='1w')
            df2 = pd.DataFrame.from_dict(df2)
            df1 = pd.concat((df1,df2) , axis =1)
            list.append(metric)
        time.sleep(3) #need to delay loop so you don't overload Messari with requests
    
    df1.columns = list #rename columns to their metric names
    return df1 #return the complete pandas dataframe with all metrics for a given project


##########
# Fetch data for a projects and print to an excel sheets >> use this format for whatever projects you want to look at. Ex:
##########

axie = get_all_metrics2(slugs[0])
axie.to_excel(('M1-axie.xlsx'), sheet_name=('axie'))
time.sleep(30) #need to sleep for 30 seconds after each call so you don't overload Messari with requests

# decentraland = get_all_metrics2(slugs[1])
# decentraland.to_excel(('M-decentraland.xlsx'), sheet_name=('decentraland'))
# time.sleep(30)
