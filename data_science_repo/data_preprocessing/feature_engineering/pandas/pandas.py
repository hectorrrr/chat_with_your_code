import pandas as pd
import numpy as np



def remove_outliers(df, columns,  threshold=3):
    """
    Removes outliers from the DataFrame.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (list): List of columns to remove outliers from.
        method (str): Method to detect outliers ('zscore' or 'iqr').
    
    Returns:
        pd.DataFrame: DataFrame with outliers removed.
    """
    Q1 = df[columns].quantile(0.25)
    Q3 = df[columns].quantile(0.75)
    IQR = Q3 - Q1
    return df[~((df[columns] < (Q1 - threshold * IQR)) | (df[columns] > (Q3 + threshold * IQR))).any(axis=1)]


def encode_categorical(df, columns, drop_first=True):
    """
    Encodes categorical variables using one-hot encoding.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (list): List of columns to encode.
        drop_first (bool): Whether to drop the first level to avoid multicollinearity.
    
    Returns:
        pd.DataFrame: DataFrame with categorical variables encoded.
    """
    return pd.get_dummies(df, columns=columns, drop_first=drop_first)

def extract_datetime_features(df, column, features=['year', 'month', 'day', 'hour']):
    """
    Extracts features from a datetime column.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        column (str): Name of the datetime column.
        features (list): List of features to extract ('year', 'month', 'day', 'hour', 'minute', 'second').
    
    Returns:
        pd.DataFrame: DataFrame with datetime features extracted.
    """
    df[column] = pd.to_datetime(df[column])
    if 'year' in features:
        df[f"{column}_year"] = df[column].dt.year
    if 'month' in features:
        df[f"{column}_month"] = df[column].dt.month
    if 'day' in features:
        df[f"{column}_day"] = df[column].dt.day
    if 'hour' in features:
        df[f"{column}_hour"] = df[column].dt.hour
    if 'minute' in features:
        df[f"{column}_minute"] = df[column].dt.minute
    if 'second' in features:
        df[f"{column}_second"] = df[column].dt.second
    return df