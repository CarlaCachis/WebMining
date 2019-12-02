from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
nltk.download('stopwords')
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import multiprocessing 
import gensim
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import os
from sklearn.metrics.pairwise import cosine_similarity


# App config.
# https://medium.com/@onejohi/building-a-simple-rest-api-with-python-and-flask-b404371dc699
# set FLASK_ENV=development
# set FLASK_APP=app.py
#DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
#model = Doc2Vec.load("./doc2vec_wikipedia_es_pvdbow")

class ReusableForm(Form):
    pregunta = TextField('Ingresar la pregunta:', validators=[validators.required()])

    #@app.before_request
    #def loadModel():
        #print (model.docvecs.vectors_docs.shape)

    @app.route("/", methods=['GET', 'POST'])
    def hello():
        form = ReusableForm(request.form)
    
        print (form.errors)
        if request.method == 'POST':
            pregunta=request.form['pregunta']
            print (pregunta)
    
        if form.validate():
            # Save the comment here.
            cadpun = string.punctuation + '¿'
            stops = stopwords.words('spanish')


            pregunta = pregunta.lower()
            pregunta = pregunta.translate(str.maketrans('', '', cadpun))
            palabras = pregunta.split()
            resultwords = [palabra for palabra in palabras if palabra.lower() not in stops]
            preguntaclean = (' '.join(resultwords)).split()

            #Carga de BD



            flash(preguntaclean)



        return render_template('hello.html', form=form)

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
    	port=int(os.getenv('PORT', 5000)))
