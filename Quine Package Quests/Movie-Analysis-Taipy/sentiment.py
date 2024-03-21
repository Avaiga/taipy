import nltk
#nltk.download('punkt')
#nltk.download('vader_lexicon')



from nltk.sentiment.vader import SentimentIntensityAnalyzer 

sia = SentimentIntensityAnalyzer()

def calc_score(text:str):
    score = sia.polarity_scores(text)
    if(score['compound']>=0.05):
        return "Positive"
    elif(score['compound']<0.05 and score['compound']>-0.05):
        return "Neutral"
    else:
        return "Negative"