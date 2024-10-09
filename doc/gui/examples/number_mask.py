from taipy.gui import Gui, Markdown
import phonenumbers
import pycountry
from phonenumbers import geocoder, region_code_for_number
import re


phone_number = ""
detected_country = "Detecting..."
error_text = ""
valid = False
error_cls = None
masked_number = "" 

def detect_country_code(state):
    try:
        print(state.phone_number)
        # trials ====> germany = +49 30 12345678  usa = +1 2133563445 
        parsed_number = phonenumbers.parse(state.phone_number)
        
        
        country_code = region_code_for_number(parsed_number)
        print(country_code)
        # Get the country name using pycountry
        if country_code:  # Check if country code is valid
            country = pycountry.countries.get(alpha_2=country_code)
            state.detected_country = country.name if country else "Country not found!"
        else:
            state.detected_country = "Country not found!"
        
    except phonenumbers.NumberParseException:
        state.detected_country = "Invalid number!"
    except Exception as e:
        print(e)
        state.detected_country = "Error retrieving country name!"
    state.commit()



page = Markdown(
    """
# Input Masking Demo

Your detected country code is: **<|{detected_country}|>**

Enter your phone number:  
<|{phone_number}|input|class_name={error_cls}|on_change=detect_country_code|>
<|{error_text}|text|class_name={error_cls}|>

<|Mask Input|button|active={valid}|on_click=mask_phone_number|>
Masked Output: <|{masked_number}|>  
""",
    style={".invalid-value": {"background-color": "red"}},
)

# Initialize the GUI
gui = Gui(page)

# Run the GUI on localhost
if __name__ == '__main__':
    gui.run(
        phone_number='',               # Initialize the input state variable
        detected_country='Detecting...',# Placeholder for country detection
        error_text='',                 # Initialize error message
        valid=False,                   # Initial validity state
        error_cls=None,                # Initial error class
        masked_number=''                # Initialize masked output
    )