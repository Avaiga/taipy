from taipy import Gui
from taipy.gui import Html, navigate
import taipy.gui.builder as tgb
import data
import csv
import graphs
oddEvencontent = """
<|toggle|theme|>
<h1>Welcome To the Odd-Even Zone</h1>
<p style="font-size:18px;">Implementing the odd-even rule can help reduce traffic congestion and improve air quality.</p>
<p style="margin-bottom:30px; font-size:18px;">Choose an activity to learn more about the odd-even rule:</p>

<|Understanding the Rule|button|id=understandSubmit|on_action=on_action|>
<div style="display: flex; justify-center">
    <img style="margin-bottom: 20px; margin-top: 15px; width: 200px; height: auto; margin-right: 20px;" src='images/OE.jpg' alt="Description of the image"></img>
    <p style="font-size:24px;">Understanding the odd-even rule is the first step. It's a system where vehicles with odd and even number plates are allowed on the roads on alternate days.</p>
</div>
<|Benefits of the Rule|button|id=benefitsSubmit|on_action=on_action|>
<div style="display: flex; justify-center">
    <img style="margin-bottom: 20px; margin-top: 15px; width: 200px; height: auto; margin-right: 20px;" src="images/oddeven.jpg" alt="Description of the image"></img>
    <p style="font-size:24px;">The odd-even rule can have several benefits, including reduced traffic congestion, lower air pollution levels, and increased use of public transportation.</p>
</div>
<|Challenges of the Rule|button|id=challengeSubmit|on_action=on_action|>
<div style="display: flex; justify-center">
    <img style="margin-bottom: 20px; margin-top: 15px; width: 200px; height: auto; margin-right: 20px;" src="images/challenges.png" alt="Description of the image"></img>
    <p style="font-size:24px;">While the odd-even rule has its benefits, it also comes with challenges. These can include enforcement issues, public compliance, and the need for robust public transportation systems.</p>
</div>

"""