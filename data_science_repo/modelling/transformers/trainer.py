import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_metric, Dataset
from sklearn.model_selection import train_test_split

class TextClassificationModel:
    def __init__(self, model_name, num_labels, device=None):
        """
        Initializes the text classification model.
        
        Args:
            model_name (str): The name of the pre-trained model from Hugging Face's model hub.
            num_labels (int): The number of labels for classification.
            device (str, optional): Device to use ('cuda' or 'cpu'). If None, automatically detects.
        """
        self.model_name = model_name
        self.num_labels = num_labels
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels).to(self.device)

    def preprocess_data(self, texts, labels, test_size=0.2):
        """
        Preprocesses the text data by tokenizing and splitting into training and test sets.
        
        Args:
            texts (list): List of input texts.
            labels (list): List of labels corresponding to the texts.
            test_size (float): Proportion of the dataset to include in the test split.
        
        Returns:
            Dataset: Hugging Face Dataset object with tokenized data.
        """
        # Tokenization
        encodings = self.tokenizer(texts, truncation=True, padding=True, max_length=512)
        
        # Creating the dataset
        dataset = Dataset.from_dict({
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': labels
        })

        # Splitting into train and test sets
        train_dataset, test_dataset = dataset.train_test_split(test_size=test_size).values()
        return train_dataset, test_dataset

    def compute_metrics(self, p):
        """
        Computes accuracy metrics for the model evaluation.
        
        Args:
            p: Predictions from the model.
        
        Returns:
            dict: Dictionary of accuracy and F1 metrics.
        """
        metric = load_metric("accuracy")
        predictions, labels = p
        predictions = torch.argmax(predictions, dim=1)
        acc = metric.compute(predictions=predictions, references=labels)
        
        return acc

    def train(self, train_dataset, test_dataset, batch_size=16, epochs=3, logging_steps=10):
        """
        Trains the model using the provided dataset.
        
        Args:
            train_dataset (Dataset): Hugging Face Dataset object for training.
            test_dataset (Dataset): Hugging Face Dataset object for evaluation.
            batch_size (int): Batch size for training.
            epochs (int): Number of training epochs.
            logging_steps (int): Steps interval for logging during training.
        """
        training_args = TrainingArguments(
            output_dir='./results',          # output directory
            evaluation_strategy="epoch",     # evaluation strategy
            save_strategy="epoch",           # save strategy
            learning_rate=2e-5,              # learning rate
            per_device_train_batch_size=batch_size,  # batch size for training
            per_device_eval_batch_size=batch_size,   # batch size for evaluation
            num_train_epochs=epochs,         # number of training epochs
            weight_decay=0.01,               # strength of weight decay
            logging_dir='./logs',            # directory for storing logs
            logging_steps=logging_steps,     # log every `logging_steps` steps
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            compute_metrics=self.compute_metrics
        )

        trainer.train()

    def evaluate(self, test_dataset):
        """
        Evaluates the model on the test dataset.
        
        Args:
            test_dataset (Dataset): Hugging Face Dataset object for evaluation.
        
        Returns:
            dict: Dictionary with evaluation results.
        """
        trainer = Trainer(model=self.model)
        return trainer.evaluate(eval_dataset=test_dataset)

    def predict(self, texts):
        """
        Predicts labels for the given texts.
        
        Args:
            texts (list): List of texts to classify.
        
        Returns:
            list: List of predicted labels.
        """
        self.model.eval()
        inputs = self.tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)
        return predictions.cpu().numpy()

