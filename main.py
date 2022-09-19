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

#Load .env file
load_dotenv()

#Get Directory Path
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

#Twitter ID - Used in Streams (Currently set to @ParcaeBot)
queen = 1503097980588462081

#A Class Stream that will retweet designated tweets - See Class Implementation for Stream Details (Filter)
class RetweetStream(AsyncStream):

    async def on_status(self, tweet):
        try:

            #Will only retweet if there is media in the tweet
            media = tweet.entities['media']
            #Check if the tweet was already retweeted
            if not tweet.retweeted:
                # Retweet, since we have not retweeted it yet
                try:
                    #Retweet with client
                    await aclient.retweet(tweet_id=str(tweet.id), user_auth=True)
                    print("Retweeted: " + str(tweet.id))
                    #To avoid exceeding the rate limit, a sleep of 22 seconds is enabled
                    await asyncio.sleep(22)
                    return True
                except Exception as e:
                    print("Error on fav and retweet")
                    print(e)
                    return False
            #To avoid exceeding the rate limit, a sleep of 22 seconds is enabled
            await asyncio.sleep(22)
            return True
        except KeyError:
            return True

    async def on_error(self, status):
        if status == 420:
            # returning False disconnects the stream
            print("ERROR 420: Disconnecting Stream")
            return False
        elif status == 401:
            # returning non-False continues the stream
            print("ERROR 401: Disconnecting Stream")
            return False

#A Class Stream that will "Like" or "Heart" designated tweets
class LikeStream(AsyncStream):

    async def on_status(self, tweet):
        try:
            #Checking to see if media content is in the tweet
            media = tweet.entities['media']
            print(f"Processing tweet id: " + str(tweet.id))
            #Checking if tweet is a reply or users' tweet
            if tweet.in_reply_to_status_id is not None or tweet.user.id == queen:
                # This tweet is a reply or I'm its author so, ignore it
                return True
            if not tweet.favorited:
                # Mark it as Liked, since we have not done it yet
                try:
                    await aclient.like(tweet_id=str(tweet.id), user_auth=True)
                    print("Liked: "+ str(tweet.id))
                except Exception as e:
                    print(e)
                    return False
        except KeyError:
            return True

    async def on_error(self, status):
        if status == 420:
            # returning False disconnects the stream
            print("ERROR 420: Disconnecting Stream")
            return False
        elif status == 401:
            # returning non-False continues the stream
            print("ERROR 401: Disconnecting Stream")
            return False
        elif status == 403:
            # returning non-False continues the stream
            print("ERROR 403: Disconnecting Stream")
            return False


#Function to tweet 10 day crypto predictions
def prediction():
    new_line = """

"""
    #Load options.json file
    with open("tweets.json", "r") as read_file:
        options = json.load(read_file)

    #Random numbers generated to choose JSON stored data
    rdm_1 = random.randint(0,11)
    rdm_2 = random.randint(3,4)

    #Get markets
    market = options['markets'][rdm_1][str(rdm_1)]

    #Get token
    token = options['markets'][rdm_1]['value']

    #Get Name of token for tweet
    name = options['markets'][rdm_1]['name']

    #Run prediction algorithm located at predict.py (Import)
    #Algorithm will save a picture as "temp.png"
    combine_predictions(market)

    #Set Tweet status (Text)
    status = options['predict_status']['1'] + token + options['predict_status']['2'] + new_line + name + options['predict_status'][str(rdm_2)] + new_line + options['intraday_trading']['12']

    #Return Text for Tweet
    return status


#Function to market Parcae.io and
#NFT Collection from ERC-721 Vyper Contract
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

#Files not associated with Github Repo are stored on the server. These files are labeled "1.png" through "12.png"
#They are NFT pictures (See Twitter @ParcaeBot for pics)
def choose_marketing_png():

    #Because files are name with nummber sequences, randomly choose a file name to return
    text = str(random.randint(1,12)) + ".png"

    #Return Text of file name
    return text

#Function to build gann tweets (See gann_prototype.py)
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


#Function to compile authenticate login and post tweet
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


#Initiate LikeStream Class as as asyncio likes function to track list of strings
async def likes():
    stream = LikeStream(consumer_key, consumer_secret, access_token, access_token_secret)
    await stream.filter(track=["#technicalanalysis","#btcgraph", "#ethgraph","#avaxgraph", "#solgraph", "#Matplotlib","#MachineLearning", "#NFTCollection", "#NFT", "#nftart"], languages=["en"])

#Initiate Rewtweet class as asyncio function to reweet list of strings
async def retweets():
    stream = RetweetStream(consumer_key, consumer_secret, access_token, access_token_secret)
    await stream.filter(track=["$SWTH", "@0xcarbon", "#Demexchange"], languages=["en"])

#async function to build 10 day prediction (ML) tweet (See predict.py)
async def tweet_predict():
    r = random.randint(32400, 43200)
    await asyncio.sleep(r)
    tweet(prediction, "temp.png")
    print("Tweet Status Updated: Prediction")


#async function to tweet marketing NFT
async def tweet_marketing():
    r = random.randint(21600, 28800)
    await asyncio.sleep(r)
    tweet(build_marketing_text(), choose_marketing_png())
    print("Tweet Status Updated: Marketing")

#async function to tweet Gann lines for ETH and BTC
async def tweet_gann():
    r = random.randint(1080, 1560)
    await asyncio.sleep(r)
    tweet(build_gann(), "temp.png")
    print("Tweet Status Updated: Gann")

#compile all functions into main
async def main():
    #Create Websocket asyncio tasks
    predict = asyncio.create_task(tweet_predict())
    marketing = asyncio.create_task(tweet_marketing())
    gann = asyncio.create_task(tweet_gann())
    like_stream = asyncio.creatretask(likes())
    retweet_stream = asyncio.creatre_task(retweets())

    #Gather and run functions concurrently
    asyncio.gather(
                    asyncio.get_event_loop().run_until_complete(await predict),
                    aasyncio.get_event_loop().run_until_complete(await marketing),
                    asyncio.get_event_loop().run_until_complete(await gann)
                    )

asyncio.run(main())
