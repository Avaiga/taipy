# from math import sqrt
import taipy as tp
import pandas as pd
from taipy import Config, Scope, Gui
from taipy.gui import Html
import numpy as np
from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import pickle
# from sklearn.neural_network import MLPRegressor

# Create a Taipy App that will output the carbon footprint of a person based on his lifestyle choices

# Taipy Core - backend definition

def calculate_carbon_emission(initial_dataset: pd.DataFrame, height, weight, sex, diet, how_often_shower, heating_energy_source, transport, vehicle_type, vehicle_monthly_distance_km, social_activity, monthly_grocery_bill, frequency_traveling_by_air, waste_bag_size, waste_bag_weekly_count, how_long_tv_pc_daily_hour, how_many_new_clothes_monthly, how_long_internet_daily_hour, energy_efficiency, recycling, cooking_with):

    # Calculate carbon emission based on the selected lifestyle choices

    # Ckeck passed values
    if (height == "" or weight == "" or sex == "" or diet == "" or how_often_shower == "" or heating_energy_source == "" or transport == "" or vehicle_type == "" or vehicle_monthly_distance_km == "" or social_activity == "" or monthly_grocery_bill == "" or frequency_traveling_by_air == "" or waste_bag_size == "" or waste_bag_weekly_count == "" or how_long_tv_pc_daily_hour == "" or how_many_new_clothes_monthly == "" or how_long_internet_daily_hour == "" or energy_efficiency == ""):
        return "Please fill in all the required fields."
    
    # Encode categorical values
    #print(initial_dataset['Energy efficiency'][:5])

    initial_dataset['Body Type'] = initial_dataset['Body Type'].astype('category').cat.codes
    initial_dataset['Sex'] = initial_dataset['Sex'].astype('category').cat.codes
    initial_dataset['Diet'] = initial_dataset['Diet'].astype('category').cat.codes
    initial_dataset['How Often Shower'] = initial_dataset['How Often Shower'].astype('category').cat.codes
    initial_dataset['Heating Energy Source'] = initial_dataset['Heating Energy Source'].astype('category').cat.codes
    initial_dataset['Transport'] = initial_dataset['Transport'].astype('category').cat.codes
    initial_dataset['Vehicle Type'] = initial_dataset['Vehicle Type'].astype('category').cat.codes
    initial_dataset['Social Activity'] = initial_dataset['Social Activity'].astype('category').cat.codes
    initial_dataset['Frequency of Traveling by Air'] = initial_dataset['Frequency of Traveling by Air'].astype('category').cat.codes
    initial_dataset['Waste Bag Size'] = initial_dataset['Waste Bag Size'].astype('category').cat.codes
    initial_dataset['Energy efficiency'] = initial_dataset['Energy efficiency'].astype('category').cat.codes

    #print(initial_dataset['Energy efficiency'][:5])

    # Format body_type
    body_type = determine_body_type(height, weight)
    if body_type == "Obese":
        body_type = 1
    elif body_type == "Overweight":
        body_type = 2
    elif body_type == "Normal":
        body_type = 0
    else:
        body_type = 3

    # Format sex
    if sex == "Male":
        sex = 1
    else:
        sex = 0

    # Format diet
    if diet == "Vegetarian":
        diet = 3
    elif diet == "Vegan":
        diet = 2
    elif diet == "Pescatarian":
        diet = 1
    else:
        diet = 0
    
    # Format how_often_shower
    if how_often_shower == "Daily":
        how_often_shower = 0
    elif how_often_shower == "Twice a day":
        how_often_shower = 3
    elif how_often_shower == "More frequently":
        how_often_shower = 2
    else:
        how_often_shower = 1

    # Format heating_energy_source
    if heating_energy_source == "Wood":
        heating_energy_source = 3
    elif heating_energy_source == "Electricity":
        heating_energy_source = 1
    elif heating_energy_source == "Coal":
        heating_energy_source = 0
    else:
        heating_energy_source = 2

    # Format transport
    if transport == "Public":
        transport = 1
    elif transport == "Private":
        transport = 0
    else:
        transport = 2

    # Format vehicle_type
    if vehicle_type == "Diesel":
        vehicle_type = 0
    elif vehicle_type == "Electric":
        vehicle_type = 1
    elif vehicle_type == "Hybrid":
        vehicle_type = 2
    elif vehicle_type == "Lpg":
        vehicle_type = 3
    elif vehicle_type == "Petrol":
        vehicle_type = 4
    else:
        vehicle_type = -1

    # Format social_activity
    if social_activity == "Never":
        social_activity = 0
    elif social_activity == "Often":
        social_activity = 1
    else:
        social_activity = 2

    # Format frequency_traveling_by_air
    if frequency_traveling_by_air == "Frequently":
        frequency_traveling_by_air = 0
    elif frequency_traveling_by_air == "Never":
        frequency_traveling_by_air = 1
    elif frequency_traveling_by_air == "Rarely":
        frequency_traveling_by_air = 2
    else:
        frequency_traveling_by_air = 3

    # Format waste_bag_size
    if waste_bag_size == "Small":
        waste_bag_size = 3
    elif waste_bag_size == "Medium":
        waste_bag_size = 2
    elif waste_bag_size == "Large":
        waste_bag_size = 1
    else:
        waste_bag_size = 0

    # Format energy_efficiency
    if energy_efficiency == "Yes":
        energy_efficiency = 2
    elif energy_efficiency == "No":
        energy_efficiency = 0
    else:
        energy_efficiency = 1

    # Drop unused columns
    
    initial_dataset = initial_dataset.drop(['Recycling', 'Cooking_With'], axis=1)

    # Separate features and target
        
    X = initial_dataset.drop('CarbonEmission', axis=1)
    X = X.values
    y = initial_dataset['CarbonEmission']
    y = y.values

    # Split dataset into training and testing sets
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    scaler.fit(X_train)
    # X_train = scaler.transform(X_train)
    # X_test = scaler.transform(X_test)

    # Train a model on the training set and save it to a file
        
    # mlp = MLPRegressor(hidden_layer_sizes=(100, 100), max_iter=1000, random_state=42, verbose=True)
    # mlp.fit(X_train, y_train)
    # with open('model.pkl', 'wb') as f:
    #     pickle.dump(mlp, f)

    # Evaluate the model on the testing set
        
    # train_preds = mlp.predict(X_train)
    # train_mse = mean_squared_error(y_train, train_preds)
    # train_rmse = sqrt(train_mse)
    # train_r2 = r2_score(y_train, train_preds)
    # print("RMSE(train): ", train_rmse)
    # print("R2(train): ", train_r2)
    # test_preds = mlp.predict(X_test)
    # test_mse = mean_squared_error(y_test, test_preds)
    # test_rmse = sqrt(test_mse)
    # test_r2 = r2_score(y_test, test_preds)
    # print("RMSE(test): ", test_rmse)
    # print("R2(test): ", test_r2)
        
    with open('model.pkl', 'rb') as f:
        mlp = pickle.load(f)

    new_data_point = np.array([
        body_type,
        sex,
        diet,
        how_often_shower,
        heating_energy_source,
        transport,
        vehicle_type,
        social_activity,
        monthly_grocery_bill,
        frequency_traveling_by_air,
        vehicle_monthly_distance_km,
        waste_bag_size,
        waste_bag_weekly_count,
        how_long_tv_pc_daily_hour,
        how_many_new_clothes_monthly,
        how_long_internet_daily_hour,
        energy_efficiency
    ])

    new_data_point = scaler.transform(new_data_point.reshape(1, -1))

    carbon_emission = mlp.predict(new_data_point)
    carbon_emission = carbon_emission[0]
    return f"Your estimated monthly carbon footprint is {carbon_emission:.2f} kg of CO2."

