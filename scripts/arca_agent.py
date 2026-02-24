import argparse
import requests
import zipfile
import io
import smtplib  # NEW: Library for sending emails
from email.mime.text import MIMEText # NEW: Tools for formatting email text
from email.mime.multipart import MIMEMultipart # NEW: Tools for complex emails
import google.generativeai as genai

def send_email(subject, body, to_email, smtp_user, smtp_pass):
    # 1. Prepare the standard Gmail settings
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    # 2. Create the "Envelope"
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # 3. Add the "Letter" (Body)
    msg.attach(MIMEText(body, 'plain'))
    
    print(f"📧 Sending notification to {to_email}...")
    
    try:
        # 4. Connect to the Gmail post office
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Secure the connection
        server.login(smtp_user, smtp_pass)
        
        # 5. Drop the letter in the box
        text = msg.as_string()
        server.sendmail(smtp_user, to_email, text)
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def analyze_with_ai(error_list, api_key):
    # 1. Initialize the Gemini Brain
    genai.configure(api_key=api_key)
    
    # Using 'gemini-flash-latest' - This matches the available model list from your VM.
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # 2. Prepare the context
    error_context = "\n".join(error_list)
    prompt = f"""
    You are a Senior DevOps Engineer. 
    Analyze the following build error logs from a GitHub Action.
    
    IMPORTANT RULES:
    1. PRIORITIZE "Hard Failures" (Connection errors, Dial TCP, Connection Refused, Process Crashes).
    2. IGNORE "Soft Warnings" like Checkstyle, Linter, or Formatting errors IF a hard failure is present.
    3. Identify the ACTUAL ROOT CAUSE that stopped the pipeline and provide a clear one-sentence fix.
    
    Error logs:
    {error_context}
    """
    
    print(f"🧠 Asking Gemini for help...")
    
    # DEBUG: Print exactly what we are sending to the AI
    print("\n--- 🛠️ DEBUG: AI PROMPT START ---")
    print(prompt)
    print("--- 🛠️ DEBUG: AI PROMPT END ---\n")
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "❌ AI Quota Error: You have reached the limit for free requests. Please wait a minute and try again, or check your Google AI Studio billing."
        return f"Error connecting to AI: {e}"

def get_logs(repo, run_id, token):
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    headers = {"Authorization": f"token {token}"}
    
    print(f"Connecting to GitHub API...")
    response = requests.get(url, headers=headers)
    
    found_errors = [] 
    
    if response.status_code == 200:
        print("✅ Successfully found the logs!")
        zip_data = io.BytesIO(response.content)
        
        with zipfile.ZipFile(zip_data) as zip_file:
            # 1. THE CHRONOLOGICAL ORDER
            # GitHub log files are named 1_step.txt, 2_step.txt, etc.
            # Sorting ensures we see the pipeline failing in order.
            file_names = sorted(zip_file.namelist())
            print(f"📦 Searching log files for errors...")
            
            # 2. THE BRAIN'S DICTIONARY
            keywords = ["ERROR", "FAIL", "REFUSED", "UNABLE", "TIMEOUT", "EXCEPTION", "EXIT CODE", "UNABLE TO CONNECT"]
            
            for name in file_names:
                if name.endswith(".txt") and "system" not in name:
                    content = zip_file.read(name).decode("utf-8")
                    lines = content.splitlines()
                    
                    # 3. THE STORYTELLER (Searching for candidate errors)
                    matches_in_file = 0
                    for i in range(len(lines)):
                        current_line = lines[i]
                        line_upper = current_line.upper()
                        
                        if any(key in line_upper for key in keywords):
                            # NOISE FILTER: Skip git checkout messages
                            # (They often contain the word 'error' in commit messages)
                            if "HEAD IS NOW AT" in line_upper or "CHECKOUT" in line_upper:
                                continue
                                
                            print(f"   🔍 Found match in: {name} (Line {i+1})")
                            start = max(0, i - 5)
                            end = min(len(lines), i + 10)
                            
                            context_chunk = "\n".join(lines[start:end])
                            found_errors.append(f"Step Log [{name}]:\n{context_chunk}\n---")
                            
                            # We keep looking to find later errors, but limit to 5 per file
                            matches_in_file += 1
                            if matches_in_file >= 5:
                                break 
    else:
        print(f"❌ Failed to get logs. Error Code: {response.status_code}")

    return found_errors

def main():
    parser = argparse.ArgumentParser(description="ARCA Agent: Automated Root Cause Analysis")
    parser.add_argument("--run-id", help="The GitHub Action Run ID to analyze", required=True)
    parser.add_argument("--repo", help="The full 'owner/repo' name", required=True)
    parser.add_argument("--token", help="GitHub Personal Access Token", required=True)
    parser.add_argument("--gemini-key", help="Google Gemini API Key", required=True)
    
    # NEW: SMTP Arguments for Phase 4
    parser.add_argument("--smtp-user", help="Gmail address to send from", required=True)
    parser.add_argument("--smtp-pass", help="Gmail App Password", required=True)
    parser.add_argument("--to-email", help="Recipient email address", required=True)

    args = parser.parse_args()

    print(f"ARCA Agent Initialized!")
    
    # Step 1: Research (Researcher Assistant)
    errors = get_logs(args.repo, args.run_id, args.token)

    if errors:
        print(f"\n📢 Found {len(errors)} potential issues.")
        
        # Step 2: Analysis (Thinker Assistant)
        ai_analysis = analyze_with_ai(errors, args.gemini_key)
        
        print("\n--- 🧠 ARCA AI ANALYSIS ---")
        print(ai_analysis)
        print("---------------------------\n")

        # Step 3: Notification (Messenger Assistant)
        # We take the output of Step 2 (ai_analysis) and hand it to the emailer
        subject = f"🚨 ARCA Analysis: Failure in {args.repo} (Run #{args.run_id})"
        send_email(subject, ai_analysis, args.to_email, args.smtp_user, args.smtp_pass)
        
    else:
        print("✅ No errors found. Pipeline looks healthy!")

if __name__ == "__main__":
    main()
