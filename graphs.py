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
