import os
import requests
import pandas as pd
import io
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from jwt import PyJWKClient
import json
import openai

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
        print("➡️ Starting token validation")
        print("🔑 Token snippet:", access_token[:30] + "...")

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)

        print("📬 Microsoft response code:", response.status_code)
        print("📬 Response text:", response.text)

        if response.status_code == 200:
            user_data = response.json()
            print("✅ Token is valid. User:", user_data["displayName"])
            return user_data
        else:
            print("🚨 Microsoft rejected the token.")
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



@app.route('/search-lessons', methods=['POST'])
def search_lessons():
    try:
        access_token = request.headers.get("Authorization")
        if not access_token:
            return jsonify({"error": "Missing access token in request"}), 401

        access_token = access_token.replace("Bearer ", "").strip()

        user_data = validate_token(access_token)
        if not user_data:
            return jsonify({"error": "Invalid or expired access token"}), 401

        query = request.get_json().get("query", "").strip().lower()
        if not query:
            return jsonify({"error": "Missing 'query' in request body"}), 400

        print(f"🔍 Searching for lessons matching: '{query}'")

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(SHAREPOINT_FILE_URL, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch file: {response.text}"}), response.status_code

        df = pd.read_excel(io.BytesIO(response.content), engine="openpyxl")
        df.columns = df.columns.str.strip()
        df_filtered = df[df["Approval"].astype(str).str.upper() == "TRUE"].fillna("")

        # Filter for rows that match the query in any column
        df_matched = df_filtered[
            df_filtered.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)
        ]

        print(f"✅ Found {len(df_matched)} matching lessons.")
        return jsonify({"results": df_matched.to_dict(orient="records")})

    except Exception as e:
        print(f"🚨 Search Error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500







# Set your OpenAI API key
import os
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route('/ask-assistant', methods=['POST'])
def ask_assistant():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        access_token = data.get("token", "").strip()

        if not message or not access_token:
            return jsonify({"error": "Missing message or token"}), 400

        # Validate token with Microsoft (optional but recommended)
        user = validate_token(access_token)
        if not user:
            return jsonify({"error": "Invalid Microsoft token"}), 401

        # === ASSISTANT WORKFLOW ===
        assistant_id = "asst_qIH7TNF3KcWFOOSiCQ146F1L"  # your Assistant ID

        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(thread_id=thread.id, role="user", content=message)
        run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

        # Wait for function call
        import time
        while run.status not in ["completed", "requires_action", "failed"]:
            time.sleep(1)
            run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action":
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            query = eval(tool_call.function.arguments)["query"]

            # Call internal search
            lessons_res = requests.post(
                "https://vogellessons-backend.onrender.com/search-lessons",
                json={"query": query},
                headers={"Authorization": f"Bearer {access_token}"}
            )
            lessons = lessons_res.json().get("results", [])
            tool_output = {
                "matches_found": len(lessons) > 0,
                "matches": lessons
            }

            openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[{
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(tool_output)
                }]
            )

            # Wait again for final reply
            while run.status != "completed":
                time.sleep(1)
                run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # Get the assistant's reply
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for m in messages.data[::-1]:
            if m.role == "assistant":
                return jsonify({"reply": m.content[0].text.value})

        return jsonify({"error": "No assistant response found"}), 500

    except Exception as e:
        print("🚨 Assistant error:", str(e))
        return jsonify({"error": str(e)}), 500







# ✅ Start the app only if run directly (Render handles this automatically)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)