# TwitterBot
Bot is designed to generate graphs via gann_prototype.py and predict.py, save the files as temp.png, generate a tweet based on tweets.json database with random assignment of string mixes. Bot is currently being run for Parcae.io marketing.

## Gann_prototype
Gan prototype is a work in progress. It will currently query Coinbase via http request for approximately 45-50 five minute candlesticks of BTC or ETH. The calculation is for the 45 degree and 26 degrees fan pattern. Descending calculation is based on the highest closing candlestick in the dataset. Ascending calculation is based on the lowest closing candlestick in the dataset. Candlestick data is stored via Pandas. Calculations are assisted by numpy. Visulations are assisted by matplotlib.

## Predict
Predict is a reproduction of an existing repository from github @c1im4cu5. File has been redesigned for a graph generated via matplotlib.

## Marketing
Marketing section of main.py (and tweets.json) reference random png's from 1-12. The png files are not supplied.

## Starting a Developer Account with Twitter
You will need a Twitter API v2 account. Getting access to API v2 currently requires permission from Twitter. Please make sure to acquire access for the appropriate API version. After you've gained access to the correct API, please take the time to regenerate ALL tokens. Here is a link to the developer portal: <a href="https://developer.twitter.com/">Twitter Developer Portal</ahref>

## Running
Bot is currently being run with Twitter handle @parcaeBot
