import json
import os
import pygsheets
import tempfile

from performance.env import check_get_env
from performance import prod_config as config


def get_pygsheets_client():
    google_auth_private_key_id = os.getenv('GOOGLE_AUTH_PRIVATE_KEY_ID')
    if not google_auth_private_key_id:
        return pygsheets.authorize(service_file=config.GSHEETS_CREDENTIALS_FILE)

    creds = {
        "type": "service_account",
        "project_id": "verify-performance",
        "private_key_id": google_auth_private_key_id,
        # Private key cannot be set in `.env` at the moment and must therefore be defined in the
        # shell when running locally.
        "private_key": check_get_env('GOOGLE_AUTH_PRIVATE_KEY'),
        "client_email": check_get_env('GOOGLE_AUTH_CLIENT_EMAIL'),
        "client_id": check_get_env('GOOGLE_AUTH_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": check_get_env('GOOGLE_AUTH_CLIENT_CERT_URL')
    }
    temp = tempfile.NamedTemporaryFile(delete=False, mode="w+t")
    temp.write(json.dumps(creds))
    temp.close()
    try:
        return pygsheets.authorize(service_file=temp.name)
    finally:
        os.unlink(temp.name)
