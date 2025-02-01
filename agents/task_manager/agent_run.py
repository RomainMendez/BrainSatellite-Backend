# Main program to execute the agent

from uvicorn import run
from fastapi import FastAPI

app = FastAPI()


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8080)