import torch
import torch.nn as nn
import torch.optim as optim


class Trainer:
    """
    Trainer class for training and evaluating a PyTorch model.

    Attributes:
        model (nn.Module): The PyTorch model to be trained.
        criterion (nn.CrossEntropyLoss): Loss function.
        optimizer (optim.Adam): Optimizer.
        train_loader (DataLoader): DataLoader for training data.
        val_loader (DataLoader): DataLoader for validation data.
    """
    def __init__(self, model, train_loader, val_loader, learning_rate=0.001):
        """
        Initializes the trainer with model, DataLoaders, and learning rate.

        Args:
            model (nn.Module): The PyTorch model to be trained.
            train_loader (DataLoader): DataLoader for training data.
            val_loader (DataLoader): DataLoader for validation data.
            learning_rate (float, optional): Learning rate for the optimizer. Defaults to 0.001.
        """
        self.model = model
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.train_loader = train_loader
        self.val_loader = val_loader

    def train(self, num_epochs):
        """
        Trains the model for a specified number of epochs.

        Args:
            num_epochs (int): Number of epochs to train the model.
        """
        for epoch in range(num_epochs):
            self.model.train()
            running_loss = 0.0
            for inputs, labels in self.train_loader:
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {running_loss / len(self.train_loader)}")

    def evaluate(self):
        """
        Evaluates the model on the validation data.

        Returns:
            float: Accuracy of the model on the validation data.
        """
        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in self.val_loader:
                outputs = self.model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        accuracy = 100 * correct / total
        print(f'Accuracy: {accuracy}%')
        return accuracy