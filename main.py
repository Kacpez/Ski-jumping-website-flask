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

@app.route("/skocznia/zwyciezcy", methods=['GET','POST'])
def zwyciezcy():
	q1="""
    MATCH  (a:Skoczek)-[:WYGRAŁ_NA]->(b:Skocznia)  RETURN a.nazwa AS p,collect(b.nazwa) AS tab  
    """
	results=session.run(q1)
	print(results)
	data=results.data()
	wynik=[(row["p"],row["tab"]) for row in data]
	return render_template("zwyciezcy.html",all_data=wynik)

@app.route("/kraj/skoczkowie", methods=['GET','POST'])
def skoczkowieKraj():
	q1="""
    MATCH  (a:Skoczek)-[:POCHODZI_Z]->(b:Kraj)  RETURN b.nazwa AS p,collect(a.nazwa) AS tab ORDER BY b.nazwa  
    """
	results=session.run(q1)
	print(results)
	data=results.data()
	wynik=[(row["p"],row["tab"]) for row in data]
	return render_template("skoczkowieKraj.html",all_data=wynik)

@app.route("/kraj/skocznie", methods=['GET','POST'])
def skocznieKraj():
	q1="""
    MATCH  (a:Skocznia)-[:ZNAJDUJE_SIĘ_W]->(b:Kraj)  RETURN b.nazwa AS p,collect(a.nazwa) AS tab  ORDER BY b.nazwa  
    """
	results=session.run(q1)
	print(results)
	data=results.data()
	wynik=[(row["p"],row["tab"]) for row in data]
	return render_template("skocznieKraj.html",all_data=wynik)

@app.route("/skocznia", methods=['GET','POST'])
def skocznia():
	q1="""
    MATCH (sk:Skocznia) RETURN sk  
    """
	results=session.run(q1)
	print(results)
	data=results.data()
	wynik=[row["sk"] for row in data]
	return render_template("skocznia.html",all_data=wynik)

@app.route("/skoczek/podziwianie", methods=['GET','POST'])
def podziwianie():
	q1="""
    MATCH (a:Skoczek)-[:PODZIWIA]->(b:Skoczek) RETURN DISTINCT a.nazwa AS p, b.nazwa  AS tab
    """
	results=session.run(q1)
	print(results)
	data=results.data()
	wynik=[(row["p"],row["tab"]) for row in data]
	return render_template("podziwianie.html",all_data=wynik)

@app.route("/skocznia/skoki", methods=['GET','POST'])
def skoki():
    q1="""
    MATCH (p:Skocznia) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    if request.method == "POST":
        skocznia_nazwa = request.form["nazwa"]

        query = ("""
            MATCH (p:Skocznia) RETURN p  
		"""
        )
        session.run(query)

        return redirect(url_for("skocznia_narciarska",usr=skocznia_nazwa))
    else:
        return render_template("skoki.html",all_data=wynik)

@app.route("/kraj", methods=['GET','POST'])
def kraj():
	q1="""
    MATCH (panstwo:Kraj) RETURN panstwo  ORDER BY panstwo.nazwa  
    """
	results=session.run(q1)
	print(results)
	data=results.data()
	wynik=[row["panstwo"] for row in data]
	return render_template("kraj.html",all_data=wynik)

@app.route("/skocznia/statystyki", methods=['GET','POST'])
def statystyki():
	q1="""
    MATCH (sk:Skoczek)-[skok:SKAKAŁ_NA]->(sko:Skocznia) RETURN sko.nazwa AS a, sko.miejscowosc AS i ,sko.punktK AS g,sko.punktHS AS h,collect(skok.odleglosc) AS b ,avg(skok.odleglosc) AS c,max(skok.odleglosc) AS d ,min(skok.odleglosc) AS e,count(*) AS f
    """
	results=session.run(q1)
	print(results)
	data=results.data()
	wynik=[row for row in data]
	return render_template("statystyki.html",all_data=wynik)

@app.route("/skoczek/dodaj_skoczka", methods=["POST", "GET"])
def dodaj_skoczka():
    q1="""
    MATCH (p:Kraj) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    if request.method == "POST":
        skoczek_nazwa = request.form["nazwa"]
        skoczek_rok = request.form["rok"]
        skoczek_forma = request.form["forma"]
        skoczek_kraj = request.form["panstwo"]
        query = ("""
            MATCH (panstwo:Kraj) WHERE panstwo.nazwa= $skoczek_kraj
            CREATE (p1:Skoczek { nazwa: $skoczek_nazwa , rok_urodzenia: $skoczek_rok , aktualna_forma: $skoczek_forma })
            CREATE (p1)-[:POCHODZI_Z]->(panstwo)
		"""
        )
        session.run(query,skoczek_nazwa=skoczek_nazwa,skoczek_rok=skoczek_rok,skoczek_forma=skoczek_forma,skoczek_kraj=skoczek_kraj)

        return redirect(url_for("skoczek"))
    else:
        return render_template("dodaj_skoczka.html",all_data=wynik)

