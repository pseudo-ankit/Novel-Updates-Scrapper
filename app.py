from crypt import methods
from distutils.log import debug
from urllib import request
from scraper import ScraperNovelUpdates
from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method=="GET":
        return render_template("index.html")
    elif request.method=="POST":
        novel_name = request.form['novelName']
        novel_details = scrape(novel_name=novel_name)
        if novel_details['status']==200:
            return render_template('details.html', novel_details=novel_details)
        return render_template('404.html')


def scrape(novel_name):
    if request.method=='GET':
        return redirect(url_for("main"))
    elif request.method == 'POST':
        novel_name = request.form["novelName"]
        scraperObj = ScraperNovelUpdates(novel_name)
        scraperObj.scrape()

        novel_details = {
            "title" : scraperObj.title,
            "cover_url" : scraperObj.cover_url,
            "genre" : scraperObj.genre,
            "associated_names" : scraperObj.associated_names,
            "discription" : scraperObj.discription,
            "comments" : scraperObj.comments,
            "status" : scraperObj.status
        }

        print(scraperObj.status)
        return novel_details
    

if __name__=="__main__":
    
    app.run(debug=True)