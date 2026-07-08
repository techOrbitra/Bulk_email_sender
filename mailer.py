import configparser
import csv
import io
import mimetypes
import os
import tempfile
from email.message import EmailMessage
from pathlib import Path
import smtplib


REQUIRED_EMAIL_COLUMNS = ("email",)


def parse_email_targets(email_value):
    parts = [part.strip() for part in str(email_value).split(",") if part.strip()]
    if not parts:
        return "", None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]


def read_file_text(file_obj):
    if hasattr(file_obj, "getvalue"):
        return file_obj.getvalue().decode("utf-8-sig")
    if hasattr(file_obj, "read"):
        content = file_obj.read()
        if isinstance(content, bytes):
            return content.decode("utf-8-sig")
        return content
    return Path(file_obj).read_text(encoding="utf-8-sig")


def read_template_ini(template_file):
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(read_file_text(template_file))
    if not parser.has_section("email"):
        raise ValueError("Template INI must contain an [email] section.")
    return dict(parser["email"])


def normalize_csv_rows(csv_file):
    reader = csv.DictReader(io.StringIO(read_file_text(csv_file)))
    if not reader.fieldnames:
        raise ValueError("CSV file is empty or missing a header row.")
    headers = {header.strip().lower() for header in reader.fieldnames}
    if not all(column in headers for column in REQUIRED_EMAIL_COLUMNS):
        raise ValueError("CSV must include an email column.")

    rows = []
    for row in reader:
        normalized = {key.strip().lower(): (value or "").strip() for key, value in row.items()}
        extra_values = row.get(None, [])
        if extra_values:
            extra_values = [value.strip() for value in extra_values if value and value.strip()]
            if extra_values:
                normalized["email"] = ",".join(filter(None, [normalized.get("email", ""), *extra_values]))
        to_email, cc_email = parse_email_targets(normalized.get("email", ""))
        if to_email:
            normalized["raw_email"] = normalized.get("email", "")
            normalized["email"] = to_email
            normalized["to_email"] = to_email
            normalized["cc_email"] = cc_email or ""
            rows.append(normalized)
    return rows


def build_message(sender_email, recipient, subject, body_template, reply_to, attachment_path, attachment_filename=None):
    body = body_template.format(**recipient)
    to_email = recipient.get("to_email") or recipient.get("email", "")
    cc_email = recipient.get("cc_email", "") or None

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = to_email
    if cc_email:
        message["Cc"] = cc_email
    message["Subject"] = subject.format(**recipient)
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(body)

    if attachment_path:
        attachment_bytes = Path(attachment_path).read_bytes()
        mime_type, _ = mimetypes.guess_type(str(attachment_path))
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
        message.add_attachment(
            attachment_bytes,
            maintype=maintype,
            subtype=subtype,
            filename=attachment_filename or Path(attachment_path).name,
        )
    return message


def send_message(smtp_host, smtp_port, use_tls, sender_email, sender_password, message):
    with smtplib.SMTP(smtp_host, smtp_port, timeout=60) as smtp:
        if use_tls:
            smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.send_message(message)


def bulk_send_from_csv(
    csv_file,
    template_file,
    resume_file,
    smtp_host,
    smtp_port,
    use_tls,
    sender_email,
    sender_password,
    reply_to,
    subject,
):
    template = read_template_ini(template_file)
    rows = normalize_csv_rows(csv_file)
    if not rows:
        return {"sent": 0, "failed": 0, "errors": []}

    temp_path = None
    attachment_filename = None
    if resume_file is not None:
        if hasattr(resume_file, "getbuffer"):
            attachment_filename = Path(getattr(resume_file, "name", "attachment")).name
            suffix = Path(getattr(resume_file, "name", "attachment")).suffix or ".bin"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(resume_file.getbuffer())
                temp_path = temp_file.name
        else:
            temp_path = str(resume_file)
            attachment_filename = Path(temp_path).name

    errors = []
    sent = 0
    failed = 0

    body_template = template.get("body", "")
    subject_1 = template.get("subject_1", template.get("subject", subject))
    subject_2 = template.get("subject_2", subject_1)
    template_reply_to = template.get("reply_to", reply_to)

    try:
        for index, recipient in enumerate(rows):
            try:
                email_subject = subject_1 if index % 2 == 0 else subject_2
                message = build_message(
                    sender_email=sender_email,
                    recipient=recipient,
                    subject=email_subject,
                    body_template=body_template,
                    reply_to=template_reply_to,
                    attachment_path=temp_path,
                    attachment_filename=attachment_filename,
                )
                send_message(
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    use_tls=use_tls,
                    sender_email=sender_email,
                    sender_password=sender_password,
                    message=message,
                )
                sent += 1
            except Exception as exc:
                failed += 1
                errors.append({"email": recipient.get("email", ""), "error": str(exc)})
    finally:
        if resume_file is not None and hasattr(resume_file, "getbuffer") and temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return {"sent": sent, "failed": failed, "errors": errors}