@app.route("/skoczek/edytuj_skoczka", methods=["POST", "GET"])
def edytuj_skoczka():
    q1="""
    MATCH (p:Skoczek) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    if request.method == "POST":
        skoczek_nazwa = request.form["nazwa"]
        skoczek_forma = request.form["forma"]
        query = ("""
            MATCH (p1:Skoczek) WHERE p1.nazwa= $skoczek_nazwa
            SET p1.aktualna_forma = $skoczek_forma
		"""
        )
        session.run(query,skoczek_nazwa=skoczek_nazwa,skoczek_forma=skoczek_forma)

        return redirect(url_for("skoczek"))
    else:
        return render_template("edytuj_skoczka.html",all_data=wynik)


@app.route("/skoczek/usun_skoczka", methods=["POST", "GET"])
def usun_skoczka():
    q1="""
    MATCH (p:Skoczek) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    if request.method == "POST":
        skoczek_nazwa = request.form["nazwa"]
        query = ("""
            MATCH (p1:Skoczek) WHERE p1.nazwa= $skoczek_nazwa
            DETACH DELETE p1
		"""
        )
        session.run(query,skoczek_nazwa=skoczek_nazwa)

        return redirect(url_for("skoczek"))
    else:
        return render_template("usun_skoczka.html",all_data=wynik)

@app.route("/skoczek/dodaj_podziwianie", methods=["POST", "GET"])
def dodaj_podziwianie():
    q1="""
    MATCH (p:Skoczek) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    if request.method == "POST":
        skoczek_nazwa1 = request.form["nazwa1"]
        skoczek_nazwa2 = request.form["nazwa2"]
        query = ("""
            MATCH (a:Skoczek), (b:Skoczek)
            WHERE a.nazwa = $skoczek_nazwa1 AND b.nazwa=$skoczek_nazwa2
            CREATE (a)-[:PODZIWIA]->(b)
		"""
        )
        session.run(query,skoczek_nazwa1=skoczek_nazwa1,skoczek_nazwa2=skoczek_nazwa2)

        return redirect(url_for("skoczek"))
    else:
        return render_template("dodaj_podziwianie.html",all_data=wynik)

@app.route("/skoczek/dodaj_skok", methods=["POST", "GET"])
def dodaj_skok():
    q1="""
    MATCH (p:Skoczek) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    q2="""
    MATCH (p:Skocznia) RETURN p  
    """
    results2=session.run(q2)
    print(results2)
    data2=results2.data()
    wynik2=[row["p"] for row in data2]
    if request.method == "POST":
        skoczek_nazwa = request.form["nazwa1"]
        skocznia_nazwa = request.form["nazwa2"]
        sodleglosc=float(request.form["skok"])
        query = ("""
            MATCH (a:Skoczek), (m:Skocznia)
            WHERE a.nazwa = $skoczek_nazwa AND m.nazwa=$skocznia_nazwa
            CREATE (a)-[skok:SKAKAŁ_NA]->(m)
            SET skok.odleglosc=$sodleglosc
		"""
        )
        session.run(query,skoczek_nazwa=skoczek_nazwa,skocznia_nazwa=skocznia_nazwa,sodleglosc=sodleglosc)

        return redirect(url_for("skoczek"))
    else:
        return render_template("dodaj_skok.html",all_data=wynik,all_data2=wynik2)

