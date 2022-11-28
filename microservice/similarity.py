from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


text_files = {'C:\\Users\\ssavkin\\Downloads\\news_aggregator\\microservice\\text_example.txt',
              'C:\\Users\\ssavkin\\Downloads\\news_aggregator\\microservice\\text_example2.txt',
              'C:\\Users\\ssavkin\\Downloads\\news_aggregator\\microservice\\text_example3.txt'}

documents = [open(f).read() for f in text_files]
tfidf = TfidfVectorizer().fit_transform(documents)
# no need to normalize, since Vectorizer will return normalized tf-idf
pairwise_similarity = tfidf * tfidf.T

print("pairwise_similarity", pairwise_similarity.toarray())

corpus = ["I'd like an apple",
          "An apple a day keeps the doctor away",
          "Never compare an apple to an orange",
          "I prefer scikit-learn to Orange",
          "The scikit-learn docs are Orange and Blue"]
vect = TfidfVectorizer(min_df=1, stop_words="english")
tfidf = vect.fit_transform(corpus)
pairwise_similarity = tfidf * tfidf.T

print(pairwise_similarity)

print(pairwise_similarity.toarray())


arr = pairwise_similarity.toarray()
np.fill_diagonal(arr, np.nan)
input_doc = "The scikit-learn docs are Orange and Blue"
input_idx = corpus.index(input_doc)
print(input_idx)
result_idx = np.nanargmax(arr[input_idx])
print(corpus[result_idx])
n, _ = pairwise_similarity.shape
pairwise_similarity[np.arange(n), np.arange(n)] = -1.0
print(pairwise_similarity[input_idx].argmax())
