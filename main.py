from flask import Flask, request, jsonify, render_template
import requests, os, time

app = Flask(__name__)

HF_KEY = os.getenv("HF_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")
    
print("USER MESSAGE:", msg)
print("HF STATUS:", response.status_code)
print("HF RESPONSE:", response.text)

# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")

    # IMAGE
    if any(word in msg.lower() for word in ["draw","image","photo","picture"]):
        API_URL = "https://router.huggingface.co/hf-inference/models/runwayml/stable-diffusion-v1-5"

        headers = {
            "Authorization": f"Bearer {HF_KEY}"
        }

        response = requests.post(API_URL, headers=headers, json={
            "inputs": msg
        })

        if response.status_code == 200:
            filename = f"static/output_{int(time.time())}.png"

            with open(filename, "wb") as f:
                f.write(response.content)

            return jsonify({"type":"image","file":filename})

        return jsonify({"type":"text","message":"Image error"})

    # TEXT (GROQ)
    else:
        from openai import OpenAI

        client = OpenAI(
            api_key=GROQ_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":msg}]
        )

        reply = res.choices[0].message.content

        return jsonify({"type":"text","message":reply})


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
