from taipy import Gui
import taipy as tp
from taipy import Config, Core, Gui
import taipy as tp
import google.generativeai as palm
import json
from bs4 import BeautifulSoup
palm.configure(api_key='InPut_PALm_API_KeY')



models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name
print(model)


# import random
# import openai
# import requests
# from bs4 import BeautifulSoup
# from metaphor_python import Metaphor

# # Set your OpenAI API key
# openai.api_key = "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"

# # Set your Metaphor API key
# metaphor_api_key = "78680482-9066-4983-8119-fb342968edc7"
# metaphor = Metaphor(metaphor_api_key)

import requests


def scrape_article_content(url):
    try:
        # Send a GET request to the article URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the text content from the article
        article_text = ""
        for paragraph in soup.find_all('p'):
            article_text += paragraph.get_text() + '\n'

        return article_text

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# # Example usage
# article_url = "https://www.theatlantic.com/ideas/archive/2024/01/dance-salsa-relationships/677132/?utm_source=pocket-newtab-en-intl"
# article_content = scrape_article_content(article_url)

# if article_content:
#     print("Article Content:")
#     print(article_content)




# # Set your input text
# prompt = "Carefully read the following paragraph and create concise, informative notes highlighting the key points with sub headings and concepts. Structure the notes logically and clearly, making them easy to understand and review later"
# prompt += article_content
# completion = palm.generate_text(
#     model=model,
#     prompt=prompt,
#     temperature=0,
#     # The maximum length of the response
#     max_output_tokens=1000,
# )

# print(completion.result)
#notes_text = completion.result


# notes_json = {
#     "notes": notes_text.splitlines()  # Split the text into a list of lines
# }

# # Convert the data structure to JSON format
# notes_json_string = json.dumps(notes_json)

# print(notes_json_string)



input_url="input website url "
qsn_no=1
message=" "

def submit_scenario(state):
    global input_url, qsn_no, message  # Add this line to indicate that you're using the global variables
    input_url = state.input_url
    article_url = input_url
    article_content = scrape_article_content(article_url)
    print("article content bsdk" + article_content)
    prompt = "Carefully read the following paragraph and create concise, informative notes highlighting the key points with sub headings and concepts. Structure the notes logically and clearly, making them easy to understand and review later"
    prompt += article_content
    completion = palm.generate_text(
    model=model,
    prompt=prompt,
    temperature=0,
    # The maximum length of the response
    max_output_tokens=1000,
    )

    print(completion.result)
#notes_text = completion.result



    message = completion.result
    state.message = message
    
    print(input_url)
    print("message "+message)



# def format_notes(notes_text):
#     # Your logic to format the notes goes here
#     # This is a basic example, you may need to adapt it based on your specific requirements
#     sections = notes_text.split("**")
#     formatted_notes = ""
#     for i in range(1, len(sections), 2):
#         heading = sections[i].strip()
#         content = sections[i + 1].strip()
#         formatted_notes += f"\n\n{heading}\n{content}"
    
#     return formatted_notes
page = """
<style>

</style>

<|text-center|
<h1>Echo Learn</h1>

<p>A platform to give summary of any website  </p>


Url of website  : <|{input_url}|input|>   <|submit|button|on_action=submit_scenario|>
>
Ai Ans: <|{message}|text|>

"""





   # find_similar_urls_and_generate_quiz(input_url,qsn_no )




if __name__ =="__main__":
   tp.Core().run()
   app=Gui(page)
   app.run(use_reloader=True)
   