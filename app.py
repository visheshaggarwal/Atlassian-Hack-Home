from flask import Flask
from flask import render_template, redirect, url_for, request,jsonify
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import pandas as pd
app = Flask(__name__, template_folder='template')



@app.route("/",methods=["GET","POST"])
def home():
    return "Success"

@app.route("/state",methods=["GET","POST"])
def state():
    data_url = "https://www.mygov.in/corona-data/covid19-statewise-status"
    data = urlopen(data_url)
    print(type(data))
    data_html = data.read()
    print(len(data_html))
    data.close()
    data_soup = soup(data_html,'html.parser')
    tables = data_soup.findAll('div',{'class':'entity entity-field-collection-item field-collection-item-field-covid-statewise-data clearfix'})
    print(len(tables))
    table_list = []
    for t in tables:
        row = t.findAll('div',{'class':'field-item even'})
        row_list = []
        for r in row:
            row_list.append(r.text)
        table_list.append(row_list)

    if request.method == "POST":
        state = request.form["City"]
        print(state)
        for t in table_list:
            if state in t:
                return render_template('individual.html',state_data = t)
    return render_template("state.html",table_list=table_list)

@app.route("/info",methods=["GET","POST"])
def info():
    data_url = "https://www.mygov.in/covid-19#updates"
    data = urlopen(data_url)
    data_html = data.read()
    data.close()
    data_soup = soup(data_html,'html.parser')
    infos = data_soup.findAll('div',{'class' : 'lnr'})
    date = []
    title = []
    links = []
    for x in infos:
        link = x.find('a')
        title.append(link.text)
        dates = x.find('span')
        date.append(dates.text)
        link = str(link).split(".pdf")[0][8:] + ".pdf\""
        links.append(link)

    return render_template("info.html",date = date,links = links,title = title,num = len(date))

@app.route("/district",methods=["GET","POST"])
def district():
    data_url = "https://www.indiatvnews.com/coronavirus/cases-in-india-district-wise-details"
    data = urlopen(data_url)
    print(type(data))
    data_html = data.read()
    print(len(data_html))
    data.close()
    data_soup = soup(data_html,'html.parser')
    tables = data_soup.findAll('table',{})
    tables = tables[0]
    print(len(tables))
    headers = tables.findAll('th')
    col_head = []
    for i in headers:
        col_head.append(i.text)
    # print(col_head)
    rows_data = tables.findAll('tr')[3:-1]
    # print(len(rows_data))
    table_list = []
    num = []
    i=0
    while i < len(rows_data):
        row = rows_data[i].findAll('td')
        row = row[:2]
        row_list = []
        for r in row:
            row_list.append(r.text)
        if len(rows_data[i].findAll('table')) > 0:
            district_data = rows_data[i].findAll('table')
            dist = []
            # print(district_data)
            for d in district_data[0].findAll('td'):
                dist.append(d.text)
            val = []
            for d in district_data[1].findAll('td'):
                val.append(d.text)
            i += 2 + len(val) + len(dist)
            table_list.append((row_list,dist,val,len(dist)))
        else:
            i += 1

        if request.method == "POST":
            state = request.form["District"]
            for t in table_list:
                for i in range(len(t[1])):
                    if state in t[1][i]:
                        return render_template('individual_d.html',state_data = t[1][i],value = t[2][i])
        
    return render_template("districts.html",table_list=table_list)

@app.route("/FAQs",methods=["GET","POST"])
def FAQs():
    data_url = "https://www.pennmedicine.org/coronavirus/frequently-asked-questions-about-covid-19#"
    data = urlopen(data_url)
    data_html = data.read()
    data.close()
    data_soup = soup(data_html,'html.parser')
    infos = data_soup.findAll('section',{'class' : 'accordion__item js-tabs__content'})
    print(len(infos))
    ques = {}

    for info in infos:
        print(info)
        q = info.find('a')
        ans = info.find('p')
        ques[q.text.lower()] = ans.text
        print(q.text)

    if request.method == "POST":
        state = request.form["Q"]
        if state.lower() in ques.keys():
            return render_template("FAQanswer.html", Q = state,ans = ques[state.lower()])
        else:
            return render_template("ALL.html",ques = ques)
    
    return render_template("FAQ.html",ques = ques)


if __name__ == "__main__":
    app.debug = True
    app.run()