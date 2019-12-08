from flask import Flask, render_template, flash, request,jsonify
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

import os
import xlrd 
from difflib import SequenceMatcher
from collections import Counter


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

    @app.route("/dashboard", methods=['GET', 'POST'])
    def dashboard():

        categoryFilter='Nuestra vida'

        loc = ("temasFinal.xlsx") 
        wb = xlrd.open_workbook(loc) 
        temas = wb.sheet_by_index(0)    
        nrows=temas.nrows
        
        dashboardData=[]
        categories=[]
        for row in range(1,nrows):
            if temas.cell_value(row,0) not in categories:
                categories.append(temas.cell_value(row,0))

            dashboardData.append({
                "categoria":temas.cell_value(row, 0),
                "subcategoria":temas.cell_value(row, 1),
                "tema":temas.cell_value(row, 2),
                "link":temas.cell_value(row, 3),
                "pagina":temas.cell_value(row, 4)})
        

        subByCategory=[]
        themesByCategory=[]        

        countedDashboard = Counter((elem["categoria"]) for elem in dashboardData)
        themesByCategory = [({'categoria' : categoria,'count': k}) \
            for (categoria), k in countedDashboard.items()]

        
        countedDashboard = Counter((elem["categoria"], elem["subcategoria"]) for elem in dashboardData)
        subByCategory = [({'categoria' : categoria, 'subcategoria' : subcategoria,'count': k}) \
            for (categoria, subcategoria), k in countedDashboard.items()]

        subByCategoryFiltered=[]

        if categoryFilter=='Todos':
            subByCategoryFiltered=subByCategory
        else:
            for elem in subByCategory:
                if elem['categoria']==categoryFilter:
                    subByCategoryFiltered.append(elem)           
        

        return render_template('dashboards.html',test=dashboardData[:5],categories=categories,pieData=subByCategoryFiltered,barData=themesByCategory)

    @app.route("/get-data", methods=['GET', 'POST'])
    def dataDashboard():
        loc = ("temasFinal.xlsx") 
        wb = xlrd.open_workbook(loc) 
        temas = wb.sheet_by_index(0)    
        nrows=temas.nrows
        
        dashboardData=[]
        for row in range(0,nrows):
            dashboardData.append({
                "categoria":temas.cell_value(row, 0),
                "subcategoria":temas.cell_value(row, 1),
                "tema":temas.cell_value(row, 2),
                "link":temas.cell_value(row, 3),
                "pagina":temas.cell_value(row, 4)})
        #flash(dashboardData)
        return jsonify(dashboardData)
    
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