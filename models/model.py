# -*- coding: utf-8 -*-
"""Model.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1j3iYzyNLM0_mFFsbqJwZ3T6NTb2qdcdY
"""

import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    LSTM, Embedding, Dense, Input, Attention,
    Concatenate, Bidirectional
)
from tensorflow.keras.callbacks import EarlyStopping

# Load the dataset
file_path = '/content/sample_data/en_ar_final.tsv'  # Path to your dataset
data = pd.read_csv(file_path, sep='\t')

# Data Cleaning
def clean_text(text):
    if isinstance(text, str):  # Check if text is a string
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
        text = text.lower()  # Convert to lowercase
        return text.strip()
    return ''  # Return empty string if not a valid string

data['en'] = data['en'].apply(clean_text)
data['ar'] = data['ar'].apply(clean_text)

import pandas as pd

# Load the dataset
file_path = '/content/en_ar_final.tsv'
data = pd.read_csv(file_path, sep='\t')

# Display the first few rows of the dataset
print("Dataset Preview:")
print(data.head())

# Display the dataset info to understand its structure
print("\nDataset Info:")
print(data.info())

# Drop rows with missing English sentences
data_cleaned = data.dropna(subset=['en'])

# Display the cleaned dataset info
print("Cleaned Dataset Info:")
print(data_cleaned.info())

#Proceed with tokenization
tokenizer_en = Tokenizer()
tokenizer_ar = Tokenizer()

tokenizer_en.fit_on_texts(data_cleaned['en'])
tokenizer_ar.fit_on_texts(data_cleaned['ar'])

# Convert text sequences to integers
sequences_en = tokenizer_en.texts_to_sequences(data_cleaned['en'])
sequences_ar = tokenizer_ar.texts_to_sequences(data_cleaned['ar'])

# Padding sequences
max_len_en = max(len(seq) for seq in sequences_en)
max_len_ar = max(len(seq) for seq in sequences_ar)

padded_en = pad_sequences(sequences_en, maxlen=max_len_en, padding='post')
padded_ar = pad_sequences(sequences_ar, maxlen=max_len_ar, padding='post')

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(padded_en, padded_ar, test_size=0.2, random_state=42)

from tensorflow.keras.layers import Dropout
# Model Creation
embedding_dim = 128
vocab_size_en = len(tokenizer_en.word_index) + 1
vocab_size_ar = len(tokenizer_ar.word_index) + 1



# Encoder
encoder_inputs = Input(shape=(max_len_en,))
encoder_embedding = Embedding(input_dim=vocab_size_en, output_dim=embedding_dim)(encoder_inputs)
encoder_lstm = LSTM(128, return_sequences=True)(encoder_embedding)  # LSTM without dropout for simplicity
encoder_dropout = Dropout(0.5)(encoder_lstm)  # Add dropout after encoder LSTM

# Decoder
decoder_inputs = Input(shape=(max_len_ar,))
decoder_embedding = Embedding(input_dim=vocab_size_ar, output_dim=embedding_dim)(decoder_inputs)
decoder_lstm = LSTM(128, return_sequences=True)(decoder_embedding)  # Keep return_sequences=True for attention
decoder_dropout = Dropout(0.5)(decoder_lstm)  # Add dropout after decoder LSTM


# Attention Layer
attention_layer = Attention()  # Instantiate the Attention layer
attention = attention_layer([decoder_dropout, encoder_dropout])

# Concatenate attention output and the decoder LSTM output
decoder_combined_context = Concatenate(axis=-1)([attention, decoder_dropout])

# Output Layer
decoder_dense = Dense(vocab_size_ar, activation='softmax')(decoder_combined_context)


# Final Model
model = Model([encoder_inputs, decoder_inputs], decoder_dense)

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Prepare decoder output (y_train and y_test) for the training
# Use only the portion that corresponds to the training data
y_train_shifted = np.zeros_like(padded_ar[:len(X_train)])  # Match the shape with X_train
y_train_shifted[:, :-1] = padded_ar[:len(X_train), 1:]

