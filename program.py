import base64

# Your shared URL
shared_url = "https://vogelbldg-my.sharepoint.com/personal/cramquist_vogelbldg_com/Documents/lessons.xlsx"

# Encode the URL
encoded_url = base64.b64encode(shared_url.encode("utf-8")).decode("utf-8")
share_id = f"u!{encoded_url}"

print(share_id)


https://graph.microsoft.com/v1.0/shares/u!aHR0cHM6Ly92b2dlbGJsZGctbXkuc2hhcmVwb2ludC5jb20vcGVyc29uYWwvY3JhbXF1aXN0X3ZvZ2VsYmxkZ19jb20vRG9jdW1lbnRzL2xlc3NvbnMueGxzeA==/driveItem/content