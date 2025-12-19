import gradio as gr
import requests
import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

# ================= CONFIG =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SHOP_NAME = "Raja Cycle Mart"
SHOP_LOCATION = "SS Puram, Tumkur"
WHATSAPP = "+91 98446 29722"

IST = ZoneInfo("Asia/Kolkata")

# ================= GEMINI =================
def clean_problem_with_gemini(problem):
    if not GEMINI_API_KEY:
        return problem

    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-pro:generateContent?key=" + GEMINI_API_KEY
        )

        prompt = f"""
You are a cycle service assistant.
Convert the customer's message into a short, clear mechanic-friendly issue description.
Do not add extra explanation.

Customer message:
"{problem}"
"""

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        res = requests.post(url, json=payload, timeout=8)
        data = res.json()

        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    except Exception:
        return problem

# ================= TELEGRAM =================
def send_telegram(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=5
        )
        return True
    except:
        return False

# ================= BOOKING =================
def book_service(name, phone, problem):
    if not name.strip() or not problem.strip():
        return "❌ **Please enter your name and cycle issue.**"

    booking_id = f"RCM-{random.randint(1000,9999)}"
    now = datetime.now(IST)
    time_str = now.strftime("%d %b %Y • %I:%M %p (IST)")

    refined_problem = clean_problem_with_gemini(problem)

    telegram_msg = f"""
🚲 *NEW CYCLE SERVICE BOOKING*

🆔 *Booking ID:* `{booking_id}`
👤 *Customer:* {name}
📞 *Phone:* {phone if phone else "Will contact"}
🔧 *Issue:* {refined_problem}

⏰ *Time:* {time_str}
📍 *{SHOP_NAME}*
{SHOP_LOCATION}
"""

    sent = send_telegram(telegram_msg)

    if sent:
        return f"""
✅ **Booking Confirmed!**

🆔 **Booking ID:** `{booking_id}`  
⏰ **Booked at:** {time_str}

📞 Our team will contact you shortly.  
📍 **{SHOP_NAME}, SS Puram**

🙏 Thank you for trusting us!
"""
    else:
        return f"""
⚠️ **Booking Saved**

🆔 **Booking ID:** `{booking_id}`  
⏰ **Time:** {time_str}

📞 Please WhatsApp us:
👉 {WHATSAPP}  
💬 *Booking {booking_id}*

We’ll assist you shortly.
"""

# ================= UI =================
with gr.Blocks(title="Raja Cycle Mart – Smart Booking", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
# 🚲 Raja Cycle Mart  
### Smart Cycle Service Booking  
*Trusted in Tumkur since 1987*
""")

    name = gr.Textbox(label="Your Name", placeholder="Enter your name")
    phone = gr.Textbox(label="Phone Number (optional)")
    problem = gr.Textbox(
        label="Describe the cycle issue",
        placeholder="Example: chain making noise, brake not working...",
        lines=3
    )

    btn = gr.Button("📅 Book Service", variant="primary")
    output = gr.Markdown()

    btn.click(book_service, inputs=[name, phone, problem], outputs=output)

    gr.Markdown("---")
    gr.Markdown("📍 **SS Puram Main Road, Tumkur**  \n📞 **WhatsApp:** +91 98446 29722")

# ================= RUN =================
port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port)