def calculate_bmi(height, weight):
    # Convert height from centimeters to meters
    height_in_meters = height / 100
    
    # Calculate BMI
    bmi = weight / (height_in_meters ** 2)
    
    return bmi

def determine_body_type(height, weight):
    bmi = calculate_bmi(height, weight)
    
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# Input Data Nodes configuration
initial_dataset_cfg = Config.configure_data_node(id="initial_dataset",
                                                 storage_type="csv",
                                                 path="data/carbon_emission.csv",
                                                 scope=Scope.GLOBAL)

height_cfg = Config.configure_data_node(id="height_node", default_data="", scope=Scope.GLOBAL)

weight_cfg = Config.configure_data_node(id="weight_node", default_data="", scope=Scope.GLOBAL)

sex_cfg = Config.configure_data_node(id="sex_node", default_data="", scope=Scope.GLOBAL)

diet_cfg = Config.configure_data_node(id="diet_node", default_data="", scope=Scope.GLOBAL)

how_often_shower_cfg = Config.configure_data_node(id="how_often_shower_node", default_data="", scope=Scope.GLOBAL)

heating_energy_source_cfg = Config.configure_data_node(id="heating_energy_source_node", default_data="", scope=Scope.GLOBAL)

transport_cfg = Config.configure_data_node(id="transport_node", default_data="", scope=Scope.GLOBAL)

