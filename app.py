import os
from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route("/<path:doc_link>",methods=["GET"])
def get_doc(doc_link):
    #the doc_link is the unique part of the pdf's url.
    #so for example, for the document at:
    #https://api.iga.in.gov/2015/bills/hb1001/versions
        #/hb1001.02.comh?format=pdf

    #the url here will be:
    # in.proxy.openstates.org/2015/bills/hb1001/versions/hb1001.02.comh

    #also note that as of right now, their site fails https verification

    headers = {}
    headers['Authorization'] = os.environ['INDIANA_API_KEY']
    headers['Content-Type'] = "application/pdf"
    full_link = "https://api.iga.in.gov/" + doc_link + "?format=pdf"
    page = requests.get(full_link,headers=headers,verify=False)
    
    if page.status_code == 429:
        resp = Response()
        resp.status_code = 429
        resp.headers = page.headers
        return resp

    if page.status_code != 200:
        resp = Response()
        resp.status_code = 500
        return resp

    resp = Response(page.content)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["X-Robots-Tag"] = "noindex"
    return resp

@app.route("/")
def index():
    description = """Accessing Indiana's legislative documents \
                    without an API key is hard to do in a consistent \
                    way. This service requests the desired document \
                    using Open States' API key and make them searchable \
                    in the Open States interface."""

    return(description)

@app.route("/robots.txt")
def robots.txt():
    return """User-agent: *
Disallow: /"""



if __name__ == "__main__":
    app.run(debug=False)
