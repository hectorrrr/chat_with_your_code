import torch.nn as nn



class SimpleClassifier(nn.Module):
    """
    Simple neural network classifier.

    Attributes:
        input_dim (int): Dimension of input features.
        output_dim (int): Number of output classes.
    """
    def __init__(self, input_dim, output_dim):
        """
        Initializes the classifier with input and output dimensions.

        Args:
            input_dim (int): Dimension of input features.
            output_dim (int): Number of output classes.
        """
        super(SimpleClassifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_dim)
        self.relu = nn.ReLU()

    def forward(self, x):
        """
        Defines the forward pass of the network.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor with class scores.
        """
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x