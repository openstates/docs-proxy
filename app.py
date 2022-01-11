import os
from flask import Flask, Response, request
import lxml.html
import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"
)
app = Flask(__name__)


def _upstream_to_resp(upstream_resp):
    resp = Response(upstream_resp.content)
    resp.status_code = upstream_resp.status_code

    if upstream_resp.status_code != 200:
        pass
    else:
        resp.headers["Content-Type"] = "application/pdf"
        resp.headers["X-Robots-Tag"] = "noindex"
    return resp


@app.route("/ca", methods=["GET"])
def get_california_doc():
    BASE_URL = "https://leginfo.legislature.ca.gov/faces/billPdf.xhtml"
    bill_id = request.args.get("bill_id")
    version = request.args.get("version")

    # use one session to make the GET and then POST with view_state and cookie
    session = requests.Session()
    get_resp = session.get(BASE_URL + f"?bill_id={bill_id}&version={version}")
    doc = lxml.html.fromstring(get_resp.content)
    view_state = doc.xpath("//input[@name='javax.faces.ViewState']/@value")[0]

    form = {
        "downloadForm": "downloadForm",
        "javax.faces.ViewState": view_state,
        "pdf_link2": "pdf_link2",
        "bill_id": bill_id,
        "version": version,
    }
    resp = session.post(BASE_URL, data=form)
    return _upstream_to_resp(resp)


@app.route("/<path:doc_link>", methods=["GET"])
def get_indiana_doc(doc_link):
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
    return _upstream_to_resp(page)


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
