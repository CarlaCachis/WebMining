from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

import os
import xlrd 
from difflib import SequenceMatcher


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

    @app.route("/", methods=['GET', 'POST'])
    def hello():
        form = ReusableForm(request.form)

        if request.method == 'POST':
            entrada=request.form['entrada']
    
        if form.validate():

            with open("set_preguntas.txt", "a") as myfile:
                myfile.write(entrada+'\n')


            loc = ("preguntas.xlsx") 
            wb = xlrd.open_workbook(loc) 
            preguntas = wb.sheet_by_index(0)    
            nrows=preguntas.nrows
            
            lista=[]
            for row in range(0,nrows):
                preguntaExcel=preguntas.cell_value(row, 0) 
                ratio=SequenceMatcher(None,entrada,preguntaExcel).ratio()
                lista.append({"indice":row,"ratio":ratio,"pregunta":preguntaExcel})

            lista=sorted(lista, key = lambda i: i['ratio'],reverse=True) 

            #Buscaremos las respuestas a esta pregunta

            loc2=("respuestas.xls")
            wb=xlrd.open_workbook(loc2)
            respuestas=wb.sheet_by_index(0)
            nrows=respuestas.nrows

            jsonList=[]
            for row in range(0,nrows):

                filaExcel=respuestas.cell_value(row,0)
                if(respuestas.cell_value(row,0)==lista[0]['indice']):
                    jsonList.append({"tema":respuestas.cell_value(row,1),"categoria":respuestas.cell_value(row,2),"link":respuestas.cell_value(row,4)})

            flash(jsonList)



        return render_template('hello.html', form=form)

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), 
    	port=int(os.getenv('PORT', 80)))
