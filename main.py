import random
import tweepy
from urllib.error import HTTPError
import requests
import json
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os, sys
import asyncio

from gann_prototype import GetCandlesticks, GannLines, DisplayChart
from predict import combine_predictions

load_dotenv()

#Get Dictionary Path
PATH = sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#Load Environmental Variables
t_API_KEY = os.getenv('t_API_KEY')
t_API_SECRET = os.getenv('t_API_SECRET')
Bearer_Token = os.getenv('Bearer_Token')
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')

# Your app's API/consumer key and secret can be found under the Consumer Keys
# section of the Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')

# Your account's (the app owner's account's) access token and secret for your
# app can be found under the Authentication Tokens section of the
# Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')

def prediction():
    new_line = """

"""
    #Load options.json file
    with open("tweets.json", "r") as read_file:
        options = json.load(read_file)

    rdm_1 = random.randint(0,11)

    rdm_2 = random.randint(3,4)

    #Get markets
    market = options['markets'][rdm_1][str(rdm_1)]

    #Get token
    token = options['markets'][rdm_1]['value']

    #Get Name of token for tweet
    name = options['markets'][rdm_1]['name']

    combine_predictions(market)

    status = options['predict_status']['1'] + token + options['predict_status']['2'] + new_line + name + options['predict_status'][str(rdm_2)] + new_line + options['intraday_trading']['12']

    return status


def build_marketing_text():

    new_line = """

"""

    #Load options.json file
    with open("tweets.json", "r") as read_file:
        options = json.load(read_file)

    rdm_1 = random.randint(3, 6)
    rdm_2 = random.randint(1, 3)
    rdm_tag = random.randint(1,3)

    status = options['marketing'][str(rdm_1)] + new_line + options['marketing']["1"] + new_line + options['marketing']["2"] + new_line + options['marketing_tags'][str(rdm_tag)]

    return status

def choose_marketing_png():

    text = str(random.randint(1,12)) + ".png"

    return text

def build_gann():

    #Load options.json file
    with open("tweets.json", "r") as read_file:
        options = json.load(read_file)

    rdm_1 = random.randint(0,1)

    #Get markets
    market = options['markets'][rdm_1][str(rdm_1)]

    #Get token
    token = options['markets'][rdm_1]['value']

    #Get Name of token for tweet
    name = options['markets'][rdm_1]['name']

    #Get candles for gann algorithm
    candles = GetCandlesticks(market, "300")

    #Run Gann algorithm
    predict, df, granularity, pair = GannLines(candles, market, "300")

    #Build and save chart (saved as temp.png in main directory)
    DisplayChart(predict, df, granularity, pair)

    #Build tweet
    new_line = """

"""

    rdm_1 = random.randint(3,9)
    rdm_tag = random.randint(10,11)

    status = options['intraday_trading']['1'] + token + options['intraday_trading']['2'] + new_line + options['intraday_trading'][str(rdm_1)] + new_line + name + options['intraday_trading'][str(rdm_tag)] + new_line + options['intraday_trading']['12']

    return status


def tweet(status, png_file):

    #Connect Tweepy with Twitter
    auth = tweepy.OAuthHandler(
           consumer_key,
           consumer_secret,
           access_token,
           access_token_secret,
        )
    api = tweepy.API(auth)

    #Upload media files(s)
    media = api.media_upload(filename=png_file)

    #Update status with media
    tweet = api.update_status(status=status, media_ids=[media.media_id_string])

async def tweet_predict():
    r = random.randint(32400, 43200)
    await asyncio.sleep(r)
    tweet(prediction, "temp.png")
    print("Tweet Status Updated: Prediction")

async def tweet_marketing():
    r = random.randint(21600, 28800)
    await asyncio.sleep(r)
    tweet(build_marketing_text(), choose_marketing_png())
    print("Tweet Status Updated: Marketing")

async def tweet_gann():
    r = random.randint(1080, 1560)
    await asyncio.sleep(r)
    tweet(build_gann(), "temp.png")
    print("Tweet Status Updated: Gann")

async def main():
    #Create Websocket asyncio tasks
    predict = asyncio.create_task(tweet_predict())
    marketing = asyncio.create_task(tweet_marketing())
    gann = asyncio.create_task(tweet_gann())

    #Gather and run functions concurrently
    asyncio.gather(
                    asyncio.get_event_loop().run_until_complete(await predict),
                    aasyncio.get_event_loop().run_until_complete(await marketing),
                    asyncio.get_event_loop().run_until_complete(await gann)
                    )

asyncio.run(main())
