import plotly.express as px


def violin_plot(dataframe, value_column, group_column=None):
    """
    Generates a violin plot for the specified column in a pandas DataFrame.

    Parameters:
    - dataframe (pd.DataFrame): The DataFrame containing the data.
    - value_column (str): The column name of the DataFrame to be plotted.
    - group_column (str, optional): The column name for grouping data into different violins.

    Returns:
    - fig (plotly.graph_objects.Figure): The Plotly figure object for the violin plot.
    """
    if group_column:
        fig = px.violin(dataframe, y=value_column, x=group_column, box=True, points="all")
    else:
        fig = px.violin(dataframe, y=value_column, box=True, points="all")

    fig.update_layout(title=f'Violin Plot of {value_column} by {group_column}' if group_column else f'Violin Plot of {value_column}')
    return fig