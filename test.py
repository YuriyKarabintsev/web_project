from requests import get, post, delete

print(get("http://127.0.0.1:5000/api/users/19").json())