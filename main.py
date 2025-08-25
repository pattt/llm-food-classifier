from fastapi import FastAPI, Request
from weather_time_agent.agent import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types
from dotenv import load_dotenv
import base64
import json

from google.cloud import pubsub_v1


load_dotenv()

app = FastAPI()

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name="weather_time_agent",
    session_service=session_service)

sessions = {}

@app.post("/start_session")
async def custom_webhook(request: Request):
    # Create a session
    session = await session_service.create_session(
        app_name="weather_time_agent",
        user_id="user_id")
    sessions["user_id"] = session
    return {"session_id": session.id}

@app.post("/custom_webhook")
async def custom_webhook(request: Request):
    body = await request.json()
    print("📥 Request body:", body)

    data = base64.b64decode(body["message"]["data"])
    print("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm " + str(data))
    message = json.loads(data)["msg"]
    chat_id = json.loads(data)["chat_id"]

    print("mmmmm11" + json.loads(data)["msg"])
    print("mmmmm22" + str(json.loads(data)["chat_id"]))

    session = sessions.get("user_id")

    if not session:
            session = await session_service.create_session(
                app_name="weather_time_agent",
                user_id="user_id")
            sessions["user_id"] = session

    print("📥 session.id:", session.id)

    print("message message message " + message)

    response = call_agent(message, session.id, "user_id")

    publish_response(response, chat_id)

    print("📤 ADK response:", response)
    return response

# Helper method to send query to the runner
def call_agent(query, session_id, user_id):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=user_id, session_id=session_id, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
            return final_response

def publish_response(response, chat_id):
    project_id = "llm-food-classifier-project"
    topic_id = "llm-weather-service-quene-resp"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    data_str = json.dumps({"msg": response, "chat_id": chat_id})
    data = data_str.encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(future.result())

# Локальный запуск
if __name__ == "__main__":
    import uvicorn

    print("start start start start !!!!!!!!!!!! \n")

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

    print("end end end end !!!!!!!!!!!! \n")