vehicle_type_cfg = Config.configure_data_node(id="vehicle_type_node", default_data="", scope=Scope.GLOBAL)

vehicle_monthly_distance_km_cfg = Config.configure_data_node(id="vehicle_monthly_distance_km_node", default_data="", scope=Scope.GLOBAL)

social_activity_cfg = Config.configure_data_node(id="social_activity_node", default_data="", scope=Scope.GLOBAL)

monthly_grocery_bill_cfg = Config.configure_data_node(id="monthly_grocery_bill_node", default_data="", scope=Scope.GLOBAL)

frequency_traveling_by_air_cfg = Config.configure_data_node(id="frequency_traveling_by_air_node", default_data="", scope=Scope.GLOBAL)

waste_bag_size_cfg = Config.configure_data_node(id="waste_bag_size_node", default_data="", scope=Scope.GLOBAL)

waste_bag_weekly_count_cfg = Config.configure_data_node(id="waste_bag_weekly_count_node", default_data="", scope=Scope.GLOBAL)

how_long_tv_pc_daily_hour_cfg = Config.configure_data_node(id="how_long_tv_pc_daily_hour_node", default_data="", scope=Scope.GLOBAL)

how_many_new_clothes_monthly_cfg = Config.configure_data_node(id="how_many_new_clothes_monthly_node", default_data="", scope=Scope.GLOBAL)

how_long_internet_daily_hour_cfg = Config.configure_data_node(id="how_long_internet_daily_hour_node", default_data="", scope=Scope.GLOBAL)

energy_efficiency_cfg = Config.configure_data_node(id="energy_efficiency_node", default_data="", scope=Scope.GLOBAL)

recycling_cfg = Config.configure_data_node(id="recycling_node", default_data="", scope=Scope.GLOBAL)

cooking_with_cfg = Config.configure_data_node(id="cooking_with_node", default_data="", scope=Scope.GLOBAL)

# Output Data Node configuration
carbon_emission_cfg = Config.configure_data_node(id="carbon_emission",
                                                 scope=Scope.GLOBAL)


# Task configuration
calculate_task_cfg = Config.configure_task(id="calculate_carbon_emission",
                                            function=calculate_carbon_emission,
                                            input=[initial_dataset_cfg, height_cfg, weight_cfg, sex_cfg, diet_cfg, how_often_shower_cfg, heating_energy_source_cfg, transport_cfg, vehicle_type_cfg, vehicle_monthly_distance_km_cfg, social_activity_cfg, monthly_grocery_bill_cfg, frequency_traveling_by_air_cfg, waste_bag_size_cfg, waste_bag_weekly_count_cfg, how_long_tv_pc_daily_hour_cfg, how_many_new_clothes_monthly_cfg, how_long_internet_daily_hour_cfg, energy_efficiency_cfg, recycling_cfg, cooking_with_cfg],
                                            output=carbon_emission_cfg,
                                            skippable=True)

