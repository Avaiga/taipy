from data.data import data as dataset


def bar_graph(district):
    df = dataset

    filtered_data = df[df['District'] == district]
    # Reset index for proper x-axis positioning
    filtered_data = filtered_data.reset_index(drop=True)

    # Create layout
    layout = {
        "title": f'Male and Female Population in {district}',
        "xaxis": dict(title='District'),
        "yaxis": dict(title='Population'),
        "barmode": 'group'  # 'group' for grouped bar chart, 'overlay' for overlaid bar chart
    }

    return filtered_data, layout


def bubble_chart(district_name):
    df = dataset
    # Filter data for the specified district
    district_data = df[df['District'] == district_name]

    bubble_size = district_data['Total population'] * 0.001

    data = {
        "Total Male": district_data['Total Male'].to_list(),
        "Total Female": district_data['Total Female'].to_list(),
        "Texts": district_data['Local Level Name'].to_list()
    }

    marker = {
        "size": bubble_size.to_list(),  # Scale bubble size
        "color": district_data.index,
        "colorscale": 'viridis'
    }

    # Show the bubble chart
    return data, marker


def overlayed_chart(district_name):
    df = dataset
    # Filter data for the specified district
    district_data = df[df['District'] == district_name]

    data = {
        "Local Level Name": district_data['Local Level Name'],
        "Total Male": district_data['Total Male'],
        "Total Female": district_data['Total Female'],
        "Total Family Member": district_data['Total family number'],
        "Total Household Number": district_data['Total household number'],
    }

    return data, ['Total Male', "Total Female", "Total Family Member", "Total Household Number"], {"stackgroup": "first_group"}
