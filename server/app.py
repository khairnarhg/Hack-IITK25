import asyncio
import threading
from fastapi import FastAPI, Request
from kafka.admin import KafkaAdminClient
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers.ws_connections import router as ws_connections_router
from kafka_consumer import run_kafka_consumer
import os

app = FastAPI(title="Threat Detection Backend with Kafka")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="public", html=True), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    index_file = os.path.join("public", "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


app.include_router(ws_connections_router) 

@app.on_event("startup")
async def startup_event():
    print("Starting up FastAPI app and Kafka consumer...")
    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=run_kafka_consumer, args=(loop,), daemon=True)
    thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down FastAPI app...")
    admin_client = KafkaAdminClient(
        bootstrap_servers=["localhost:9092"],
        client_id="fastapi-shutdown"
    )
    try:
        admin_client.delete_topics(topics=["packets"])
        admin_client.close()
        print("Deleted 'packets' topic on shutdown.")
    except Exception as e:
        print(f"Error deleting 'packets' topic: {e}")

    json_path = os.path.join(os.path.dirname(__file__), "public", "data", "incoming_logs.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                f.write("[]")
            print("Cleared incoming_logs.json.")
        except Exception as e:
            print(f"Error clearing incoming_logs.json: {e}")
    else:
        print("No incoming_logs.json file found to clear.")
