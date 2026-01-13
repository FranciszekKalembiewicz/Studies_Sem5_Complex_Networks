import nltk
import random
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string


try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('movie_reviews')
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')

documents = []
for category in movie_reviews.categories():
    for fileid in movie_reviews.fileids(category):
        documents.append((list(movie_reviews.words(fileid)), category))

random.shuffle(documents)

stop_words = set(stopwords.words('english'))
punctuations = set(string.punctuation)

all_words = []
for w in movie_reviews.words():
    w_lower = w.lower()
    if w_lower not in stop_words and w_lower not in punctuations:
        all_words.append(w_lower)

all_words_dist = nltk.FreqDist(all_words)
word_features = list(all_words_dist.keys())[:2000]

def find_features(document):
    words = set(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features

featuresets = [(find_features(rev), category) for (rev, category) in documents]

training_set = featuresets[:1900]
testing_set = featuresets[1900:]

print("--- Trenowanie klasyfikatora Naive Bayes... ---")
classifier = nltk.NaiveBayesClassifier.train(training_set)

accuracy = nltk.classify.accuracy(classifier, testing_set)
print(f"\nDokładność modelu (Accuracy): {accuracy * 100:.2f}%")

print("\n--- Najbardziej informatywne słowa (Wnioski) ---")
classifier.show_most_informative_features(10)

print("\n--- Test na nowym zdaniu ---")
custom_review = "This movie was absolutely terrible and boring. The plot was weak."
custom_tokens = word_tokenize(custom_review.lower())
custom_feats = find_features(custom_tokens)
result = classifier.classify(custom_feats)
print(f"Recenzja: '{custom_review}'")
print(f"Werdykt modelu: {result} (neg = negatywna, pos = pozytywna)")