import xmlrpc.client
import time
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ================= CONFIGURATION =================
# Load environment variables from .env file
load_dotenv()

# Odoo Configuration - from .env file
URL = os.getenv("ODOO_URL")
DB = os.getenv("ODOO_DB")
USERNAME = os.getenv("ODOO_USERNAME")
PASSWORD = os.getenv("ODOO_PASSWORD")

# Groq API Configuration - from .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Company Information (can remain in code if not sensitive)
COMPANY_NAME = "innoSoul inc."
HR_NAME = "Administrator"
# =================================================

def connect_to_odoo():
    """Connect to Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        if uid:
            models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
            return uid, models
    except Exception as e:
        print(f"❌ Connection error: {e}")
    return None, None

def test_groq_api():
    """Test Groq API with current models"""
    print("🧪 Testing Groq API...")
   
    models_to_test = [
        "llama-3.1-8b-instant",
        "llama-3.2-1b-preview",
        "gemma2-9b-it"
    ]
   
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
   
    for model in models_to_test:
        print(f"   Testing model: {model}")
       
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a professional HR assistant."},
                {"role": "user", "content": "Hello, write a short test message."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
       
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
           
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content']
                print(f"   ✅ {model} WORKS!")
                return model
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown')
                print(f"   ❌ Failed: {error_msg[:80]}")
               
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
   
    print("\n❌ No models worked! Check your API key.")
    return None

def get_ai_response_groq(text, model_name, applicant_name):
    """Get AI response from Groq API"""
    print(f"      🤖 Generating AI response...")
   
    clean_text = str(text or "").strip()
    if not clean_text or len(clean_text) < 10:
        print("      ⚠️ Text too short")
        return None
   
    print(f"      📝 Analyzing message...")
   
    # Smart prompt - AI writes ONLY the body
    prompt = f"""You are an HR assistant for {COMPANY_NAME}.

Applicant Name: {applicant_name}
Applicant's Message: "{clean_text[:400]}"

Write ONLY the body/content of the email reply. DO NOT include:
- "Dear [Name]" or any greeting
- "Best regards" or any signature
- Your name or company name

Guidelines:
1. Address their specific message directly
2. Be warm, professional, and helpful
3. Keep it concise (3-4 sentences)
4. Focus on being helpful

Write ONLY the email body content:"""
   
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
   
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": f"""You are a professional HR assistant at {COMPANY_NAME}.
                ONLY provide the email body content.
                DO NOT include greetings or closings."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 200,
        "stream": False
    }
   
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
       
        if response.status_code == 200:
            result = response.json()
            ai_text = result['choices'][0]['message']['content']
           
            # Clean up
            import re
            ai_text = ai_text.strip()
            ai_text = re.sub(r'^(Dear\s+[^,\n]+,?\s*)', '', ai_text, flags=re.IGNORECASE)
            ai_text = re.sub(r'(Best\s+regards,?|Sincerely,?|Regards,?).*$', '', ai_text, flags=re.IGNORECASE | re.DOTALL)
            ai_text = ai_text.strip()
           
            print(f"      ✅ AI response generated")
            return ai_text
           
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown')
            print(f"      ❌ API Error: {error_msg[:100]}")
            return None
           
    except Exception as e:
        print(f"      ❌ Connection error: {e}")
        return None

def create_chatter_message(models, uid, applicant_id, ai_response, candidate_message, email_sent=True):
    """Save AI response in Odoo chatter"""
    try:
        import re
        clean_candidate = re.sub(r'<[^>]+>', '', candidate_message)
       
        message_body = f"""
        <div style="font-family: Arial, sans-serif; padding: 15px;">
            <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 4px solid #0d6efd;">
                <strong style="color: #0d6efd;">📥 Candidate's Message:</strong>
                <p style="margin: 8px 0; color: #212529; line-height: 1.5;">{clean_candidate[:200]}{'...' if len(clean_candidate) > 200 else ''}</p>
            </div>
           
            <div style="background: #d1e7dd; padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 4px solid #198754;">
                <strong style="color: #198754;">🤖 AI Auto-Reply:</strong>
                <p style="margin: 8px 0; color: #0f5132; line-height: 1.5;">{ai_response}</p>
            </div>
           
            <div style="font-size: 12px; color: #666;">
                <strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        """
       
        message_id = models.execute_kw(
            DB, uid, PASSWORD,
            'mail.message', 'create',
            [{
                'model': 'hr.applicant',
                'res_id': applicant_id,
                'body': message_body,
                'subject': 'AI Auto-Reply',
                'message_type': 'comment',
                'subtype_id': 1,
                'author_id': uid,
            }]
        )
       
        print(f"      💬 Saved to chatter")
        return True
       
    except Exception as e:
        print(f"      ⚠️ Chatter error: {e}")
        return False

