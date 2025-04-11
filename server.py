import os
import requests
import pandas as pd
import io
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from jwt import PyJWKClient

app = Flask(__name__)

# ✅ Enable CORS for frontend
CORS(app, resources={r"/*": {
    "origins": "https://vogellessons.com",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Authorization", "Content-Type"]
}})

# ✅ Microsoft Graph API URL for the Excel file
SHAREPOINT_FILE_URL = "https://graph.microsoft.com/v1.0/shares/u!aHR0cHM6Ly92b2dlbGJsZGctbXkuc2hhcmVwb2ludC5jb20vcGVyc29uYWwvY3JhbXF1aXN0X3ZvZ2VsYmxkZ19jb20vRG9jdW1lbnRzL2xlc3NvbnMueGxzeA==/driveItem/content"

# ✅ Microsoft token validation URL (JWKS)
JWKS_URL = "https://login.microsoftonline.com/common/discovery/keys"
EXPECTED_AUDIENCE = "00000003-0000-0000-c000-000000000000"  # Graph API audience

# ✅ Validate token using Microsoft Graph
def validate_token(access_token):
    try:
        print("🔹 Using Microsoft to validate token...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            print("✅ Token is valid. User:", user_data["displayName"])
            return user_data
        else:
            print("🚨 Microsoft rejected the token:", response.text)
            return None
    except Exception as e:
        print("🚨 Token validation failed:", str(e))
        return None

# ✅ Route to fetch the Excel file from SharePoint
@app.route('/fetch-excel', methods=['GET'])
def fetch_excel():
    try:
        access_token = request.headers.get("Authorization")
        if not access_token:
            return jsonify({"error": "Missing access token in request"}), 401

        access_token = access_token.replace("Bearer ", "").strip()

        user_data = validate_token(access_token)
        if not user_data:
            return jsonify({"error": "Invalid or expired access token"}), 401

        print(f"🔹 Token validated for user: {user_data['displayName']} - Fetching file...")

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(SHAREPOINT_FILE_URL, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch file: {response.text}"}), response.status_code

        df = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
        df.columns = df.columns.str.strip()
        df_filtered = df[df["Approval"].astype(str).str.upper() == "TRUE"]

        # selected_columns = [
        #     "Lesson Learned:",
        #     "Job Number",
        #     "Relevant Spec Section:",
        #     "Category",
        #     "Date:",
        #     "Name"
        # ]
        # df_filtered = df_filtered[selected_columns].fillna("")
        df_filtered = df_filtered.fillna("")

        json_data = df_filtered.to_dict(orient="records")

        print("✅ Sending clean JSON data to frontend.")
        return jsonify(json_data)

    except Exception as e:
        print(f"🚨 Server Error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/')
def home():
    return "Backend is running!"


# ✅ Start the app only if run directly (Render handles this automatically)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)