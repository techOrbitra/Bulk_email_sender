# Bulk Mail Sender for Gmail

Privacy-first Streamlit app to send personalized Gmail emails from CSV + INI templates with optional attachments.

## SEO Summary
Bulk Mail Sender for Gmail helps you send personalized bulk emails from a CSV file and INI template using Gmail SMTP. It supports optional attachments, subject alternation, and To/Cc splitting from a single email field.

Primary intent keywords:
- bulk mail sender
- gmail bulk email sender python
- streamlit email automation
- send personalized emails from csv
- ini template email sender

## Features
- Send bulk emails from a CSV recipient list
- Personalize content using placeholders like `{name}` and `{email}`
- Use INI templates for reusable subject/body content
- Alternate subjects with `subject_1` and `subject_2`
- Safe fallback: if `subject_2` is missing, `subject_1` is used for all mails
- Split two emails in one CSV cell into `To` and `Cc`
- Attach any file type (optional)
- No credential/data persistence by app design (runtime entry)

## CSV Format
Use at least an `email` column.

```csv
name,email
Oceanlab,hr@oceanlab.example
Creatuaries,"tapan.gajera@creatuaries.com,info@creatuaries.com"
```

Notes:
- Single email -> sent in `To`
- Two comma-separated emails -> first in `To`, second in `Cc`

## Template INI Format
```ini
[email]
subject_1 = Full Stack Developer Application | Job Application
subject_2 = Fell In Love With Coding | Full Stack Developer Application
reply_to =
body = Hello {name},
 
 Thank you for your time.
 Please find my resume attached for your review.
 
 Regards,
 Your Name
```

Notes:
- `subject_1` is the primary subject
- `subject_2` is optional
- Keep multiline `body` lines indented (INI continuation format)

## Setup
1. Create and activate virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run
```powershell
streamlit run app.py
```

Or use the provided launcher:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_app.ps1
```

## Gmail App Password
1. Enable 2-Step Verification in your Google Account.
2. Go to Security -> App passwords.
3. Generate a Mail app password.
4. Paste it into the app when sending.

## Privacy
- Credentials are entered at runtime in the UI.
- The app is intended to avoid storing user credentials or uploaded data.
- Refreshing the page clears entered values and interrupts in-progress sending.

## Included Samples
- `sample_recipients.csv`
- `sample_template.ini`

## FAQ
### What happens if subject_2 is not provided?
No issue. The app automatically uses subject_1 for every email.

### Can I send emails without attachment?
Yes. Attachment is optional.

### Can I send one email to To and another to Cc from CSV?
Yes. In the email column, provide two comma-separated addresses. First goes to To, second to Cc.

### Does this project store my credentials or uploaded files?
No. Credentials are entered at runtime and the app is intended for session-only use.

## GEO and AEO Notes
- GEO (Generative Engine Optimization): README includes concise product purpose, capabilities, and limitations for better AI citation.
- AEO (Answer Engine Optimization): FAQ format is included so answer engines can extract direct answers quickly.

## Tech Stack
- Python
- Streamlit
- CSV
- Gmail SMTP
