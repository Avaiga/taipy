import pandas as pd
import nltk
import string
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

# Download the necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load the queries
with open('data/queries.json', 'r') as f:
    queries = json.load(f)
query_words = [word for sublist in queries for word in sublist]

def preprocess_text(text):
    # Check if text is not NaN
    if pd.isnull(text):
        return ''
    
    # Convert to lower case
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    words = word_tokenize(text)
    
    # Remove stopwords, lemmatize, and keep only words that are in query_words
    words = [lemmatizer.lemmatize(word) for word in words if word not in stopwords.words('english') and word in query_words]
    
    # Join words back into a string
    text = ' '.join(words)
    
    return text

# Load the data
df = pd.read_csv('data/desc/2024_03_17desc_in.csv')

# Preprocess the descriptions
df['description'] = df['description'].apply(preprocess_text)

# Initialize the vectorizer
vectorizer = TfidfVectorizer()

# Vectorize the descriptions
df['description'] = list(vectorizer.fit_transform(df['description']).toarray())

# Save the processed data
df.to_csv('processed_data.csv', index=False)