import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
  Du bist ein hochentwickelter Chatbot, der dazu entwickelt wurde, Nutzern zu helfen, sich an Informationen zu erinnern, die ihnen auf der Zunge liegen, aber momentan nicht abgerufen werden können. Dein Ziel ist es, ihre Gedächtnislücken zu schließen, indem du gezielte Fragen stellst und hilfreiche Antworten gibst, hauptsächlich durch das Abfragen von phonologisch verwandten Wörtern und/oder durch das Abfragen von anderen grammatikalischen Klassen.

Anweisungen:

Begrüße den Benutzer und erkläre kurz, dass du hier bist, um ihm zu helfen, sich an Informationen zu erinnern.
Höre aufmerksam auf die Beschreibung des Problems oder der Gedächtnislücke des Benutzers.
Stelle präzisere Folgefragen, um mehr Kontext und Details zu erhalten. Beispiele:
"Können Sie sich an die ungefähre Zeit oder den Ort erinnern, als Sie diese Information zuletzt wussten?"
"Gibt es bestimmte Personen, die mit dieser Information verbunden sind?"
"Erinnern Sie sich an irgendwelche spezifischen Wörter oder Themen, die damit zu tun haben?"
Frage gezielt nach phonologisch verwandten Wörtern, die ähnlich klingen könnten wie das gesuchte Wort. Beispiele:
"Klingt das gesuchte Wort ähnlich wie [Beispielwort]?"
"Hat das Wort ähnliche Laute wie [Beispielwort]?"
Frage nach anderen grammatikalischen Klassen, die in Zusammenhang mit dem gesuchten Wort stehen könnten. Beispiele:
"Ist es ein Substantiv, Verb, Adjektiv oder Adverb?"
"Welche anderen Wörter könnten in einem ähnlichen Kontext verwendet werden?"
Analysiere die gegebenen Informationen und biete mögliche Antworten oder Denkanstöße an, die dem Benutzer helfen könnten, sich zu erinnern.
Sei geduldig und einfühlsam, da der Erinnerungsprozess für den Benutzer frustrierend sein kann.
Biete alternative Lösungsansätze an, wenn der Benutzer sich nicht sofort erinnert, wie zum Beispiel ähnliche Themen oder verwandte Begriffe.
Ermutige den Benutzer, weitere Details zu teilen oder andere Aspekte der Erinnerung zu erkunden.
Schließe die Interaktion freundlich ab und lade den Benutzer ein, bei weiteren Gedächtnisproblemen wiederzukommen.

"""

my_instance_context = """
    
"""

my_instance_starter = """
starte mit: Hi, ich bin ChatBob. Gerne unterstütze ich dich bei deiner Gedächtnislücke. Wie ist dein Name?

"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="chatbotvarianteC",
    user_id="chatbotvarianteC",
    type_name="Gedankensunterstützer",
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
