from taipy.gui import Markdown
no_of_prod = 0
amt_one_pro= 0
cost_of_making_one_p = 0
net_amount = 0

def clear_out1(state):
    state.no_of_prod = 0

def clear_out2(state):
    state.amt_one_pro = 0

def clear_out3(state):
    state.cost_of_making_one_p = 0


def net_amt(state):
   n = state.no_of_prod
   a = state.amt_one_pro
   c = state.cost_of_making_one_p
   net_amount = (n * a) - (n * c)
   state.net_amount = net_amount # Update the state variable
   return net_amount

def on_action(state, action):
  if action == "net_amount":
    net_amt(state)


calc_ui = """
<h1><div style="text-align: center;">
<span style="color: #B7C9F2;">SALES CALCULATOR</span>
</div></h1>
<|1 1 1 |layout|
<|card|
<total_Product|
#### **Number of products sold**:
<|{no_of_prod}|number|>
<br/>
<br/>
<|Clear|button|class_name=blueButton|on_action=clear_out1|>
|total_Product>
|>

<|card|
<amount|
####  **Amount of One Product**:
<|{amt_one_pro}|number|>
<br/>
<br/>
<|Clear|button|class_name=blueButton|on_action=clear_out2|>
|amount>
|>

<|card|
<amount_p|
#### **Cost of making one Product**:
<|{cost_of_making_one_p}|number|>
<br/>
<br/>
<|Clear|button|class_name=blueButton|on_action=clear_out3|>
|amount_p>
|>
|>


<br/>
<|card|
<|text-center |
##**TOTAL Earning From Product Sale:**
<|{net_amount}|text|>

<br/>
<br/>
<|Calculate|button|on_action=net_amt|>
|>
|>
<hr/>

<h1><div style="text-align: center;">
<span style="color: #B7C9F2;">Strategies to increase sales revenue</span>
</div></h1>
* **Find new customers**—<br/>new customers can help grow your business.<br/><br/>
* **Develop new product lines**—<br/>ask your customers about what new products or services they are interested in.<br/><br/>
* **Focus on your most profitable customers**—<br/>it may be more profitable to sell fewer products to higher spending customers than to focus on increasing sales volume alone.<br/><br/>
* **Work with your best customers**—<br/>find out who your best customers are, what they buy and when they buy it. You can use this information to market and advertise to them more effectively.<br/><br/>
* **Up-sell and cross sell**—<br/>persuade your customers of the benefits of your more profitable products and pitch additional products.<br/><br/>
* **Find new markets**—<br/>use market research to see if there are opportunities to expand into new areas.<br/><br/>
* **Customer service**—<br/>improve your customer service and develop a staff training program.<br/><br/>
* **Increase your prices**—<br/>review the prices of products regularly and adjust accordingly. You may increase a small amount at a time.<br/><br/>
* **Price discounts**—<br/>consider price discounts and promotions to increase your customer base (e.g. 2-for-1 deals or happy hour).<br/><br/>
* **Increase productivity of your staff**—<br/>recognise and reward staff with staff performance reviews. Regularly upskill and educate staff with training.<br/><br/>
* **Retail displays**—<br/>use effective retail displays to increase sales.<br/><br/>

<|1 1 1 |layout|



<br/>

<|text-center |
<|card|
## "A Small Profit<br/>
## is better than<br/>
## a Big Loss"<br/>
    -Ron Rash
|>
|>
"""
