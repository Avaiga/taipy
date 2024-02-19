...

from taipy import Gui
from flask import Flask, request, jsonify
from taipy.gui import Html
import re
import os
from PIL import Image
import google.generativeai as palm
from dotenv import load_dotenv
import json
from openai import OpenAI
load_dotenv() 

client = OpenAI(api_key=os.getenv("KEY"))
# palm.configure(api_key= os.getenv("key"))


# models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
# model = models[0].name


image_path="./safe journey.gif"
image = Image.open(image_path)



def display_json_result(result):
    user_friendly_format = ""
    try:
        json_data = json.loads(result)
        for key, value in json_data.items():
            user_friendly_format += f"\n {key}: {value['text']} \n\n "
    except json.JSONDecodeError as e:
        user_friendly_format = f"Establishing connection please retry ... "

    return user_friendly_format

def submit_scenario(state):
    print("pahucha")
    input_url_place = state.input_url_place
    input_url_option = state.input_url_option
    print(input_url_option + input_url_place)
    data = {
        "place": input_url_place,
        "option": input_url_option
    }

    place = data.get("place")
    option = data.get("option")

  
    prompt = f"""
    Imagine you're a seasoned travel writer crafting a captivating guide about {place}, highlighting {option}. 
    Paint a vivid picture with your words, including practical tips, hidden gems, and unique experiences that make this place special. 
    dont give long response of text make it  short and informative  about the place or thing user are looking at.
    *Present each recommendation or insight as a separate numbered JSON object, containing a descriptive sentence within the 'text' key.* 

    Follow the example format:

    {{
    "1": {{"text": "Your first recommendation here."}},
    "2": {{"text": "Your second recommendation here."}},
    ...
    }}
 
    Please ensure each recommendation is structured as a separate JSON object with a unique number and follows the 'text' key format. Be mindful of correct JSON syntax.
    only give 7 points

    """
    
    # completion = palm.generate_text(
    #     model=model,
    #     prompt=prompt,
    #     temperature=0.7,
    #     # The maximum length of the response
    #     max_output_tokens=1000,
    # )
    completion = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens=500,
    temperature=0.8,
    )


    print('reached')
    res = completion.choices[0].text
    json_string = res.replace("```", "").replace("json", "")
    print(json_string)
    user_friendly_message = display_json_result(json_string)
    state.message = user_friendly_message



    



options = ["The best places to go?", "The best things to do?", "The best travel Tips","The best clothes to bring ?","The best Time to go"]

input_url_place=""
input_url_option=""



message=""

# Definition of the page
page = """

<style>

.container-heading {
  
  font-size: 5rem;
  display:flex;
  justify-content:center;
   align-items:center;
   paddding:2rem;
  }

  .desc{
   display:flex;
  justify-content:center;
  align-items:center;
  padding:2rem;
  }

.center{
 display:flex;
  justify-content:center;
   paddding:2rem;
   margin:3rem;
   text-align:center;
}

.center-output{
 display:flex;
 justify-content:center;
 width:100%;
}
.fullwidth{
width:100% !important;
}

.form{
 display:flex;
 flex-direction:column;
 justify-content:space-evenly;
 padding:2rem;
 margin-top:2rem;
}


.middleSection{
 display:flex;
  flex-wrap: wrap;
 justify-content:center;
 gap:2rem;
 padding:"2rem"
 
}

.buttonStyle{
margin-top:1rem;
}

.fullCenter{
 display:flex;
 justify-content:center;
 align-items:center;
  flex-direction:column;
}

</style>

<|container-heading| 
 Wander  Wizard 🪄 
 |>


<|desc| 

<||  - A Tool to help you to take decision for your trips |> 

|>


<|middleSection| 
 
<|fullCenter|  
 <|{image_path}|image|>

 |>

<||

<h4>Plan your trips with wise decision </h4>



<|form| 


Enter place name : <br></br>
<|{input_url_place}|input|>
  



Enter option for your trip : 
<|{input_url_option}|selector|lov={options}|dropdown|>

Or enter a custom option: 
<|{input_url_option}|input|>

<|buttonStyle|
<|submit|button|on_action=submit_scenario|>
|>





|>




|>



 |>




<|part|class_name=card mt1|
<|{message}|input|multiline|not active|label= your message will appear here...|class_name=fullwidth|>
|>


<|center|

Made with 💖 by
[Rahul Yadav](https://www.linkedin.com/in/rahul-yadav-50276723b/) ,
[Sahil Pradhan](https://www.linkedin.com/in/sahil-pradhan-46a0a31b7/)

|>





"""




if __name__ =="__main__": 
# Create a Gui object with our page content
 app=Gui(page=page)
 app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True,use_reloader=True)
