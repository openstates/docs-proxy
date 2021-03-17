import os
from flask import Flask, Response
import urllib3
import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"
)
app = Flask(__name__)


@app.route("/iga/<path:iga_path>", methods=["GET"])
def get_iga_page(iga_path):
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    pm = urllib3.PoolManager(maxsize=10)
    full_link = "http://iga.in.gov/" + iga_path
    raw = pm.urlopen("GET", full_link, headers=headers)

    resp = Response(raw.data)
    resp.status_code = raw.status
    return resp


@app.route("/<path:doc_link>", methods=["GET"])
def get_doc(doc_link):
    # the doc_link is the unique part of the pdf's url.
    # so for example, for the document at:
    # https://api.iga.in.gov/2015/bills/hb1001/versions/hb1001.02.comh?format=pdf

    # the url here will be:
    # in.proxy.openstates.org/2015/bills/hb1001/versions/hb1001.02.comh

    # also note that as of right now, their site fails https verification

    headers = {}
    headers["Authorization"] = os.environ["INDIANA_API_KEY"]
    headers["Content-Type"] = "application/pdf"
    headers["User-Agent"] = USER_AGENT
    full_link = "https://api.iga.in.gov/" + doc_link + "?format=pdf"
    page = requests.get(full_link, headers=headers, verify=True)

    resp = Response(page.content)
    resp.status_code = page.status_code

    if page.status_code != 200:
        pass
    else:
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

    return description


@app.route("/robots.txt")
def robots_txt():
    return """User-agent: *
Disallow: /"""


if __name__ == "__main__":
    app.run(debug=False)
