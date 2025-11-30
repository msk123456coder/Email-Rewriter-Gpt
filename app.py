from flask import Flask, render_template, request, send_file
import requests
import io
import os

app = Flask(__name__)

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-20b:free"

CHAR_LIMIT = 1000


def extract_reply(data):
    print("DEBUG RAW RESPONSE:", data)

    if "choices" in data:
        choice = data["choices"][0]
        if "message" in choice:
            return choice["message"]["content"]
        if "text" in choice:
            return choice["text"]

    if "response" in data:
        return data["response"]

    if "output_text" in data:
        return data["output_text"]

    return "Could not read response:\n\n" + str(data)


def call_deepseek_api(email, tone):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Rewrite the following email in a **{tone}** tone.
Improve grammar, clarity and professionalism:

\"\"\"{email}\"\"\"
"""

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(API_URL, json=body, headers=headers)
    data = response.json()

    return extract_reply(data)


@app.route("/", methods=["GET", "POST"])
def index():
    rewritten = None
    original = None
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()   # FIXED HERE
        tone = request.form.get("tone", "Formal")

        if not email:
            error = "Email cannot be empty."
        elif len(email) > CHAR_LIMIT:
            error = "Email exceeds 1000 characters."
        else:
            original = email
            rewritten = call_deepseek_api(email, tone)

    return render_template("index.html",
                           rewritten=rewritten,
                           original=original,
                           error=error)


@app.route("/download")
def download():
    text = request.args.get("text", "")
    file = io.BytesIO(text.encode("utf-8"))
    return send_file(file, as_attachment=True, download_name="rewritten_email.txt")


if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(host=HOST, port=PORT, debug=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
