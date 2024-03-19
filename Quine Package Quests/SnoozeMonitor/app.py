# Import necessary libraries

from taipy.gui import *
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import openai
import plotly.graph_objects as go
import os


# Defining a request function to fetch the response for the prompt from OpenAI's GPT 3.5 Turbo model

def request(prompt):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{prompt}",
            }
        ],
        model="gpt-3.5-turbo",
    )
    x=response.choices[0].message.content
    return x

# Defining a function when submit button is pressed, this initiates the data fetch and processing operation and produces results

def submit(state):
    state.result=''
    err=0
    
    ## Error handling cases
    # height field should be greater than 0
    if state.h<=0:
        err=1
        notify(state, "error", "Height should be a positive value..", True)

    # weight field should be greater than 0
    if state.w<=0:
        err=1
        notify(state, "error", "Weight should be a positive value..", True)
        
    # heart rate per minute field should be greater than 0
    if state.heart<=0:
        err=1
        notify(state, "error", "Heart Rate should be a positive value..", True)

    # Blood pressure should in the format sys/dia    
    if '/' not in state.bp:
        err=1
        notify(state, "error", "Enter Blood Pressure in 'sys/dia' format..", True)
        
    if err==0:
        # Splitting the blood pressure into Systolic and Diastloic pressures
        systolic,diastolic=state.bp.split('/')

        #Calucating BMI = Weightin Kg/ (Height in m)^2 and assigning the labels
        
        bmi=state.w/((state.h/100)**2)
        if bmi<18.5: bmi_label=3
        elif 18.5<=bmi<=24.9: bmi_label=1
        elif 25<=bmi<=30:bmi_label=2
        else: bmi_label=0

        # Loading train data
        
        train=pd.read_csv('assets/train.csv')

        #Collecting the user input data
        
        data=[state.sleep_time,state.phys_level,state.stress,state.heart,state.walking,systolic,diastolic,bmi_label]

        #defining the numerical columns that need to be scaled for modeling 
        
        numeric_cols=['Sleep Duration', 'Physical Activity Level', 'Stress Level','Heart Rate', 'Daily Steps', 'Systolic Pressure',
        'Diastolic Pressure']

        # Defining a StandardScaler Object
        
        scaler=StandardScaler()
        train[numeric_cols]=scaler.fit_transform(train[numeric_cols])

        # Concating with the BMI category
        
        cols=numeric_cols+['BMI Category']

        # Converting into a dataframe
        
        inp_df=pd.DataFrame([data],columns=cols)

        # Copying the contents to a temporary variable
        
        x=inp_df.copy()

        # Scaling down the numerical cols
        
        inp_df[numeric_cols]=scaler.transform(inp_df[numeric_cols])

        # Loading the saved nueral network 
        
        model=load_model('assets/model.h5')

        #Feeding the user input data to the model for prediction
        
        pred=model.predict(inp_df).argmax(axis=1)[0]
        labels={0:'No Worries',1:'Sleep Apnea',2:'Insomnia'}

        # Triggering the results if the user doesn't have any sleep disorder
        
        if pred==0:
            state.prec="""
                1. Maintain a consistent sleep schedule, going to bed and waking up at the same time every day.
                2. Create a relaxing bedtime routine to signal to your body that it's time to wind down.
                3. Ensure your sleep environment is conducive to rest by keeping it dark, quiet, and cool.
                4. Limit exposure to screens before bedtime to avoid disrupting your body's production of melatonin.
                5. Manage stress effectively through techniques like mindfulness or journaling to promote relaxation before sleep.
            """
            state.result="Great news! Everything seems fine. No worries. 🥳"

            # Initiating a pop up Notification 
            
            notify(state, "success", "Great news! Everything seems fine. No worries. 🥳", True)

        # Triggering the results if the user is suffering from Sleep Apnea
        
        elif  pred==1 :
            state.prec=''
            state.result="The result indicates Sleep Apnea, which can have serious health implications 🚩"
            notify(state,"warning","The result indicates Sleep Apnea, which can have serious health implications 🚩",True)
            notify(state,"info","Kindly hold on for a moment as we generate some precautionary measures.",True)

        # Triggering the results if the user is suffering from Insomnia
        
        elif pred==2:
            state.prec=''
            state.result="Attention! The result suggests Insomnia. It's important to address sleep issues early.🙂"
            notify(state,"warning","Attention! The result suggests Insomnia. It's important to address sleep issues early.🙂",True)  
            notify(state,"info","Kindly hold on for a moment as we generate some precautionary measures.",True) 
              
         
        # Triggering the Google's Gemini Generative AI model to generate few precautionary measures
        
        if pred!=0:
            user_data = x.to_dict()
            prompt=f"Recently, I had my sleep health check-up, and it reported that I am suffering from {labels[pred]}, give me the 4-5 necessary precautions as a paragraph to take care of my health. Here is my report {user_data}"
            response = gemini_model.generate_content(prompt)   
            html = markdown.markdown(response.text)
            plain_text = BeautifulSoup(html).get_text()
            lines = plain_text.split('\n')
            state.prec=lines

