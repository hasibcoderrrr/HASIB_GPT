import os
import json
import uuid
from flask import Flask, request, jsonify, render_template, Response
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "hasibgpt_super_secret_2026"  # এটি Flask-এর সিক্রেট, API Key নয়

# 🔑 আপনার দেওয়া OpenAI API Key (এখনই Revoke করে নতুন করে নিন)
OPENAI_API_KEY = "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"

# ✅ OpenAI ক্লায়েন্ট (DeepSeek নয়, তাই base_url বাদ দিতে হবে অথবা OpenAI সেট করতে হবে)
client = OpenAI(
    api_key=OPENAI_API_KEY,
    # base_url = "https://api.openai.com/v1"  # এটি ডিফল্ট, লেখার দরকার নেই
)

conversations = {}

SYSTEM_PROMPT = """You are HASIBGPT, an advanced AI assistant created by HASIB CODEX.
If anyone asks who created you, say: "I am HASIBGPT, created by HASIB CODEX. 
Please subscribe to his YouTube channel @hasib_hi, follow him on TikTok @connector, 
and join his Telegram @connector."
Answer in the same language as the user's question. Be helpful and concise.
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    session_id = data.get('session_id', str(uuid.uuid4()))
    user_message = data.get('message', '').strip()
    
    if session_id not in conversations:
        conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    conversations[session_id].append({"role": "user", "content": user_message})
    
    def generate():
        try:
            # 🚀 OpenAI GPT-4o-mini মডেল (সস্তা এবং দ্রুত)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # অথবা "gpt-3.5-turbo" বা "gpt-4o"
                messages=conversations[session_id][-10:],
                stream=True,
                temperature=0.7
            )
            collected = []
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    collected.append(content)
                    yield f"data: {json.dumps({'token': content})}\n\n"
            
            full_reply = "".join(collected)
            conversations[session_id].append({"role": "assistant", "content": full_reply})
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'API তে সমস্যা: {str(e)}'})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route('/clear/<session_id>', methods=['POST'])
def clear_history(session_id):
    if session_id in conversations:
        conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)