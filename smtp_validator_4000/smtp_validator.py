import argparse
import csv
import json
import re
import socket
import smtplib
from pathlib import Path

import dns.resolver

# Simple RFC 5322 email regex (works for most addresses)
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
)

def load_emails(input_path: str, column: str = None) -> list:
    """
    Load emails from a CSV (using header row) or plain text file.
    If column is specified, use that header; otherwise use first column.
    """
    path = Path(input_path)
    emails = []
    if path.suffix.lower() == '.csv':
        with path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames or []
            if not headers:
                return emails
            col = column if column in headers else headers[0]
            for row in reader:
                value = row.get(col)
                if value:
                    emails.append(value.strip())
    else:
        with path.open(encoding='utf-8') as f:
            for line in f:
                email = line.strip()
                if email:
                    emails.append(email)
    return emails


def validate_syntax(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def get_mx_records(domain: str) -> list:
    """
    Retrieve MX records for a domain.
    """
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        records = sorted(
            [(r.preference, str(r.exchange).rstrip('.')) for r in answers],
            key=lambda x: x[0]
        )
        return [host for _, host in records]
    except Exception:
        return []


def smtp_check(email: str, mx_hosts: list, timeout: int) -> dict:
    """
    Perform SMTP handshake to verify mailbox exists (sans delivery).
    """
    result = {'smtp_valid': False, 'smtp_error': None, 'mx_hosts': mx_hosts}
    if not mx_hosts:
        result['smtp_error'] = 'No MX records found'
        return result

    for host in mx_hosts:
        try:
            with smtplib.SMTP(host, 25, timeout=timeout) as server:
                server.ehlo_or_helo_if_needed()
                from_addr = 'validator@localdomain.com'
                code, _ = server.mail(from_addr)
                if code != 250:
                    continue
                code, _ = server.rcpt(email)
                if code in (250, 251):
                    result['smtp_valid'] = True
                    return result
                else:
                    result['smtp_error'] = f'RCPT rejected ({code})'
        except (socket.error, smtplib.SMTPException) as e:
            result['smtp_error'] = str(e)
    return result


def main():
    parser = argparse.ArgumentParser(description='SMTP Email Validator')
    parser.add_argument(
        '--file', '-f',
        help=('Comma-separated list of file names or full paths to process. '
              'If a name without path is given, it is looked up in data/dirty_data. '
              'If omitted, all .csv/.txt in data/dirty_data are processed.')
    )
    parser.add_argument(
        '--column', '-c', default=None,
        help='CSV header name for email addresses (default: first column)'
    )
    parser.add_argument(
        '--timeout', '-t', type=int, default=10,
        help='Timeout in seconds for SMTP connections'
    )
    parser.add_argument(
        '--output', '-o', default='data/validation_results.json',
        help='Path to save JSON results'
    )
    args = parser.parse_args()

    default_dir = Path('data/dirty_data')
    files_to_process = []

    if args.file:
        for fname in args.file.split(','):
            candidate = Path(fname.strip())
            if candidate.is_file():
                files_to_process.append(candidate)
            else:
                alt = default_dir / candidate
                if alt.is_file():
                    files_to_process.append(alt)
                else:
                    print(f"Warning: File not found {fname.strip()}")
    else:
        if default_dir.is_dir():
            for file in sorted(default_dir.iterdir()):
                if file.suffix.lower() in ('.csv', '.txt'):
                    files_to_process.append(file)

    if not files_to_process:
        print("No files to process.")
        return

    emails = []
    for file in files_to_process:
        emails.extend(load_emails(str(file), args.column))

    if not emails:
        print("No emails found in specified files.")
        return

    results = []
    for email in emails:
        record = {
            'email': email,
            'syntax_valid': False,
            'mx_records': [],
            'smtp_valid': False,
            'error': None
        }
        if validate_syntax(email):
            record['syntax_valid'] = True
            domain = email.split('@', 1)[-1]
            mx_hosts = get_mx_records(domain)
            record['mx_records'] = mx_hosts
            smtp_result = smtp_check(email, mx_hosts, args.timeout)
            record['smtp_valid'] = smtp_result['smtp_valid']
            record['error'] = smtp_result.get('smtp_error')
        else:
            record['error'] = 'Invalid email syntax'
        results.append(record)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Validation complete. Results written to {args.output}")


if __name__ == '__main__':
    main()