# Defining a function to reset the input fields to default

def reset_pressed(state):
    state.sleep_time,state.w,state.h,state.phys_level,state.heart,state.stress,state.bp,state.walking=6.5,60,170,5,70,5,'120/80',5000
    state.result,state.prec='',''


# defualt input field contents

w=60
h=170
sleep_time=6.5
phys_level=5
heart=70
stress=5
bp='120/80'
walking=5000
result=''

prec=''

## UI components for data page which contains input fields
# Title of the app

# Tagline for the app

# Initiating a container field whihc contains THEME of the application

# Adding customized styles to the container elements


## Creating 2 column layout
# Using number input field for Weight, Height and Heart Rate

# Using text input field for Blood Pressure

# Making use of sliders to rate their stress level and Physical activity level on the scale of 10

# Sliders to select sleep duration in hrs and Avg. Walking Steps per day

# Creating 2 buttons `submit` and `reset` with appropriate triggering functions called using `on_action`

# Output area for predicted result and precautionary measures

data_page = """

## SnoozeMonitor

***Your ultimate sleep companion!***

<div class="container">
    
<p>Tired of feeling groggy every morning 🥱?  Struggle to fall or stay asleep 😪? </p>

<p>SnoozeMonitor empowers you to take control of your sleep ⏰ Track patterns, get personalized tips, and say goodbye to sleepless nights. Hello to a happier, healthier you with SnoozeMonitor 😃</p>

</div>

<style>
    .container {
        border: 1px solid #ccc;
        width:100%;
        padding: 20px;
        border-radius: 5px;
        background-color:#132842;
        backdrop-filter: blur(3px);
        color:white;
        margin-bottom:10px;
    }
    .p{
        margin-top:10px;
    }
</style>

<|layout|columns=1 1|gap=10px|columns[mobile]=1|

⚖️**Weight** <|{w}|number|label=Weight in kgs|label=Weight in Kg|>

🗼**Height** <|{h}|number|label=Height in CM|label=Height in cm|>

📈**Heart Rate per minute** <|{heart}|number|label=Heart rate|>

🩸**Blood Pressure** <|{bp}|input|label=Enter BP like 120/80|>


🛌🏻**Sleep duration in hrs** 

<|{sleep_time}|slider|min=1|max=10|step=0.5|>

⛹🏻‍♂️**Physical Activity Level**

<|{phys_level}|slider|min=1|max=10|>


⚒️**Stress level**

<|{stress}|slider|step=0.5|min=1|max=10|>

🚶🏻‍♂️**Average Walking Steps**

<|{walking}|slider|step=500|min=1000|max=10000|>



<|Predict|button|on_action=submit|>

<|Reset|button|on_action=reset_pressed|>

|>
-----

<|layout|columns=2*1|


👉🏻***Note*** The below prediction may be inaccurate, do not panic, if it goes wrong 😓!!


📑**Predicted result** <|{result}|text|>

|>
-----

<|layout|columns=1 1|
📌**Precatuions**

<|{prec}|text|>

|>
"""
# Loading the dataset

df=pd.read_csv('assets/data.csv')    


## Performing Exploratory Data Analysis and Visualizing the plots

# Representing Gender distribution using a Pie Chart

gender_counts = df['Gender'].value_counts()
gender_df={
    'Gender': gender_counts.index.tolist(),
    'Count': gender_counts.values.tolist()
}

# Disease count distribtuion across Gender

disease_df=pd.DataFrame({'Disease':['Insomnia','None','Sleep Apnea'],'Male':[41,137,11],'Female':[36,82,67]})

# Sleep Duration Comparision in hrs across gender

lower_bound,upper_bound = min(df['Sleep Duration']), max(df['Sleep Duration']) 
filtered_df = df[(df['Sleep Duration'] >= lower_bound) & (df['Sleep Duration'] <= upper_bound)]
sleep_count = filtered_df.groupby(['Sleep Duration', 'Gender']).size().reset_index(name='Count')
pivot_df = sleep_count.pivot(index='Sleep Duration', columns='Gender', values='Count').reset_index()
sleep_df=pivot_df.fillna(0)

