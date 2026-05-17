import azure.functions as func
import logging
from verse import get_verses
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    book = req.params.get("book")
    chapter = req.params.get("chapter")
    verse_num = req.params.get("verse_num")

    if book and chapter and verse_num:
        verses = get_verses(book, chapter, verse_num)
        return func.HttpResponse(
            json.dumps(verses), mimetype="application/json", status_code=200
        )
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200,
        )
