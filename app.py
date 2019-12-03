from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

import pandas as pd
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
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
#model = Doc2Vec.load("./doc2vec_wikipedia_es_pvdbow")

class ReusableForm(Form):
    entrada = TextField('Ingresar la pregunta:', validators=[validators.required()])

    #@app.before_request
    #def loadModel():
        #print (entradaclean)

    @app.route("/", methods=['GET', 'POST'])
    def hello():
        form = ReusableForm(request.form)


        print (form.errors)
        if request.method == 'POST':
            entrada=request.form['entrada']
            print (entrada)
        
    
        if form.validate():
            df = pd.read_excel('temasDFv3.xlsx')

            model = gensim.models.Word2Vec.load('doc2vec_wikipedia_es_pvdbow')

                         
            #A minúsculas
            df["Minusculas"] = df["Tema"].str.lower()

            #Retirar puntuación
            cadpun = string.punctuation + '¿'
            df["Sin Puntuacion"] = df["Minusculas"].str.translate(str.maketrans('', '', cadpun))

            #Retirar stopwords
            stops = stopwords.words('spanish')
            df["Clean"] = df["Sin Puntuacion"].apply(lambda x: ' '.join([word for word in x.split() if word not in (stops)]))

            #Tokenization
            df["Tokenization"] = df["Clean"].str.split()

            vectores = []
            for tema in df["Tokenization"]:
                vector = model.infer_vector(tema)
                vectores.append(vector)

            df["Vector"]=vectores

            cadpun = string.punctuation + '¿'
            stops = stopwords.words('spanish')


            entrada = entrada.lower()
            entrada = entrada.translate(str.maketrans('', '', cadpun))
            palabras = entrada.split()
            resultwords = [palabra for palabra in palabras if palabra.lower() not in stops]
            entradaclean = (' '.join(resultwords)).split()
            
            vector = model.infer_vector(entradaclean).reshape(1,-1)

            #comparación la pregunta ingresada con la BD
            proximidades = []
            maxprox = 0
            cont = 0
            similares = {}
            similaresdict = {}

            for x in df["Vector"]:
                vectortema = np.asarray(x).reshape(1,-1)
                res = cosine_similarity(vectortema,vector) 
                #similares[float(res[0])] = preguntas[cont]
                similares = {}

                similares["Tema"] = df["Tema"][cont]
                similares["Categoría"] = df["Categoría"][cont]
                similares["Subcategoría"] = df["Subcategoría"][cont]
                similares["Valor"] = float(res[0]) 
                similaresdict[float(res[0])] = similares

                if (res> maxprox):
                    temaproxprox = df["Tema"][cont]
                    categoria = df["Categoría"][cont]
                    maxprox = res
                    contprox = cont
                proximidades.append(res)
                cont = cont + 1

            ordenados = sorted(similaresdict.items(), key=lambda kv: kv[0], reverse=True)

            print(ordenados[0][1])
            print(ordenados[1][1])
            print(ordenados[2][1])
            print(ordenados[3][1])
            print(ordenados[4][1])
            

            #flash(entradaclean)



        return render_template('hello.html', form=form)

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
    	port=int(os.getenv('PORT', 5000)))
