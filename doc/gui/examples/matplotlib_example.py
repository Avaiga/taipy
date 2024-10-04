# Integrating Matplotlib into Taipy using figure property

# Import Necessary Libraries:
from taipy.gui import Gui 
import taipy.gui.builder as tgb
import matplotlib.pyplot as plt  
from matplotlib.figure import Figure 
import numpy as np  

# Create a Matplotlib Figure:
fig = plt.figure(figsize =(5, 4))  
xx = np.arange(0, 2 * np.pi, 0.01)  
plot = fig.subplots(1,1)
plot.fill(xx, np.sin(xx), facecolor='none', edgecolor='purple', linewidth=2)

# Create a Taipy Page
with tgb.Page() as page:
    tgb.part(content="{fig}", height="520px")

# Run the Taipy Application:
if __name__ == "__main__":
    Gui(page=page).run(title="Matplotlib Example")