y_test_shifted = np.zeros_like(padded_ar[len(X_train):])  # Match the shape with X_test
y_test_shifted[:, :-1] = padded_ar[len(X_train):, 1:]

# Model Training
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
history = model.fit([X_train, padded_ar[:len(X_train)]],  # Encoder input
    y_train_shifted,  # Decoder output (shifted)
    epochs=100,
    batch_size=32,
    validation_data=([X_test, padded_ar[len(X_train):]], y_test_shifted),
    callbacks=[early_stopping]
)

# Save the model in the native Keras format
model.save('/home/nesrien/Downloads/language_translation_model.keras')

# Test with known input sentences
# Not tested yet
test_sentences = [
    "as in mother id like to fuck",  # Adjust based on your training set
    "i must go"
]

for sentence in test_sentences:
    input_data = preprocess_input(sentence)
    predicted_sequence = model.predict([input_data, np.zeros((1, max_len_ar))])  # Dummy decoder input

    # Get predicted indices
    predicted_word_index = np.argmax(predicted_sequence, axis=-1)

    # Print predicted word indices for debugging
    print("Predicted Word Indices:", predicted_word_index)

    # Decode the predicted output
    translated_sentence = decode_sequence(predicted_word_index)

    # Print the translated sentence
    print(f"Input: {sentence} -> Translated: {translated_sentence}")

# Check the vocabulary used in the tokenizer
print("Vocabulary Size:", len(tokenizer_en.word_index))
print("Vocabulary Example:", dict(list(tokenizer_en.word_index.items())[:10]))  # Print first 10 entries

def preprocess_input(sentence):
    # Clean the input
    sentence = clean_text(sentence)
    # Convert to sequence
    sequence = tokenizer_en.texts_to_sequences([sentence])
    # Pad the sequence
    padded_sequence = pad_sequences(sequence, maxlen=max_len_en, padding='post')
    return padded_sequence

# Reducing complexity by using a single LSTM layer for both encoder and decoder
encoder_lstm = LSTM(128, return_sequences=True)(encoder_embedding)
decoder_lstm = LSTM(128, return_sequences=True)(decoder_embedding)

# Recompile the model to set metrics
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Sample input for testing
input_sentence = "what are you doing"  # Replace with your input

# Preprocess the input sentence
def preprocess_input(sentence):
    # Clean the input
    sentence = clean_text(sentence)
    # Convert to sequence
    sequence = tokenizer_en.texts_to_sequences([sentence])
    # Pad the sequence
    padded_sequence = pad_sequences(sequence, maxlen=max_len_en, padding='post')
    return padded_sequence

# Prepare the input data
input_data = preprocess_input(input_sentence)



# Generate predictions
predicted_sequence = model.predict([input_data, np.zeros((1, max_len_ar))])  # Provide dummy decoder input

# Print the shape and content of predicted_sequence
print("Predicted Sequence Shape:", predicted_sequence.shape)
print("Predicted Sequence Raw Output:", predicted_sequence)

# Get the predicted word indices
predicted_word_index = np.argmax(predicted_sequence, axis=-1)

# Print predicted indices for inspection
print("Predicted Word Indices:", predicted_word_index)

# Convert predictions back to words
def decode_sequence(sequence):
    # Convert back to words
    return ' '.join(tokenizer_ar.index_word[i] for i in sequence[0] if i > 0)

# Decode the predicted output
translated_sentence = decode_sequence(predicted_word_index)

# Print the translated sentence
print("Translated Sentence:", translated_sentence)

# Convert predictions back to words
def decode_sequence(sequence):
    # Convert back to words
    return ' '.join(tokenizer_ar.index_word[i] for i in sequence[0] if i > 0)

# Decode the predicted output
translated_sentence = decode_sequence(predicted_word_index)
print("Translated Sentence:", translated_sentence)

