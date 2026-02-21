from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import threading
import time
import requests

app = FastAPI()

@app.get("/static/{filename}")
async def get_static_file(filename: str):
    with open(filename, "w") as f:
        f.write("<html><body>test</body></html>")
    return FileResponse(filename, media_type="text/html")

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(2)

response = requests.get("http://127.0.0.1:8001/static/test_file.html")
print(response.headers)
print(response.content)