# Stress level comparision across Gedner

lower_bound,upper_bound = 0, 10
filtered_df = df[(df['Stress Level'] >= lower_bound) & (df['Stress Level'] <= upper_bound)]
stress_count = filtered_df.groupby(['Stress Level', 'Gender']).size().reset_index(name='Count')
pivot_df = stress_count.pivot(index='Stress Level', columns='Gender', values='Count').reset_index()
stress_df=pivot_df.fillna(0)

# BMI Category distrbution in the dataset, using Pie Chart 

bmi_counts = df['BMI Category'].value_counts()
bmi_df={
    'BMI Category': bmi_counts.index.tolist(),
    'Count': bmi_counts.values.tolist()
}

options={
    "fill": "tozeroy"
    }

# Representing Avg Sleep Duration in hrs v/s occupaton using Box plots

occupations = df['Occupation'].unique()
fig=go.Figure()
for i, occupation in enumerate(occupations):
    occupation_data = df[df['Occupation'] == occupation]['Sleep Duration']
    fig.add_trace(go.Box(y=occupation_data, name=occupation))
fig.update_layout(
    title='Sleep Duration by Occupation',
    xaxis=dict(title='Occupation'),
    yaxis=dict(title='Sleep Duration')
)

# Visualizing the Avg. Stress experienced by an Occupation using Bar plot
avg_stress_by_occupation = df.groupby('Occupation')['Stress Level'].mean().reset_index()
color_scale = [[0,'blue'],[0.4,'green'],[0.8,'orange'],[1,'red']]  
fig1 = go.Figure(go.Bar(
    x=avg_stress_by_occupation['Stress Level'],
    y=avg_stress_by_occupation['Occupation'],
    marker=dict(color=avg_stress_by_occupation['Stress Level'], 
                coloraxis='coloraxis'), 
    orientation='h',  
    hoverinfo='x+y',  
    textposition='inside',  
    texttemplate='%{x:.2f}',  
))
fig1.update_layout(
    title='Average Stress Level by Occupation',
    yaxis=dict(tickangle=-30),
    xaxis=dict(title='Average Stress Level'), 
    bargap=0.15,  
    font=dict(family='Arial', size=9, color='white'),  
    coloraxis=dict(colorscale=color_scale, cmin=0, cmax=8),  
)

# UI Design and layout code for Plots Page
## Defining a 2 Columns grid layout

# 1. Pie chart showing Gender Distribution

# 2. Histogram showing the count of persons in each occupation

# 3. Bar plot showing the count of persons suffering from sleep disorder across Gender

# 4. Area Chart representing the Sleep Duration distribution across Gender

# 5. Area Chart representing the Stress Level distribution across Gender

# 6. Pie Chart showing BMI Category Distribution

# 7. Box plots depicitng the sleep duration across occupaton

# 8. Horizontal Bar plots showing the Avg. Stress levels expeerienced by a person comparing across Occupation

plot_file="""
## SnoozeMonitor

***Your ultimate sleep companion!***

<|layout|columns=1 1|gap=20px|columns[mobile]=1|

<|{gender_df}|chart|type=pie|labels=Gender|values=Count|title=Gender Distribution|>

<|{df}|chart|type=histogram|x=Occupation|title=Data distribtuion across Occupation|>

<|{disease_df}|chart|type=bar|x=Disease|y[1]=Male|y[2]=Female|title=Disease Counts by Gender|>

<|{sleep_df}|chart|mode=lines|x=Sleep Duration|y[1]=Male|y[2]=Female|options={options}|title=Sleep Duration Distribution by Gender|>


<|{stress_df}|chart|mode=lines|x=Stress Level|y[1]=Male|y[2]=Female|options={options}|title=Stress Level Distribution by Gender|>


<|{bmi_df}|chart|type=pie|labels=BMI Category|values=Count|title=BMI Distribution|>

|>

-----

<|chart|figure={fig}|>

------

<|chart|figure={fig1}|>


"""

# Defining a multi page application with Navigation bar

pages = {"/":" <|navbar|>",
         "Data":data_page,
         "Plots":plot_file}

# Initialize a client object for interacting with the OpenAI API using the provided API key.
client=openai.Client(api_key=os.getenv("OPENAI_API_KEY")

# Create a GUI application object with the specified pages.
app = Gui(pages=pages)

# Running the application, by default the application runs in `loclahost:http://127.0.0.1:5000/` 

# Configuring the page style : Page title, Page icon and watermark

app.run(title="SnoozeMonitor",use_reloader=True, watermark="Let's sleep well 😴", favicon='https://emojifavicon.dev/favicons/1f4a4.png')
