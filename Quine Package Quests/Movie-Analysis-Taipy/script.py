import re
import requests
from bs4 import BeautifulSoup
import sentiment
from imdb import Cinemagoer


def fetch_movie(input):
    ia = Cinemagoer()

    search = ia.search_movie(title=input)


    if(len(search)==0):
        print("Not Found")

    id = "tt"+search[0].movieID
    data = search[0].data
    title = data['title']
    poster_url = data['cover url']
    url = f'https://www.imdb.com/title/{id}/reviews/'
    return url, title, poster_url


def html_removal(text):
   text = re.compile(r'<[^>]+>').sub('', text)
   return text

def reviews_func(url):
    
    page = requests.get(url=url)

    soup = BeautifulSoup(page.content, "html.parser")

    reviews = soup.find_all("div",class_="text show-more__control")
    reviews = list(reviews)
    for i in range(len(reviews)):
        reviews[i] = html_removal(str(reviews[i]))
    return reviews

def sentiment_analysis(movie, language = "English"):
    analysis = dict()
    url, title, poster_url = fetch_movie(movie)
    analysis['title'] = title

    reviews = reviews_func(url)
    total = len(reviews)
    positive = 0
    negative = 0
    for review in reviews:
        score = sentiment.calc_score(str(review))
        if score == 'Positive':
            positive+=1
        elif score == 'Negative':
            negative+=1
    
    if(positive>negative):
        overall_sentiment = 'Positive'
        percentage = f"{round((positive/total),2)*100}%"
    elif(positive<negative):
        overall_sentiment = 'Negative'
        percentage = f"{round((negative/total),2)*100}%"
    else:
        overall_sentiment = 'Neutral'
        percentage = "50%"
    
    analysis['sentiment'] = overall_sentiment
    analysis['percentage'] = percentage

    if(language == "English"):
        return analysis
    elif(language == "Hindi"):
        if(analysis['sentiment'] == "Positive"):
            analysis['sentiment'] = 'उत्तम'
        elif(analysis['sentiment'] == "Negative"):
            analysis['sentiment'] = 'खराब'

    return analysis