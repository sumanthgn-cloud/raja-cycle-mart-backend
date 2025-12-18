import gradio as gr
import requests
import os
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_booking(name, problem):
    if not BOT_TOKEN or not CHAT_ID:
        return "Bot not configured."

    msg = f"""
🚲 NEW BOOKING – Raja Cycle Mart

👤 Name: {name}
🔧 Problem: {problem}
⏰ Time: {datetime.now().strftime('%I:%M %p')}
"""

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
        return "✅ Booking sent! Owner will contact you."
    except:
        return "⚠️ Booking saved. Please WhatsApp the shop."

with gr.Blocks() as app:
    gr.Markdown("# 🚲 Raja Cycle Mart – Service Booking")

    name = gr.Textbox(label="Your Name")
    problem = gr.Textbox(label="Cycle Problem", lines=2)
    btn = gr.Button("Book Service")
    out = gr.Markdown()

    btn.click(send_booking, [name, problem], out)

port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port)

