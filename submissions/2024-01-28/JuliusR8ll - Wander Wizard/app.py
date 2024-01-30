...

from taipy import Gui
from flask import Flask, request, jsonify
# import openai
from taipy.gui import Html
import re
import os
from PIL import Image
import google.generativeai as palm
from dotenv import load_dotenv
load_dotenv() 


palm.configure(api_key= os.getenv("key"))


models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name


image_path="./safe journey.gif"
image = Image.open(image_path)

def format_content(content):
    # Define a regular expression pattern to identify headings
    heading_pattern = re.compile(r'\*\*([^*]+)\*\*')
    
    # Replace each heading with a new line after it
    formatted_content = heading_pattern.sub(r'\n\n\1 ', content)

    return formatted_content


def submit_scenario(state):
    print("pahucha")
    input_url_place=state.input_url_place
    input_url_option=state.input_url_option
    print(input_url_option+input_url_place)
    data={
          "place":input_url_place ,
          "option":  input_url_option
    }

    place = data.get("place")
    option = data.get("option")

    prompt = f"Imagine you're a seasoned travel writer crafting a captivating guide about {place}, highlighting {option}. Paint a vivid picture with your words, including practical tips, hidden gems, and unique experiences that make this place special"
    completion = palm.generate_text(
    model=model,
    prompt=prompt,
    temperature=0.7,
    # The maximum length of the response
    max_output_tokens=750,
    )
    

    # print(completion.choices[0].message)



    print('reached')
    message = format_content(completion.result)
    state.message = message



    

    # return jsonify({"response": response.choices[0].text.strip()})


   

options = ["The best places to go?", "The best things to do?", "The best travel tips?","The best clothes to bring ?","The best time to go?"]

input_url_place=""
input_url_option=""
message=""

# Definition of the page
page = """

<style>

.container-heading {
  
  font-size: 7rem;
  display:flex;
  justify-content:center;
   paddding:2rem;
  }

  .desc{
   display:flex;
  justify-content:center;
  align-items:center;
  }

.center{
 display:flex;
  justify-content:center;
   paddding:2rem;
   margin:3rem;
   text-align:center;
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






 

<|center|

Ai :  <|{message}|text|>

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
 app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
