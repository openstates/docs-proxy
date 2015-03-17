from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route('/todo/api/v1/doc/<path:doc_link>',methods=['GET'])
def get_doc(doc_link):
    #the doc_link is the unique part of the pdf's url.
    #so for example, for the document at:
    #https://api.iga.in.gov/2015/bills/hb1001/versions
        #/hb1001.02.comh?format=pdf

    #the url here will be:
    #http://localhost:5000/todo/api/v1/doc/2015/bills
        #/hb1001/versions/hb1001.02.comh

    #also note that as of right now, their site fails http

    headers = {}
    headers['Authorization'] = in_api_key
    headers['Content-Type'] = "application/pdf"
    full_link = "https://api.iga.in.gov/" + doc_link + "?format=pdf"
    page = requests.get(full_link,headers=headers,verify=False)
    resp = Response(page.content)
    resp.headers["Content-Type"] = "application/pdf"

    return resp

if __name__ == "__main__":
    app.run(debug=True)