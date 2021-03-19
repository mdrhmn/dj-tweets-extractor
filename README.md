# Django Tweets Extractor

This is a simple Django app to extract Tweets from public Twitter users using Twitter Developers API.

![alt text](https://imgur.com/Cm9L6pI.png)

## Project Set Up

1. To begin, clone this repository in your local environment.

    ```$ git clone https://github.com/mdrhmn/dj-tweets-extractor```

2. cd into the cloned directory

    ```$ cd dj-tweets-extractor/```

3. Install the required packages

    ```$ pip3 install -r requirements.txt```

4. Rename the ```settings.env``` file to ```.env```. To use this app, you **must have a Twitter Developer account registered** and **update the .env file with the required credentials**.

    ```env
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    ACCESS_TOKEN = ''
    ACCESS_TOKEN_SECRET = ''
    ```

## Features

1. Extraction of tweets from public Twitter account (excluding retweets, replies and mentions)
2. Demojisation of emojis in tweets