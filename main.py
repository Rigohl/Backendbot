from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Backendbot API is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
