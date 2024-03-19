from taipy.gui import Gui, notify
import pickle
import string
from nltk.corpus import stopwords
import nltk
from nltk.stem import WordNetLemmatizer
lemma = WordNetLemmatizer()

def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    y = []
    for i in text:
        if i.isalnum():
            y.append(i)
    text = y[:]
    y.clear()
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)
    text = y[:]
    y.clear()
    for i in text:
        y.append(lemma.lemmatize(i))
    return " ".join(y)
tfidf = pickle.load(open('vectorizer.pkl','rb'))
model = pickle.load(open('model.pkl','rb'))

intro = "Enter the message:"
dummy = " "
message = " "
h_text = "Click to classify the spam or ham mail/sms"

page = """
<|text-center|
#
# Email/SMS **Spam**{:.color-primary} Detector
|>

<|{intro}|>

#

<|{dummy}|input|multiline|class_name=fullwidth|label=Hi there! Rohan Sharma this side!|>

#
<|text-center|

<|Predict|button|on_action=on_button_action|hover_text = Click to classify the spam or ham mail/sms|center|>

#

<|{message}|input|not active|label= Know the results here!|>


######Made with **LOVE**{:.color-primary} by Rohan Sharma
|>

"""
def on_button_action(state):
    notify(state, 'info', f'Results may be inaccurate due to limited dataset. Thanks for using this Application :p')
    state.text = "Rendering results"

def on_change(state):
    # 1. preprocess
    transformed_sms = transform_text(intro)
    # 2. vectorize
    vector_input = tfidf.transform([transformed_sms])
    # 3. predict
    result = model.predict(vector_input)[0]
    # 4. Display
    if result == 1:
        state.message = "Spam"       
    else:
       state.message ="Not-Spam"

if __name__ == "__main__":
    app = Gui(page).run(watermark="""Taipy Inside :)""",use_reloader=True)