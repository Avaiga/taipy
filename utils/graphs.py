from data.data import data as dataset
import random


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


def overlayed_chart(district_name):
    df = dataset
    # Filter data for the specified district
    district_data = df[df['District'] == district_name]

    data = {
        "Local Level Name": district_data['Local Level Name'],
        "Total Male": district_data['Total Male'].to_list(),
        "Total Female": district_data['Total Female'].to_list(),
        "Total Family Member": district_data['Total family number'].to_list(),
        "Total Household Number": district_data['Total household number'].to_list(),
    }

    return data, ['Total Male', "Total Female", "Total Family Member", "Total Household Number"], {"stackgroup": "first_group"}


def radar_chart(district_name):
    df = dataset
    # Filter data for the specified district
    district_data = df[df['District'] == district_name]

    # Sum up the values for the specified columns
    total_family_number = district_data['Total family number'].sum()
    total_household_number = district_data['Total household number'].sum()
    total_male = district_data['Total Male'].sum()
    total_female = district_data['Total Female'].sum()

    # Categories and values for the radar chart
    categories = [
        'Total family number',
        'Total household number',
        'Total Male',
        'Total Female'
    ]
    values = [
        total_family_number,
        total_household_number,
        total_male,
        total_female
    ]

    data = {
        "r": values + [values[0]],
        "theta": categories + [categories[0]],

    }

    options = {"fill": "toself", "name": district_name}

    layout = {
        "polar": {
            "radialaxis": dict(
                visible=False,
                range=[0, max(values) + 1000]  # Adjust the range as needed
            )
        },
        "showlegend": True,
        "title": f'Radar Chart for {district_name}'
    }

    return data, options, layout


def pie_chart(district_name):
    df = dataset
    district_data = df[df['District'] == district_name]

    # Group data by Local Level Name and calculate total population for each local level
    local_level_population = district_data.groupby(
        'Local Level Name')['Total population'].sum().reset_index()

    data = {
        "values": local_level_population['Total population'].to_list(),
        "labels": local_level_population['Local Level Name'].to_list()
    }
    return data


def bubble_chart_whole():
    df = dataset

    aggregated_data = df.groupby('District').agg({
        'Total Male': 'sum',
        'Total Female': 'sum',
        'Total population': 'sum'
    }).reset_index()

    # Scale the bubble size for better visualization
    scale_factor = 0.0001
    bubble_size = aggregated_data['Total population'] * scale_factor

    data = {
        "Total Male": aggregated_data['Total Male'].to_list(),
        "Total Female": aggregated_data['Total Female'].to_list(),
        "Texts": aggregated_data['District'].to_list(),
    }

    marker = {
        "size": bubble_size.to_list(),
        "color": aggregated_data.index.to_list(),
        "colorscale": "viridis",
    }

    # Customize the layout
    layout = {
        "title": 'Bubble Chart: Aggregated Male vs Female Population by District',
        "xaxis": dict(title='Total Male Population'),
        "yaxis": dict(title='Total Female Population'),
        "legend": dict(title='District')
    }
    return data, marker, layout


def treemap_whole():
    df = dataset
    # Group data by District name and calculate total population for each district
    district_population = df.groupby(
        'District')['Total population'].sum().reset_index()

    # Aggregate population for each district
    aggregated_data = district_population.groupby(
        'District')['Total population'].sum().reset_index()

    # Sort by total population in descending order
    aggregated_data = aggregated_data.sort_values(
        by='Total population', ascending=False)

    data = {"label": aggregated_data['District'].to_list(),
            "parents": ['']*len(aggregated_data),
            "values": aggregated_data['Total population'].to_list()}
    # Update layout for the Treemap

    layout = {"title": "Treemap of Districts in Nepal by Total Population"}
    # Show the Treemap
    return data


def bar_graph_whole():
    df = dataset

    # Group by district and sum the Male and Female populations
    grouped_data = df.groupby('District', as_index=False).agg({
        'Total Male': 'sum',
        'Total Female': 'sum'
    })

    layout = {
        "title": 'Total Male and Female Population of Nepal',
        "xaxis": dict(title='District'),
        "yaxis": dict(title='Population'),
        "barmode": 'group'
    }

    return grouped_data, layout


def overlayed_chart_whole():
    df = dataset

    grouped_data = df.groupby('District', as_index=False).agg({
        'Total Male': 'sum',
        'Total Female': 'sum',
    })

    data = {
        "District": grouped_data['District'].to_list(),
        "Total Male": grouped_data['Total Male'].to_list(),
        "Total Female": grouped_data['Total Female'].to_list(),
    }

    return data, ['Total Male', "Total Female"], {"stackgroup": "first_group"}
