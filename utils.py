import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def save_to_google_sheet(data, worksheet_name: str):
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        gcp_secrets = st.secrets["gcp_service_account"]
        credentials_dict = {
            "type": gcp_secrets["type"],
            "project_id": gcp_secrets["project_id"],
            "private_key_id": gcp_secrets["private_key_id"],
            "private_key": gcp_secrets["private_key"].replace("\\n", "\n"),
            "client_email": gcp_secrets["client_email"],
            "client_id": gcp_secrets["client_id"],
            "auth_uri": gcp_secrets["auth_uri"],
            "token_uri": gcp_secrets["token_uri"],
            "auth_provider_x509_cert_url": gcp_secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": gcp_secrets["client_x509_cert_url"],
            "universe_domain": gcp_secrets.get("universe_domain", "googleapis.com")
        }

        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)

        sheet_id = gcp_secrets["sheet_id"]
        spreadsheet = client.open_by_key(sheet_id)

        try:
            sheet = spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")

        # Convert list of dicts to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data

        if sheet.row_count == 0 or not sheet.get_all_values():
            sheet.append_row(df.columns.astype(str).tolist())

        rows = df.astype(str).fillna("").values.tolist()
        sheet.append_rows(rows)
        st.success(f"✅ Survey complete!")

    except Exception as e:
        st.error(f"❌ Failed to save to Google Sheets tab `{worksheet_name}`: {e}")

