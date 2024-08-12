import plotly.figure_factory as ff




def plot_confusion_matrix(confusion_matrix, class_names):
    """
    Generates a confusion matrix plot from a sklearn confusion matrix object.

    Parameters:
    - confusion_matrix (array): Numpy array containing the confusion matrix information.
    - class_names (list of str): List of class names corresponding to the labels.

    Returns:
    - fig (plotly.graph_objects.Figure): The Plotly figure object for the confusion matrix plot.
    """
    fig = ff.create_annotated_heatmap(
        z=confusion_matrix,
        x=class_names,
        y=class_names,
        colorscale='Blues',
        showscale=True
    )
    fig.update_layout(title='Confusion Matrix', xaxis_title='Predicted Label', yaxis_title='True Label')
    fig.update_traces(text=confusion_matrix.astype(str), texttemplate='%{text}')
    return fig

