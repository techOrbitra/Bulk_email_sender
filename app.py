import streamlit as st
from pathlib import Path

from mailer import bulk_send_from_csv


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
FALLBACK_SUBJECT = "Job Application"
BASE_DIR = Path(__file__).resolve().parent


def get_sample_text(file_name, fallback_text):
    file_path = BASE_DIR / file_name
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return fallback_text

st.set_page_config(
    page_title="Bulk Mail Sender for Gmail",
    page_icon="✉️",
    layout="wide",
    menu_items={
        "About": "Bulk Mail Sender for Gmail - Send personalized bulk emails from CSV and INI templates with optional attachments.",
    },
)
st.title("Mail Sender")
st.caption("Send template-based emails to recipients from a CSV file, with an optional attachment.")
st.info("Your files and credentials are used only for this session. We do not store your data.")
st.warning("If you refresh this page, entered values are cleared and any in-progress mailing is interrupted. Keep a stable internet connection before sending.")

with st.expander("How to generate Gmail App Password", expanded=False):
    st.markdown(
        """
1. Open your Google Account and enable 2-Step Verification.
2. Go to Security -> App passwords.
3. Select app type as Mail (or Custom name), then click Generate.
4. Copy the 16-character app password and paste it in this app.
        """
    )

with st.expander("FAQ", expanded=False):
        st.markdown(
                """
- What if subject_2 is missing?
    No issue. The app uses subject_1 for all recipients.
- Can I send mail without attachment?
    Yes. Attachment is optional.
- Can I send to CC from CSV?
    Yes. If the email column has two addresses separated by a comma, first goes to To and second goes to Cc.
- Does this app store my credentials or files?
    No. This app is designed for session-only usage.
                """
        )

with st.sidebar:
    st.header("Sender Details")
    sender_email = st.text_input("Sender Gmail", value="", placeholder="you@gmail.com")
    sender_password = st.text_input("Gmail app password", value="", type="password")
    reply_to = st.text_input("Reply-to email (optional)", value="", placeholder="Leave blank to use sender email")
    st.divider()
    st.subheader("SMTP (Fixed)")
    st.text_input("SMTP host", value=SMTP_HOST, disabled=True)
    st.number_input("SMTP port", min_value=1, max_value=65535, value=SMTP_PORT, disabled=True)
    st.checkbox("Use TLS", value=SMTP_USE_TLS, disabled=True)

st.subheader("Files")
col1, col2, col3 = st.columns(3)
with col1:
    csv_file = st.file_uploader("CSV file with recipients", type=["csv"])
with col2:
    template_file = st.file_uploader("Template INI file", type=["ini"])
with col3:
    resume_file = st.file_uploader("Attachment (optional)")

sample_cols = st.columns(2)
with sample_cols[0]:
    st.download_button(
        "Download sample CSV",
        data=get_sample_text(
            "sample_recipients.csv",
            "name,email\nCompany Name,hr@example.com\n",
        ),
        file_name="sample_recipients.csv",
        mime="text/csv",
        use_container_width=True,
    )
with sample_cols[1]:
    st.download_button(
        "Download sample INI",
        data=get_sample_text(
            "sample_template.ini",
            "[email]\nsubject_1 = Job Application\nbody = Hello {name},\n",
        ),
        file_name="sample_template.ini",
        mime="text/plain",
        use_container_width=True,
    )

preview_cols = st.columns(2)
with preview_cols[0]:
    st.markdown("### CSV preview")
    if csv_file:
        st.dataframe(__import__("pandas").read_csv(csv_file).head(20), use_container_width=True)
    else:
        st.info("Upload a CSV with at least an email column.")
with preview_cols[1]:
    st.markdown("### Template notes")
    st.write("Template placeholders use Python format fields like {name} and {email}.")
    st.write("Use subject_1 and subject_2 in INI for alternating subject lines.")
    st.write("If subject_2 is missing, subject_1 is used for all recipients.")
    st.write("Sample files: sample_template.ini and sample_recipients.csv")

send_clicked = st.button("Send emails", type="primary", use_container_width=True)

if send_clicked:
    if not csv_file or not template_file:
        st.error("Please upload the CSV and INI template before sending.")
    elif not sender_email:
        st.error("Please enter your sender Gmail address.")
    elif not sender_password:
        st.error("Please provide your Gmail app password.")
    else:
        effective_reply_to = reply_to.strip() or sender_email.strip()
        with st.spinner("Sending emails..."):
            result = bulk_send_from_csv(
                csv_file=csv_file,
                template_file=template_file,
                resume_file=resume_file,
                smtp_host=SMTP_HOST,
                smtp_port=SMTP_PORT,
                use_tls=SMTP_USE_TLS,
                sender_email=sender_email.strip(),
                sender_password=sender_password,
                reply_to=effective_reply_to,
                subject=FALLBACK_SUBJECT,
            )
        st.success(f"Done. Sent {result['sent']} emails, failed {result['failed']}.")
        if result["errors"]:
            st.error("Some recipients failed.")
            st.dataframe(result["errors"], use_container_width=True)
