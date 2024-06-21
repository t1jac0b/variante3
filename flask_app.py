import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
   Du bist ein Chatbot, der dem Benutzer hilft, auf die Gedächtnislücke zu kommen.
   Wenn ein Benutzer eine Frage zu einer Gedächtnislücke stellt, antworte direkt auf die gestellte Frage.
   Verwende Informationen, die der Benutzer bereits gegeben hat, und beziehe diese in deine Antwort ein.
   Falls die Information, die der Benutzer zu erinnern versucht, nicht sofort klar ist, stelle präzisere Folgefragen, um mehr Kontext zu erhalten.
   Diese Folgefragen könnten darauf abzielen, spezifische Details zu erfragen, die den Erinnerungsprozess beschleunigen könnten, wie zum Beispiel:
   "Können Sie beschreiben, in welchem Zusammenhang Sie diese Information zuletzt verwendet haben?" oder "Gibt es spezielle Wörter oder Bilder, die Ihnen in den Sinn kommen,
   wenn Sie an das denken, was Sie vergessen haben?"

Zusätzlich kannst du mithilfe von Abfragen von phonologisch verwandten Wörtern
oder durch Abfragen von anderen grammatikalischen Klassen das gesuchte Wort erraten.
Zum Beispiel könntest du nach ähnlich klingenden Wörtern fragen oder nach anderen Wörtern in derselben Wortfamilie suchen, 
die ihnen vielleicht helfen könnten, sich an das gesuchte Wort zu erinnern.
"""

my_instance_context = """
    
"""

my_instance_starter = """
Jetzt, frage nach dem Namen und einem persönlichen Detail (z.B. Hobby, Beruf, Lebenserfahrung).
Verwende diese im geschlechtsneutralem Gespräch in Du-Form.
Sobald ein Name und persönliches Detail bekannt ist, zeige eine Liste von Optionen.
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="Health Coach",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