# Scenario configuration
scenario_cfg = Config.configure_scenario(id="scenario", task_configs=[calculate_task_cfg])

# Run of the Taipy Core service
tp.Core().run()

# Creation of my scenario
scenario = tp.create_scenario(scenario_cfg)



# Taipy GUI- front end definition

# Callbacks definitions

def modify_height(state):
    state.scenario.height_node.write(state.height)

def modify_weight(state):
    state.scenario.weight_node.write(state.weight)

def modify_sex(state):
    state.scenario.sex_node.write(state.sex)

def modify_diet(state):
    state.scenario.diet_node.write(state.diet)

def modify_how_often_shower(state):
    state.scenario.how_often_shower_node.write(state.how_often_shower)

def modify_heating_energy_source(state):
    state.scenario.heating_energy_source_node.write(state.heating_energy_source)

def modify_transport(state):
    state.scenario.transport_node.write(state.transport)

def modify_vehicle_type(state):
    state.scenario.vehicle_type_node.write(state.vehicle_type)

def modify_vehicle_monthly_distance_km(state):
    state.scenario.vehicle_monthly_distance_km_node.write(state.vehicle_monthly_distance_km)

def modify_social_activity(state):
    state.scenario.social_activity_node.write(state.social_activity)

def modify_monthly_grocery_bill(state):
    state.scenario.monthly_grocery_bill_node.write(state.monthly_grocery_bill)

def modify_frequency_traveling_by_air(state):
    state.scenario.frequency_traveling_by_air_node.write(state.frequency_traveling_by_air)

def modify_waste_bag_size(state):
    state.scenario.waste_bag_size_node.write(state.waste_bag_size)

def modify_waste_bag_weekly_count(state):
    state.scenario.waste_bag_weekly_count_node.write(state.waste_bag_weekly_count)

def modify_how_long_tv_pc_daily_hour(state):
    state.scenario.how_long_tv_pc_daily_hour_node.write(state.how_long_tv_pc_daily_hour)

def modify_how_many_new_clothes_monthly(state):
    state.scenario.how_many_new_clothes_monthly_node.write(state.how_many_new_clothes_monthly)

def modify_how_long_internet_daily_hour(state):
    state.scenario.how_long_internet_daily_hour_node.write(state.how_long_internet_daily_hour)

def modify_energy_efficiency(state):
    state.scenario.energy_efficiency_node.write(state.energy_efficiency)

def modify_recycling(state):
    state.scenario.recycling_node.write(state.recycling)

def modify_cooking_with(state):
    state.scenario.cooking_with_node.write(state.cooking_with)

def calculate(state):
    state.scenario.submit()
    new_footprint = scenario.carbon_emission.read()
    state.footprint = new_footprint
    if str(new_footprint).startswith('Your'):
        state.advices = "True"

# Initialization of variables

footprint = None

advices = "False"

height = None

weight = None

sex = None

diet = None

how_often_shower = None

heating_energy_source = None

transport = None

vehicle_type = None

vehicle_monthly_distance_km = None

social_activity = None

monthly_grocery_bill = None

frequency_traveling_by_air = None

waste_bag_size = None

waste_bag_weekly_count = None

how_long_tv_pc_daily_hour = None

how_many_new_clothes_monthly = None

how_long_internet_daily_hour = None

energy_efficiency = None

recycling = None

cooking_with = None

