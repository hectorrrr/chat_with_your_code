import pandas as pd
import numpy as np
from scipy.stats import zscore
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

from sklearn.feature_extraction.text import TfidfVectorizer


def scale_features(df, columns):
    """
    Scales numerical features using standard scaling (z-score normalization).
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (list): List of columns to scale.
    
    Returns:
        pd.DataFrame: DataFrame with scaled features.
    """
    scaler = StandardScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df



def create_polynomial_features(df, columns, degree=2):
    """
    Creates polynomial features from the specified columns.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (list): List of columns to create polynomial features from.
        degree (int): The degree of the polynomial features.
    
    Returns:
        pd.DataFrame: DataFrame with polynomial features added.
    """
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    poly_features = poly.fit_transform(df[columns])
    poly_feature_names = poly.get_feature_names_out(columns)
    poly_df = pd.DataFrame(poly_features, columns=poly_feature_names, index=df.index)
    return pd.concat([df, poly_df], axis=1)




    


def vectorize_text(df, column, max_features=1000):
    """
    Converts text data into TF-IDF vectors.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        column (str): The column containing text data.
        max_features (int): The maximum number of features to consider.
    
    Returns:
        pd.DataFrame: DataFrame with text data vectorized.
    """
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(df[column])
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out(), index=df.index)
    return pd.concat([df, tfidf_df], axis=1)