def format_email_body(applicant_name, ai_response):
    """Format professional email body"""
    # Extract first name
    first_name = applicant_name.split()[0] if applicant_name and ' ' in applicant_name else applicant_name
   
    # Clean AI response
    import re
    clean_response = ai_response.strip()
    clean_response = re.sub(r'^(Dear\s+[^,\n]+,?\s*)', '', clean_response, flags=re.IGNORECASE)
    clean_response = re.sub(r'(Best\s+regards,?|Sincerely,?|Regards,?).*$', '', clean_response, flags=re.IGNORECASE | re.DOTALL)
    clean_response = clean_response.strip()
   
    # Professional HTML email
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            background: #f8f9fa;
        }}
        .email-container {{
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            color: white;
            text-align: center;
        }}
        .content {{
            padding: 30px;
        }}
        .greeting {{
            font-size: 16px;
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        .message-body {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
            margin: 20px 0;
            font-size: 15px;
            line-height: 1.7;
        }}
        .signature {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h2 style="margin: 0;">{COMPANY_NAME}</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Human Resources Department</p>
        </div>
       
        <div class="content">
            <div class="greeting">
                Dear {first_name},
            </div>
           
            <div class="message-body">
                {clean_response.replace('\n', '<br>')}
            </div>
           
            <div class="signature">
                <p style="margin: 0 0 5px 0; font-weight: bold;">{HR_NAME}</p>
                <p style="margin: 0; color: #6c757d;">HR Assistant</p>
                <p style="margin: 5px 0 0 0; color: #6c757d;">{COMPANY_NAME}</p>
            </div>
        </div>
    </div>
</body>
</html>"""

def send_email(models, uid, applicant_id, recipient_email, applicant_name, ai_response):
    """Send email to candidate"""
    try:
        print(f"      📧 Sending email...")
       
        # Get sender email
        user_data = models.execute_kw(DB, uid, PASSWORD,
            'res.users', 'read', [uid, ['email']])
        sender_email = user_data[0].get('email', 'hr@company.com')
       
        # Format email
        email_body = format_email_body(applicant_name, ai_response)
       
        # Create mail.mail record
        mail_data = {
            'subject': 'Re: Your Application',
            'body_html': email_body,
            'email_to': recipient_email,
            'email_from': f'HR Department <{sender_email}>',
            'state': 'outgoing',
            'model': 'hr.applicant',
            'res_id': applicant_id,
            'auto_delete': True,
        }
       
        mail_id = models.execute_kw(DB, uid, PASSWORD,
            'mail.mail', 'create', [mail_data])
       
        print(f"      ✅ Email created")
       
        # Try to send
        try:
            models.execute_kw(DB, uid, PASSWORD, 'mail.mail', 'send', [[mail_id]])
            print(f"      📤 Email sent")
        except:
            print(f"      ⚡ Email queued")
       
        return True
       
    except Exception as e:
        print(f"      ❌ Email error: {e}")
        return False

def main():
    """Main bot function"""
    print("\n" + "="*60)
    print("   🤖 ODOO AI AUTO-REPLY BOT - CLEAN VERSION")
    print("="*60 + "\n")
   
    # Test Groq API
    working_model = test_groq_api()
    if not working_model:
        print("\n❌ Failed to connect to Groq API.")
        return
   
    print(f"\n✅ Using model: {working_model}")
   
    # Connect to Odoo
    uid, models = connect_to_odoo()
    if not uid:
        print("❌ Failed to connect to Odoo")
        return
   
    print(f"✅ Connected to Odoo (User ID: {uid})")
   
    # Track processed applicants in this session
    processed_applicants = set()
   
    print("\n🔄 Starting to monitor for NEW emails...")
    print("⏰ Only processing NEW, un-replied emails\n")
   
    while True:
        try:
            # Track new emails count
            new_emails_count = 0
           
            # Find emails from last 24 hours
            time_threshold = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
           
            message_ids = models.execute_kw(DB, uid, PASSWORD,
                'mail.message', 'search', [[
                    ('model', '=', 'hr.applicant'),
                    ('message_type', '=', 'email'),
                    ('author_id.name', '!=', 'OdooBot'),
                    ('create_date', '>', time_threshold)
                ]], {'order': 'create_date asc'})
           
            if message_ids:
                messages = models.execute_kw(DB, uid, PASSWORD,
                    'mail.message', 'read',
                    [message_ids, ['id', 'res_id', 'body', 'subject', 'author_id', 'create_date', 'email_from']])
               
                # First, count only NEW emails (not already replied)
                for msg in messages:
                    applicant_id = msg['res_id']
                   
                    # Check if already replied (in chatter)
                    existing_replies = models.execute_kw(DB, uid, PASSWORD,
                        'mail.message', 'search', [[
                            ('model', '=', 'hr.applicant'),
                            ('res_id', '=', applicant_id),
                            ('body', 'ilike', 'AI Auto-Reply'),
                            ('create_date', '>', msg['create_date'])
                        ]])
                   
                    if not existing_replies:
                        new_emails_count += 1
               
                # Now process only NEW emails
                if new_emails_count > 0:
                    print(f"📩 Found {new_emails_count} NEW email(s) to process")
                   
                    processed = 0
                   
                    for msg in messages:
                        applicant_id = msg['res_id']
                       
                        # Skip if already processed in this session
                        if applicant_id in processed_applicants:
                            continue
                       
                        # Check if already replied (in database)
                        existing_replies = models.execute_kw(DB, uid, PASSWORD,
                            'mail.message', 'search', [[
                                ('model', '=', 'hr.applicant'),
                                ('res_id', '=', applicant_id),
                                ('body', 'ilike', 'AI Auto-Reply'),
                                ('create_date', '>', msg['create_date'])
                            ]])
                       
                        if existing_replies:
                            # Silently skip - don't show any message
                            processed_applicants.add(applicant_id)
                            continue
                       
                        print(f"\n   🔍 Processing NEW applicant")
                        print(f"   📝 Subject: {msg.get('subject', 'No subject')[:60]}...")
                       
                        # Get applicant details
                        applicant = models.execute_kw(DB, uid, PASSWORD,
                            'hr.applicant', 'read', [applicant_id, ['partner_name', 'email_from', 'display_name']])
                       
                        if not applicant:
                            processed_applicants.add(applicant_id)
                            continue
                       
                        applicant = applicant[0]
                        applicant_name = applicant.get('partner_name') or applicant.get('display_name') or "Applicant"
                        recipient_email = applicant.get('email_from') or msg.get('email_from')
                       
                        if not recipient_email:
                            processed_applicants.add(applicant_id)
                            continue
                       
                        print(f"   👤 {applicant_name}")
                        print(f"   📧 {recipient_email}")
                       
                        # Get AI response
                        candidate_message = msg.get('body', '')
                        ai_response = get_ai_response_groq(candidate_message, working_model, applicant_name)
                       
                        if not ai_response:
                            processed_applicants.add(applicant_id)
                            continue
                       
                        print(f"   💬 {ai_response[:80]}...")
                       
                        # Send email
                        email_sent = send_email(models, uid, applicant_id, recipient_email, applicant_name, ai_response)
                       
                        # Save to chatter
                        chatter_saved = create_chatter_message(
                            models, uid, applicant_id, ai_response, candidate_message, email_sent
                        )
                       
                        if email_sent or chatter_saved:
                            processed += 1
                            print(f"   ✅ Processed")
                       
                        # Mark as processed in this session
                        processed_applicants.add(applicant_id)
                   
                    if processed > 0:
                        print(f"\n✅ Successfully processed {processed} new email(s)")
                    else:
                        print(f"\n📭 All emails already replied")
                else:
                    # No NEW emails found
                    pass
            else:
                # No emails found at all
                pass
           
            # Wait for next check
            print(f"\n⏰ Next check in 30 seconds...")
            time.sleep(30)
           
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()