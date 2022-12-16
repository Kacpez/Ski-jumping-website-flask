from flask import Flask,jsonify, render_template, request, flash, redirect, url_for
import os
from neo4j import GraphDatabase


uri = "neo4j+s://89d05a8e.databases.neo4j.io"
user = "neo4j"
password = "6x_sHNzaRO5iM-5fOjnqCcd0EUPV528bKyQxwmLCWxg"

driver=GraphDatabase.driver(uri=uri,auth=(user,password))
session=driver.session()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route("/skoczek", methods=['GET','POST'])
def skoczek():
	q1="""
    MATCH (p:Skoczek) RETURN p  
    """
	results=session.run(q1)
	print(results)
	data=results.data()
	wynik=[row["p"] for row in data]
	return render_template("skoczek.html",all_data=wynik)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
