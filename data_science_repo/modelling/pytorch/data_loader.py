import torch
from torch.utils.data import Dataset


class SimpleDataset(Dataset):
    """
    Custom Dataset class for loading data from a DataFrame.

    Attributes:
        data (pd.DataFrame): The DataFrame containing the input features and labels.
        feature_columns (list): List of column names to be used as input features.
        label_column (str): The name of the column to be used as labels.
    """
    def __init__(self, data, feature_columns, label_column):
        """
        Initializes the dataset with data, feature columns, and label column.

        Args:
            data (pd.DataFrame): The DataFrame containing the input features and labels.
            feature_columns (list): List of column names to be used as input features.
            label_column (str): The name of the column to be used as labels.
        """
        self.data = data
        self.feature_columns = feature_columns
        self.label_column = label_column

    def __len__(self):
        """
        Returns the total number of samples in the dataset.

        Returns:
            int: Number of samples.
        """
        return len(self.data)

    def __getitem__(self, idx):
        """
        Retrieves the input features and label for a given index.

        Args:
            idx (int): Index of the sample to retrieve.

        Returns:
            tuple: A tuple containing the input features and label as tensors.
        """
        features = torch.tensor(self.data.iloc[idx][self.feature_columns].values, dtype=torch.float32)
        label = torch.tensor(self.data.iloc[idx][self.label_column], dtype=torch.long)
        return features, label