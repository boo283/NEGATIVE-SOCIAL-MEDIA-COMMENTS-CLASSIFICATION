
import joblib
from preprocess import preprocess

loaded_vectorizer = joblib.load('bow_vectorizer.pkl')
loaded_model = joblib.load('bow_lr.pkl')
topic = 'StreamingComments'
#bow_vectorizer = CountVectorizer()


def return_idf_vector(text, vectorizer):
    text = preprocess(text)
    return vectorizer.transform([text]).toarray() 

def predict(data):
    loaded_vectorizer = joblib.load('bow_vectorizer.pkl')
    loaded_model = joblib.load('bow_lr.pkl')
    prediction = loaded_model.predict(return_idf_vector(data, loaded_vectorizer))

    return prediction[0]


    