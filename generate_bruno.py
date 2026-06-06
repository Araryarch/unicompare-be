import os
import json

base_dir = "bruno_collection"
os.makedirs(base_dir, exist_ok=True)

with open(f"{base_dir}/bruno.json", "w") as f:
    json.dump({"version": "1", "name": "Unicompare API", "type": "collection"}, f, indent=2)

os.makedirs(f"{base_dir}/environments", exist_ok=True)
with open(f"{base_dir}/environments/Local.bru", "w") as f:
    f.write('''vars {
  base_url: http://localhost:8000/api
  token: 
}
''')

def create_request(folder, name, method, url, body_type="none", body_content="", auth=False):
    os.makedirs(f"{base_dir}/{folder}", exist_ok=True)
    bru = f"""meta {{
  name: {name}
  type: http
  seq: 1
}}

{method.lower()} {{
  url: {{{{base_url}}}}{url}
  body: {body_type}
  auth: {'bearer' if auth else 'none'}
}}

"""
    if auth:
        bru += """auth:bearer {
  token: {{token}}
}

"""
    if body_type == "json":
        bru += f"""body:json {{
{body_content}
}}
"""
    with open(f"{base_dir}/{folder}/{name}.bru", "w") as f:
        f.write(bru)

create_request("Auth", "Login", "POST", "/auth/login", "json", '  {\n    "username": "admin",\n    "password": "admin"\n  }')
create_request("Auth", "Register", "POST", "/auth/register", "json", '  {\n    "username": "newuser",\n    "password": "password123"\n  }')
create_request("Auth", "Me", "GET", "/auth/me", auth=True)

create_request("Public", "List Universities", "GET", "/universities")
create_request("Public", "Search Universities", "GET", "/universities/search?q=ui")
create_request("Public", "Compare", "GET", "/compare?score=700")

create_request("Admin", "List Users", "GET", "/admin/users", auth=True)
create_request("Admin", "Create University", "POST", "/admin/universities", "json", '  {\n    "id": "test_uni",\n    "name": "Test University",\n    "sources": ["internal_mock"]\n  }', auth=True)
create_request("Admin", "Update University", "PUT", "/admin/universities/test_uni", "json", '  {\n    "name": "Updated Test University"\n  }', auth=True)
create_request("Admin", "Delete University", "DELETE", "/admin/universities/test_uni", auth=True)

print("Bruno collection generated successfully in 'bruno_collection' directory.")
