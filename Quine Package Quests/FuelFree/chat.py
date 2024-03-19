from dotenv import load_dotenv
import os
import cohere

# configuration
load_dotenv()
secret_key = os.getenv("API_KEY")
co = cohere.Client(secret_key)


def genActivity(topic):
    response = co.generate(
    model='command',
    prompt=topic,
    max_tokens=300,
    temperature=0.3,
    )
    # response is a string that is the answer to the topic in less than 60 words
    return response.generations[0].text

# print(genActivity(topic))