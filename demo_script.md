# Demo Script — Verified local workflow

These steps were tested and work on a local development machine with Python installed.

1) Install dependencies

```powershell
pip install -r requirements.txt
```

2) Start the app

```powershell
& "C:/Program Files/Python313/python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

3) Create a user

```powershell
curl -X POST "http://127.0.0.1:8000/users/" -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass"}'
```

4) Obtain a token

```powershell
curl -X POST "http://127.0.0.1:8000/token" -d "username=test@example.com&password=testpass" -H "Content-Type: application/x-www-form-urlencoded"
```

5) Create a note (use the returned access token in `access_token` query param)

```powershell
curl -X POST "http://127.0.0.1:8000/user/notes?access_token=<ACCESS_TOKEN>" -H "Content-Type: application/json" -d '{"note": {"id":"n1","title":"note1","description":"hello"}}'
```

6) List notes

```powershell
curl "http://127.0.0.1:8000/user/notes?access_token=<ACCESS_TOKEN>"
```

Replace `<ACCESS_TOKEN>` with the token value returned from step 4.
