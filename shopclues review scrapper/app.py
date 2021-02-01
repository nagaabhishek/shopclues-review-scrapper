from flask import Flask, render_template, request
from flask_cors import cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])
@cross_origin()

def homepage():
    return render_template('index.html')

@app.route('/scrap',methods=['POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            shopclues_url = "https://www.shopclues.com/search?q=" + searchString
            uClient = uReq(shopclues_url)
            shopcluesPage = uClient.read()
            uClient.close()
            shopclues_html = bs(shopcluesPage, "html.parser")
            bigboxes = shopclues_html.findAll("div", {'class': "column col3 search_blocks"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.shopclues.com" + box.a['href']
            prodRes = requests.get(productLink)
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find('div',{'class':"rnr_lists"})
            comments=commentboxes.findAll('li')
            reviews = []

            for commentbox in comments:
                try:
                    name = commentbox.div.find_all('div', {'class': 'r_by'})[0].text

                except:
                    name = 'No Name'

                try:
                    ratings = commentbox.div.find_all('div',{'class': "prd_ratings"})
                    rating=ratings[0].span.text

                except:
                    rating = 'No Rating'

                try:
                    comtag = commentbox.find_all('div', {'class': 'review_desc'})[0]
                    comtag1 = comtag.find_all('p')[0]
                    custComment = comtag1.text
                except:
                    custComment = 'No Customer Comment'

                mydict = {"Product": searchString, "Name": name, "Rating": rating,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews)
        except:
            return 'something is wrong'

if __name__ == "__main__":
    app.run(port=8000,debug=True)