html_page = Html("""
<h1>Carbon Footprint Calculator</h1>

<taipy:expandable title="Personal Information">
                 
    <taipy:part>
        <taipy:number label="Height (cm)" on_change={modify_height}>{height}</taipy:number>
    </taipy:part>
                 
    <taipy:part height="1em" />
                 
    <taipy:part>
        <taipy:number label="Weight (kg)" on_change={modify_weight}>{weight}</taipy:number>
    </taipy:part>
                 
    <taipy:part height="1em" />
                 
    <taipy:part>
        <taipy:selector lov="Female;Male" dropdown="True" multiple="False" label="Gender" on_change={modify_sex}>{sex}</taipy:selector>
    </taipy:part>

    <taipy:part height="1em" />
                 
    <taipy:layout>

        <taipy:part>
            <taipy:selector lov="Omnivore;Pescatarian;Vegetarian;Vegan" dropdown="True" multiple="False" label="Diet" on_change={modify_diet}>{diet}</taipy:selector>
        </taipy:part>
                 
        <ul>
            <li>Omnivore: eat and survive on both plant and animal matter</li>
            <li>Pescatarian: consumption of fish and shellfish to the exclusion of land-based meats</li>
            <li>Vegetarian: abstaining from the consumption of meat and all by-products of animal slaughter</li>
            <li>Vegan: a plant-based diet avoiding all animal foods such as meat, dairy, eggs and honey</li>
        </ul>

    </taipy:layout>
                 
    <taipy:part height="1em" />
                 
    <taipy:layout>

        <taipy:part>
            <taipy:selector lov="Never;Often;Sometimes" dropdown="True" multiple="False" label="Social Activity" on_change={modify_social_activity}>{social_activity}</taipy:selector>
        </taipy:part>
    
        <p>Frequency of participating in social activities (go out)</p>
                 
    </taipy:layout>
                 
</taipy:expandable>
                 
<taipy:expandable title="Travel Information">
                 
    <taipy:layout>

        <taipy:part>
            <taipy:selector lov="Public;Private;Walk/Bicycle" dropdown="True" multiple="False" label="Transportation" on_change={modify_transport}>{transport}</taipy:selector>
        </taipy:part>
    
        <p>Which transportation method do you use the most ?</p>
                 
    </taipy:layout>

    <taipy:part height="1em" />

    <taipy:layout>

        <taipy:part>
            <taipy:selector lov="Petrol;Diesel;Hybrid;Lpg;Electric;Not Applicable" dropdown="True" multiple="False" label="Vehicle Type" on_change={modify_vehicle_type}>{vehicle_type}</taipy:selector>
        </taipy:part>
    
        <div>
            <p>What type of fuel do you use in your transportation ?</p>
            <p>Choose "Not Applicable" if your transportation is not "Private"</p>         
        </div>
                 
    </taipy:layout>

    <taipy:part height="1em" />
                 
    <taipy:layout>

        <div>
            <p>What is the monthly distance traveled by the transportation ? (km)</p>
            <taipy:slider min="0" max="10000" on_change={modify_vehicle_monthly_distance_km}>{vehicle_monthly_distance_km}</taipy:slider>         
        </div>
                 
        <p>Leave to "0" if your transportation is "Walk/Bicycle"</p>
                 
    </taipy:layout>

    <taipy:part height="1em" />
                 
    <taipy:part>
        <taipy:selector lov="Never;Rarely;Frequently;Very Frequently" dropdown="True" multiple="False" label="How often do you fly" on_change={modify_frequency_traveling_by_air}>{frequency_traveling_by_air}</taipy:selector>
    </taipy:part>

</taipy:expandable>
                 
<taipy:expandable title="Waste Information">
                 
    <div>
        <p>What is the size of your waste bag ?</p>
        <taipy:selector lov="Small;Medium;Large;Extra Large" label="Choose one" dropdown="True" multiple="False" on_change={modify_waste_bag_size}>{waste_bag_size}</taipy:selector>
    </div>
                 
    <taipy:part height="1em" />
                 
    <div>
        <p>How many waste bags do you trash out in a week ?</p>
        <taipy:slider min="0" max="7" on_change={modify_waste_bag_weekly_count}>{waste_bag_weekly_count}</taipy:slider>         
    </div>

    <taipy:part height="1em" />

    <div>
        <p>Do you recycle any materials below ?</p>
        <taipy:selector lov="Plastic;Paper;Metal;Glass" label="Choose all that apply" dropdown="True" multiple="True" on_change={modify_recycling}>{recycling}</taipy:selector>        
    </div>

</taipy:expandable>
                 
<taipy:expandable title="Energy Information">
                 
    <div>
        <p>What power source do you use for heating ?</p>
        <taipy:selector lov="Natural Gas;Electricity;Wood;Coal" label="Choose one" dropdown="True" multiple="False" on_change={modify_heating_energy_source}>{heating_energy_source}</taipy:selector>
    </div>
                 
    <taipy:part height="1em" />
                 
    <div>
        <p>What cooking systems do you use ?</p>
        <taipy:selector lov="Microwave;Oven;Grill;Airfryer;Stove" label="Choose all that apply" dropdown="True" multiple="True" on_change={modify_cooking_with}>{cooking_with}</taipy:selector>        
    </div>
                 
    <taipy:part height="1em" />
                 
    <div>
        <p>Do you consider the energy efficiency of electronic devices ?</p>
        <taipy:selector lov="No;Yes;Sometimes" label="Choose one" dropdown="True" multiple="False" on_change={modify_energy_efficiency}>{energy_efficiency}</taipy:selector>
    </div>
                 
    <taipy:part height="1em" />
                 
    <div>
        <p>How many hours a day do you spend in front of your PC/TV ?</p>
        <taipy:slider min="0" max="24" on_change={modify_how_long_tv_pc_daily_hour}>{how_long_tv_pc_daily_hour}</taipy:slider>         
    </div>

    <taipy:part height="1em" />
                 
    <div>
        <p>What is your daily internet usage in hours ?</p>
        <taipy:slider min="0" max="24" on_change={modify_how_long_internet_daily_hour}>{how_long_internet_daily_hour}</taipy:slider>         
    </div>

</taipy:expandable>
                 
<taipy:expandable title="Consumption Information">
                 
    <div>
        <p>How often do you take a shower ?</p>
        <taipy:selector lov="Daily;Twice a day;More frequently;Less frequently" label="Choose one" dropdown="True" multiple="False" on_change={modify_how_often_shower}>{how_often_shower}</taipy:selector>
    </div>
                 
    <taipy:part height="1em" />
                 
    <div>
        <p>Monthly grocery spending in $</p>
        <taipy:slider min="0" max="300" on_change={modify_monthly_grocery_bill}>{monthly_grocery_bill}</taipy:slider>         
    </div>

    <taipy:part height="1em" />
                 
    <div>
        <p>How many clothes do you buy monthly ?</p>
        <taipy:slider min="0" max="50" on_change={modify_how_many_new_clothes_monthly}>{how_many_new_clothes_monthly}</taipy:slider>         
    </div>

</taipy:expandable>
                 
<taipy:part height="1em" />
                 
<taipy:button on_action={calculate}>Calculate</taipy:button>
                 
<taipy:part height="1em" />
                 
<taipy:text>{footprint}</taipy:text>
                 
<taipy:part render={advices}>
    <p>Here are some advices to reduce your carbon footprint :</p>             
    <ul>
        <li>Stop Eating (or Eat Less) Meat</li>
        <li>Unplug Unused Electronics</li>
        <li>Drive Less</li>
        <li>Fly Less</li>
        <li>Plant a Garden</li>
        <li>Eat Local (and Organic)</li>
        <li>Wash Clothes in Cold Water</li>
        <li>Line-Dry Your Clothes</li>
        <li>Switch to Sustainable, Clean Energy</li>
        <li>Recycle as Much as Possible</li>
    </ul>          
</taipy:part>
                 
<taipy:part height="1em" />
                 
""")

# run the app
Gui(page=html_page).run()