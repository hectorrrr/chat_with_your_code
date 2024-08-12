import tensorflow as tf
from transformers import TFAutoModelForSequenceClassification, AutoTokenizer
from datasets import load_metric, Dataset
from sklearn.model_selection import train_test_split

class TextClassificationModelTF:
    def __init__(self, model_name, num_labels):
        """
        Initializes the text classification model using TensorFlow.
        
        Args:
            model_name (str): The name of the pre-trained model from Hugging Face's model hub.
            num_labels (int): The number of labels for classification.
        """
        self.model_name = model_name
        self.num_labels = num_labels

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = TFAutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)

    def preprocess_data(self, texts, labels, test_size=0.2):
        """
        Preprocesses the text data by tokenizing and splitting into training and test sets.
        
        Args:
            texts (list): List of input texts.
            labels (list): List of labels corresponding to the texts.
            test_size (float): Proportion of the dataset to include in the test split.
        
        Returns:
            tf.data.Dataset: TensorFlow Dataset object with tokenized data for training and testing.
        """
        # Tokenization
        encodings = self.tokenizer(texts, truncation=True, padding=True, max_length=512)
        
        # Create TensorFlow datasets
        dataset = Dataset.from_dict({
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': labels
        })

        # Split into training and test datasets
        train_dataset, test_dataset = dataset.train_test_split(test_size=test_size).values()
        
        train_dataset = train_dataset.to_tf_dataset(
            columns=['input_ids', 'attention_mask'],
            label_cols='labels',
            shuffle=True,
            batch_size=16,
        )

        test_dataset = test_dataset.to_tf_dataset(
            columns=['input_ids', 'attention_mask'],
            label_cols='labels',
            shuffle=False,
            batch_size=16,
        )

        return train_dataset, test_dataset

    def compute_metrics(self, y_true, y_pred):
        """
        Computes accuracy metrics for the model evaluation.
        
        Args:
            y_true: Ground truth labels.
            y_pred: Model predictions.
        
        Returns:
            dict: Dictionary of accuracy and F1 metrics.
        """
        accuracy = tf.keras.metrics.Accuracy()
        accuracy.update_state(y_true, tf.argmax(y_pred, axis=1))
        acc = accuracy.result().numpy()
        
        return {'accuracy': acc}

    def train(self, train_dataset, test_dataset, epochs=3):
        """
        Trains the model using the provided dataset.
        
        Args:
            train_dataset (tf.data.Dataset): TensorFlow Dataset object for training.
            test_dataset (tf.data.Dataset): TensorFlow Dataset object for evaluation.
            epochs (int): Number of training epochs.
        """
        # Compile the model
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=2e-5),
            loss=self.model.compute_loss,
            metrics=['accuracy']
        )

        # Train the model
        self.model.fit(
            train_dataset,
            validation_data=test_dataset,
            epochs=epochs
        )

    def evaluate(self, test_dataset):
        """
        Evaluates the model on the test dataset.
        
        Args:
            test_dataset (tf.data.Dataset): TensorFlow Dataset object for evaluation.
        
        Returns:
            dict: Dictionary with evaluation results.
        """
        results = self.model.evaluate(test_dataset)
        return {'loss': results[0], 'accuracy': results[1]}

    def predict(self, texts):
        """
        Predicts labels for the given texts.
        
        Args:
            texts (list): List of texts to classify.
        
        Returns:
            list: List of predicted labels.
        """
        encodings = self.tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="tf")
        logits = self.model(encodings.data)['logits']
        predictions = tf.argmax(logits, axis=1)
        return predictions.numpy()