@app.route("/skoczek/dodaj_zwyciezce", methods=["POST", "GET"])
def dodaj_zwyciezce():
    q1="""
    MATCH (p:Skoczek) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    q2="""
    MATCH (p:Skocznia) RETURN p  
    """
    results2=session.run(q2)
    print(results2)
    data2=results2.data()
    wynik2=[row["p"] for row in data2]
    if request.method == "POST":
        skoczek_nazwa = request.form["nazwa1"]
        skocznia_nazwa = request.form["nazwa2"]
        query = ("""
            MATCH (a:Skoczek), (m:Skocznia)
            WHERE a.nazwa = $skoczek_nazwa AND m.nazwa=$skocznia_nazwa
            CREATE (a)-[:WYGRAŁ_NA]->(m)
		"""
        )
        session.run(query,skoczek_nazwa=skoczek_nazwa,skocznia_nazwa=skocznia_nazwa)

        return redirect(url_for("skoczek"))
    else:
        return render_template("dodaj_zwycezce.html",all_data=wynik,all_data2=wynik2)

@app.route("/skocznia/dodaj_skocznie", methods=["POST", "GET"])
def dodaj_skocznie():
    q1="""
    MATCH (p:Kraj) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    if request.method == "POST":
        skocznia_nazwa = request.form["nazwa"]
        skocznia_miejsce = request.form["miejsce"]
        skocznia_K = float(request.form["punktK"])
        skocznia_HS = float(request.form["punktHS"])
        skocznia_rekord = float(request.form["rekord"])
        kraj = request.form["panstwo"]
        query = ("""
        MATCH (panstwo:Kraj) WHERE panstwo.nazwa= $kraj
        CREATE (p1:Skocznia { nazwa: $skocznia_nazwa , miejscowosc: $skocznia_miejsce , punktK: $skocznia_K , punktHS: $skocznia_HS , rekord: $skocznia_rekord})
        CREATE (p1)-[:ZNAJDUJE_SIĘ_W]->(panstwo)
		"""
        )
        session.run(query,skocznia_nazwa=skocznia_nazwa,skocznia_miejsce=skocznia_miejsce,skocznia_K=skocznia_K,skocznia_HS=skocznia_HS, skocznia_rekord= skocznia_rekord,kraj=kraj)

        return redirect(url_for("skocznia"))
    else:
        return render_template("dodaj_skocznie.html",all_data=wynik)


@app.route("/skocznia/usun_skocznie", methods=["POST", "GET"])
def usun_skocznie():
    q1="""
    MATCH (p:Skocznia) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    if request.method == "POST":
        skocznia_nazwa = request.form["nazwa"]
        query = ("""
            MATCH (p1:Skocznia) WHERE p1.nazwa= $skocznia_nazwa
            DETACH DELETE p1
		"""
        )
        session.run(query,skocznia_nazwa=skocznia_nazwa)

        return redirect(url_for("skocznia"))
    else:
        return render_template("usun_skocznie.html",all_data=wynik)

@app.route("/kraj/dodaj_kraj", methods=["POST", "GET"])
def dodaj_kraj():
    if request.method == "POST":
        kraj_nazwa = request.form["nazwa"]
        kraj_stolica = request.form["stolica"]
        query = ("""
            CREATE (p1:Kraj { nazwa: $kraj_nazwa , stolica: $kraj_stolica })
		"""
        )
        session.run(query,kraj_nazwa=kraj_nazwa,kraj_stolica=kraj_stolica)

        return redirect(url_for("kraj"))
    else:
        return render_template("dodaj_kraj.html")

@app.route("/kraj/usun_kraj", methods=["POST", "GET"])
def usun_kraj():
    q1="""
    MATCH (p:Kraj) RETURN p  
    """
    results=session.run(q1)
    print(results)
    data=results.data()
    wynik=[row["p"] for row in data]
    if request.method == "POST":
        kraj_nazwa = request.form["nazwa"]
        query = ("""
            MATCH (p1:Kraj) WHERE p1.nazwa= $kraj_nazwa
            DETACH DELETE p1
		"""
        )
        session.run(query,kraj_nazwa=kraj_nazwa)

        return redirect(url_for("kraj"))
    else:
        return render_template("usun_kraj.html",all_data=wynik)


@app.route("/skocznia/<usr>", methods=["POST", "GET"])
def skocznia_narciarska(usr):
    q1="""
    MATCH (a:Skoczek)-[skok:SKAKAŁ_NA]->(b:Skocznia) WHERE b.nazwa=$usr
    RETURN a.nazwa,skok.odleglosc
    """
    results=session.run(q1,usr=usr)
    print(results)
    data=results.data()
    wynik=[row for row in data]
    return render_template("skoki2.html",all_data=wynik, usr=usr)
    

driver.close()

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
