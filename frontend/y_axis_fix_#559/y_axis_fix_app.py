from taipy import Gui

def create_heatmap(data, x_axis, y_axis, z_axis):
    """
    Create and display a heatmap using the provided data and axis labels.

    Parameters:
    - data (dict): A dictionary containing the data for the heatmap.
    - x_axis (str): The key in the data dictionary for the x-axis labels.
    - y_axis (str): The key in the data dictionary for the y-axis labels.
    - z_axis (str): The key in the data dictionary for the z-axis values.
    """
    # Calculate the maximum length of the y-axis labels
    max_length = max(len(label) for label in data[y_axis])

    # Set a dynamic margin based on the maximum length of the y-axis labels
    dynamic_margin = max_length * 10  # Adjust margin based on label length

    # Define the layout with the dynamic margin
    layout = {"margin": {"l": dynamic_margin}}

    # Create the markdown string for the heatmap chart
    md = f"<|{{data}}|chart|type=heatmap|z={z_axis}|x={x_axis}|y={y_axis}|layout={{layout}}|>"

    # Initialize and run the GUI with the defined markdown string
    Gui(md).run()

# Example usage
data = {
    "Temperatures": [
        [17.2, 27.4, 28.6, 21.5],  # Temperatures for the United Kingdom
        [5.6, 15.1, 20.2, 8.1],    # Temperatures for the United States
        [26.6, 22.8, 21.8, 24.0],  # Temperatures for Brazil
        [22.3, 15.5, 13.4, 19.6]   # Temperatures for Germany
    ],
    "Countries": [
        "United Kingdom United Kingdom United Kingdom United Kingdom United Kingdom United Kingdom", 
        "United States United States", 
        "Brazil", 
        "Germany"
    ],
    "Seasons": ["Winter", "Spring", "Summer", "Autumn"]
}

# Call the function with the example data
create_heatmap(data, x_axis="Seasons", y_axis="Countries", z_axis="Temperatures")
