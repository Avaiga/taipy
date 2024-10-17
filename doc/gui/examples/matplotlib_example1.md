# Taipy Example for Matplotlib Integration

### Sample Code:
```python:
import matplotlib.pyplot as plt
import numpy as np

import taipy.gui.builder as tgb
from taipy.gui import Gui

# Basic Line Plot in Matplotlib
fig = plt.figure(figsize=(5, 4))
x = [1, 2, 3, 4, 5]
y = [2, 4, 5, 3, 6]
plot = fig.subplots(1, 1)
plot.plot(x, y, color='red', linestyle='--', marker='o', label='Data')
plot.set_xlabel("X-axis")
plot.set_ylabel("Y-axis")
plot.set_title("Customized Line Plot")
plot.legend()

# Create a Taipy Page
with tgb.Page() as page:
    tgb.part(content="{fig}", height="520px")

# Run the Taipy Application:
if __name__ == "__main__":
    Gui(page=page).run(title="Matplotlib Examples")
```

