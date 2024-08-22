# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
# -----------------------------------------------------------------------------------------
# To execute this script, make sure that the taipy-gui package is installed in your
# Python environment and run:
#     python <script>
# -----------------------------------------------------------------------------------------
import numpy
import pandas

from taipy.gui import Gui

if __name__ == "__main__":
    # Largest cities: name, location and population
    # Source: https://simplemaps.com/data/world-cities
    cities = [
        {"name": "Tokyo", "lat": 35.6839, "lon": 139.7744, "population": 39105000},
        {"name": "Jakarta", "lat": -6.2146, "lon": 106.8451, "population": 35362000},
        {"name": "Delhi", "lat": 28.6667, "lon": 77.2167, "population": 31870000},
        {"name": "Manila", "lat": 14.6, "lon": 120.9833, "population": 23971000},
        {"name": "São Paulo", "lat": -23.5504, "lon": -46.6339, "population": 22495000},
        {"name": "Seoul", "lat": 37.56, "lon": 126.99, "population": 22394000},
        {"name": "Mumbai", "lat": 19.0758, "lon": 72.8775, "population": 22186000},
        {"name": "Shanghai", "lat": 31.1667, "lon": 121.4667, "population": 22118000},
        {"name": "Mexico City", "lat": 19.4333, "lon": -99.1333, "population": 21505000},
        {"name": "Guangzhou", "lat": 23.1288, "lon": 113.259, "population": 21489000},
        {"name": "Cairo", "lat": 30.0444, "lon": 31.2358, "population": 19787000},
        {"name": "Beijing", "lat": 39.904, "lon": 116.4075, "population": 19437000},
        {"name": "New York", "lat": 40.6943, "lon": -73.9249, "population": 18713220},
        {"name": "Kolkāta", "lat": 22.5727, "lon": 88.3639, "population": 18698000},
        {"name": "Moscow", "lat": 55.7558, "lon": 37.6178, "population": 17693000},
        {"name": "Bangkok", "lat": 13.75, "lon": 100.5167, "population": 17573000},
        {"name": "Dhaka", "lat": 23.7289, "lon": 90.3944, "population": 16839000},
        {"name": "Buenos Aires", "lat": -34.5997, "lon": -58.3819, "population": 16216000},
        {"name": "Ōsaka", "lat": 34.752, "lon": 135.4582, "population": 15490000},
        {"name": "Lagos", "lat": 6.45, "lon": 3.4, "population": 15487000},
        {"name": "Istanbul", "lat": 41.01, "lon": 28.9603, "population": 15311000},
        {"name": "Karachi", "lat": 24.86, "lon": 67.01, "population": 15292000},
        {"name": "Kinshasa", "lat": -4.3317, "lon": 15.3139, "population": 15056000},
        {"name": "Shenzhen", "lat": 22.535, "lon": 114.054, "population": 14678000},
        {"name": "Bangalore", "lat": 12.9791, "lon": 77.5913, "population": 13999000},
        {"name": "Ho Chi Minh City", "lat": 10.8167, "lon": 106.6333, "population": 13954000},
        {"name": "Tehran", "lat": 35.7, "lon": 51.4167, "population": 13819000},
        {"name": "Los Angeles", "lat": 34.1139, "lon": -118.4068, "population": 12750807},
        {"name": "Rio de Janeiro", "lat": -22.9083, "lon": -43.1964, "population": 12486000},
        {"name": "Chengdu", "lat": 30.66, "lon": 104.0633, "population": 11920000},
        {"name": "Baoding", "lat": 38.8671, "lon": 115.4845, "population": 11860000},
        {"name": "Chennai", "lat": 13.0825, "lon": 80.275, "population": 11564000},
        {"name": "Lahore", "lat": 31.5497, "lon": 74.3436, "population": 11148000},
        {"name": "London", "lat": 51.5072, "lon": -0.1275, "population": 11120000},
        {"name": "Paris", "lat": 48.8566, "lon": 2.3522, "population": 11027000},
        {"name": "Tianjin", "lat": 39.1467, "lon": 117.2056, "population": 10932000},
        {"name": "Linyi", "lat": 35.0606, "lon": 118.3425, "population": 10820000},
        {"name": "Shijiazhuang", "lat": 38.0422, "lon": 114.5086, "population": 10784600},
        {"name": "Zhengzhou", "lat": 34.7492, "lon": 113.6605, "population": 10136000},
        {"name": "Nanyang", "lat": 32.9987, "lon": 112.5292, "population": 10013600},
        {"name": "Hyderābād", "lat": 17.3617, "lon": 78.4747, "population": 9840000},
        {"name": "Wuhan", "lat": 30.5872, "lon": 114.2881, "population": 9729000},
        {"name": "Handan", "lat": 36.6116, "lon": 114.4894, "population": 9549700},
        {"name": "Nagoya", "lat": 35.1167, "lon": 136.9333, "population": 9522000},
        {"name": "Weifang", "lat": 36.7167, "lon": 119.1, "population": 9373000},
        {"name": "Lima", "lat": -12.06, "lon": -77.0375, "population": 8992000},
        {"name": "Zhoukou", "lat": 33.625, "lon": 114.6418, "population": 8953172},
        {"name": "Luanda", "lat": -8.8383, "lon": 13.2344, "population": 8883000},
        {"name": "Ganzhou", "lat": 25.8292, "lon": 114.9336, "population": 8677600},
        {"name": "Tongshan", "lat": 34.261, "lon": 117.1859, "population": 8669000},
        {"name": "Kuala Lumpur", "lat": 3.1478, "lon": 101.6953, "population": 8639000},
        {"name": "Chicago", "lat": 41.8373, "lon": -87.6862, "population": 8604203},
        {"name": "Heze", "lat": 35.2333, "lon": 115.4333, "population": 8287693},
        {"name": "Chongqing", "lat": 29.55, "lon": 106.5069, "population": 8261000},
        {"name": "Hanoi", "lat": 21.0245, "lon": 105.8412, "population": 8246600},
        {"name": "Fuyang", "lat": 32.8986, "lon": 115.8045, "population": 8200264},
        {"name": "Changsha", "lat": 28.1987, "lon": 112.9709, "population": 8154700},
        {"name": "Dongguan", "lat": 23.0475, "lon": 113.7493, "population": 8142000},
        {"name": "Jining", "lat": 35.4, "lon": 116.5667, "population": 8081905},
        {"name": "Jinan", "lat": 36.6667, "lon": 116.9833, "population": 7967400},
        {"name": "Pune", "lat": 18.5196, "lon": 73.8553, "population": 7948000},
        {"name": "Foshan", "lat": 23.0292, "lon": 113.1056, "population": 7905700},
        {"name": "Bogotá", "lat": 4.6126, "lon": -74.0705, "population": 7743955},
        {"name": "Ahmedabad", "lat": 23.03, "lon": 72.58, "population": 7717000},
        {"name": "Nanjing", "lat": 32.05, "lon": 118.7667, "population": 7729000},
        {"name": "Changchun", "lat": 43.9, "lon": 125.2, "population": 7674439},
        {"name": "Tangshan", "lat": 39.6292, "lon": 118.1742, "population": 7577289},
        {"name": "Cangzhou", "lat": 38.3037, "lon": 116.8452, "population": 7544300},
        {"name": "Dar es Salaam", "lat": -6.8, "lon": 39.2833, "population": 7461000},
        {"name": "Hefei", "lat": 31.8639, "lon": 117.2808, "population": 7457027},
        {"name": "Hong Kong", "lat": 22.3069, "lon": 114.1831, "population": 7398000},
        {"name": "Shaoyang", "lat": 27.2418, "lon": 111.4725, "population": 7370500},
        {"name": "Zhanjiang", "lat": 21.1967, "lon": 110.4031, "population": 7332000},
        {"name": "Shangqiu", "lat": 34.4259, "lon": 115.6467, "population": 7325300},
        {"name": "Nantong", "lat": 31.9829, "lon": 120.8873, "population": 7283622},
        {"name": "Yancheng", "lat": 33.3936, "lon": 120.1339, "population": 7260240},
        {"name": "Nanning", "lat": 22.8192, "lon": 108.315, "population": 7254100},
        {"name": "Hengyang", "lat": 26.8968, "lon": 112.5857, "population": 7243400},
        {"name": "Zhumadian", "lat": 32.9773, "lon": 114.0253, "population": 7231234},
        {"name": "Shenyang", "lat": 41.8039, "lon": 123.4258, "population": 7208000},
        {"name": "Xingtai", "lat": 37.0659, "lon": 114.4753, "population": 7104103},
        {"name": "Xi’an", "lat": 34.2667, "lon": 108.9, "population": 7090000},
        {"name": "Santiago", "lat": -33.45, "lon": -70.6667, "population": 7026000},
        {"name": "Yantai", "lat": 37.3997, "lon": 121.2664, "population": 6968202},
        {"name": "Riyadh", "lat": 24.65, "lon": 46.71, "population": 6889000},
        {"name": "Luoyang", "lat": 34.6587, "lon": 112.4245, "population": 6888500},
        {"name": "Kunming", "lat": 25.0433, "lon": 102.7061, "population": 6850000},
        {"name": "Shangrao", "lat": 28.4419, "lon": 117.9633, "population": 6810700},
        {"name": "Hangzhou", "lat": 30.25, "lon": 120.1675, "population": 6713000},
        {"name": "Bijie", "lat": 27.3019, "lon": 105.2863, "population": 6686100},
        {"name": "Quanzhou", "lat": 24.9139, "lon": 118.5858, "population": 6480000},
        {"name": "Miami", "lat": 25.7839, "lon": -80.2102, "population": 6445545},
        {"name": "Wuxi", "lat": 31.5667, "lon": 120.2833, "population": 6372624},
        {"name": "Huanggang", "lat": 30.45, "lon": 114.875, "population": 6333000},
        {"name": "Maoming", "lat": 21.6618, "lon": 110.9178, "population": 6313200},
        {"name": "Nanchong", "lat": 30.7991, "lon": 106.0784, "population": 6278614},
        {"name": "Zunyi", "lat": 27.705, "lon": 106.9336, "population": 6270700},
        {"name": "Qujing", "lat": 25.5102, "lon": 103.8029, "population": 6155400},
        {"name": "Baghdad", "lat": 33.35, "lon": 44.4167, "population": 6107000},
        {"name": "Xinyang", "lat": 32.1264, "lon": 114.0672, "population": 6109106},
    ]

    # Convert to Pandas DataFrame
    data = pandas.DataFrame(cities)

    # Add a column holding the bubble size:
    #   Min(population) -> size =  5
    #   Max(population) -> size = 60
    solve = numpy.linalg.solve([[data["population"].min(), 1], [data["population"].max(), 1]], [5, 60])
    data["size"] = data["population"].apply(lambda p: p * solve[0] + solve[1])

    # Add a column holding the bubble hover texts
    # Format is "<city name> [<population>]"
    data["text"] = data.apply(lambda row: f"{row['name']} [{row['population']}]", axis=1)

    marker = {
        # Use the "size" column to set the bubble size
        "size": "size"
    }

    layout = {"geo": {"showland": True, "landcolor": "4A4"}}

    page = """
# Maps - Bubbles

<|{data}|chart|type=scattergeo|lat=lat|lon=lon|mode=markers|marker={marker}|text=text|layout={layout}|>
    """

    Gui(page).run()
