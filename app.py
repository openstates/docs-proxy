import os
from flask import Flask, Response, request
from flask_compress import Compress
import logging
import lxml.html
import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"
)
app = Flask(__name__)
gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
# compress responses to save some outgoing bandwidth
Compress(app)


@app.route("/healthz", methods=["GET"])
def health():
    return "OK"


@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest()


def _upstream_to_resp(upstream_resp):
    """
    Add missing headers to the response so the actual
    consuming application can handle things properly
    """
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
    get_resp = session.get(f"{BASE_URL}?bill_id={bill_id}&version={version}")
    doc = lxml.html.fromstring(get_resp.content)
    view_state = doc.xpath("//input[@name='javax.faces.ViewState']/@value")[0]

    form = {
        "downloadForm": "downloadForm",
        "javax.faces.ViewState": view_state,
        "pdf_link2": "pdf_link2",
        "bill_id": bill_id,
        "version": version,
    }
    resp = session.post(BASE_URL, data=form, verify=False)
    return _upstream_to_resp(resp)


@app.route("/in/<path:doc_link>", methods=["GET"])
@app.route("/<path:doc_link>", methods=["GET"])
def get_indiana_doc(doc_link):
    """
    two routes here (For now), both /in/<path> and /<path>. This should let us
    migrate to /in/ in the future, making this package more flexible for more
    endpoints

    the doc_link is the unique part of the pdf's url.
    so for example, for the document at:
    https://api.iga.in.gov/2015/bills/hb1001/versions/hb1001.02.comh?format=pdf

    the url here will be:
    in-proxy.openstates.org/2015/bills/hb1001/versions/hb1001.02.comh
    """
    headers = {
        "Authorization": os.environ["INDIANA_API_KEY"],
        "Content-Type": "application/pdf",
        "User-Agent": USER_AGENT,
    }
    full_link = f"https://api.iga.in.gov/{doc_link}?format=pdf"
    page = requests.get(full_link, headers=headers, verify=False)
    return _upstream_to_resp(page)


@app.route("/")
def index():
    return "This is a service used by Open States to access sites with strange requirements (e.g. CA requires POST requests, IN auth proxy) in the browser.  Please use gently."


@app.route("/robots.txt")
def robots_txt():
    return """User-agent: *
Disallow: /"""


if __name__ == "__main__":
    app.run("0.0.0.0", debug=False)
