from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

from pandas import DataFrame
from tweepy import Cursor
import io
import zipfile
import numpy as np
import tweepy
import string
import emoji
import re
import os

# Using dotenv
from dotenv import load_dotenv
load_dotenv()

# Using dotenv/env.py
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def cleanTweets(text):
    text = re.sub("https*\S+", "", text)
    text = re.sub("@\S+", "", text)
    text = emoji.demojize(text)
    text = ''.join(text)
    return text


def main(request):
    if request.method == 'POST':

        usernames = request.POST['twitter-usernames']
        username_list = [x.strip() for x in usernames.split(',')]

        # insert the keyword here for the extraction to continue
        retweet_filter = '-filter:retweets'

        # append the term to search parameters
        q = retweet_filter
        tweets_per_qry = 200
        since_id = None
        max_id = -1
        max_tweets = 1000
        all_tweets = []

        # Create the zip file
        output = io.BytesIO()
        f = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)

        # Extract tweets from timeline of targeted politicians of the major political parties
        try:

            # Loop through all the users and extract tweets from their relative timelines
            for user in username_list:

                tweets = api.user_timeline(screen_name=user,
                                           # 200 is the maximum allowed count
                                           count=200,
                                           exclude_replies=True,
                                           include_rts=False,
                                           # Necessary to keep full_text
                                           # otherwise only the first 140 words are extracted
                                           tweet_mode='extended'
                                           )

                all_tweets = []
                all_tweets.extend(tweets)
                oldest_id = tweets[-1].id

                while True:
                    tweets = api.user_timeline(screen_name=user,
                                               # 200 is the maximum allowed count
                                               count=200,
                                               exclude_replies=True,
                                               include_rts=False,
                                               max_id=oldest_id - 1,
                                               # Necessary to keep full_text
                                               # otherwise only the first 140 words are extracted
                                               tweet_mode='extended'
                                               )
                    if len(tweets) == 0:
                        break

                    oldest_id = tweets[-1].id
                    all_tweets.extend(tweets)

                # Transform the tweepy tweets into a 2D array that will populate the csv
                outtweets = [[
                    tweet.id_str,
                    tweet.created_at,

                    # Clean tweets (remove symbols, links and emojis)
                    cleanTweets(tweet.full_text.encode(
                                "utf-8").decode("utf-8"))

                    # Raw tweets
                    # tweet.full_text.encode("utf-8").decode("utf-8")
                ]
                    for idx, tweet in enumerate(all_tweets)]

                # export_csv(outtweets, user)
                df = DataFrame(outtweets, columns=[
                               "ID", "Date Created", "Text"])

                # Remove any rows with empty strings
                df.replace(r'^\s*$', np.nan, inplace=True, regex=True)
                df.dropna(how="any", axis=0, inplace=True)
                csv_file = df.to_csv(index=False)
                # df.to_csv(index=False, path_or_buf=response)
                df.head(3)

                f.writestr(user + '.csv', csv_file)

            f.close()

            # Build your response
            response = HttpResponse(
                output.getvalue(), content_type = 'application/zip')
            response['Content-Disposition'] = 'attachment; filename=extracted_tweets.zip'

            messages.success(request, "Tweets extraction successful!")

            return response

        except tweepy.TweepError as e:
            print("There was an error, find details below, else check your internet connection or your " +
                  "credentials in the credentials.py file \n")
            print("If this is not your first time running this particular script, then there is a possibility that the "
                  "maximum rate limit has been exceeded. wait a few more minutes and re run the script.\n")
            print(f"Error Details: {str(e)}")
    else:
        return render(request, 'main.html')
