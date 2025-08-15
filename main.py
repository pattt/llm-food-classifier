from fastapi import FastAPI, Request
from weather_time_agent.agent import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types
from dotenv import load_dotenv

from contextlib import asynccontextmanager

import threading
import asyncio



from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1

# TODO(developer)
project_id = "llm-food-classifier-project"
subscription_id = "llm-weather-service-quene-subscription"
# Number of seconds the subscriber should listen for messages
timeout = 25.0

def subscribe_messages():

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.")
        message.ack()


    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    #with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        print(f"subscriber!!!! \n")
        streaming_pull_future.result() #timeout=timeout
        print(f"streaming_pull_future.result(timeout=timeout)!!!!! \n")
    except TimeoutError:
        print(f"TimeoutError!!!! \n")
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.
    finally:
        print(f"finally!!!!! \n")
        streaming_pull_future.cancel()




async def subscribe_messages_async():
    print(f"subscribe_messages_async !!!!!!!!!!!! \n", flush=True)
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.", flush=True)
        message.ack()

    print(f"streaming_pull_future 1 !!!!!!!!!!!! \n", flush=True)
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"streaming_pull_future 2 !!!!!!!!!!!! \n", flush=True)

    try:
        print(f"streaming_pull_future.result 1 !!!!!!!!!!!! \n", flush=True)
        await asyncio.to_thread(streaming_pull_future.result, timeout=timeout)
        print(f"streaming_pull_future.result 2 !!!!!!!!!!!! \n", flush=True)
    except TimeoutError:
        print(f"TimeoutError 1 !!!!!!!!!!!! \n", flush=True)
        streaming_pull_future.cancel()
        await asyncio.to_thread(streaming_pull_future.result)
        print(f"TimeoutError 2 !!!!!!!!!!!! \n", flush=True)
    finally:
        print(f"finally 1 !!!!!!!!!!!! \n", flush=True)
        streaming_pull_future.cancel()
        print(f"finally 2 !!!!!!!!!!!! \n", flush=True)



load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"lifespan lifespan lifespan !!!!!!!!!!!! \n", flush=True)
    asyncio.create_task(subscribe_messages_async())
    yield

#agent = Agent(name="manual-agent")
app = FastAPI(lifespan=lifespan)

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

    session = sessions.get("user_id")

    if not session:
            session = await session_service.create_session(
                app_name="weather_time_agent",
                user_id="user_id")
            sessions["user_id"] = session

    print("📥 session.id:", session.id)

    response = call_agent(body["message"], session.id, "user_id")

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

# Локальный запуск
if __name__ == "__main__":
    import uvicorn

    print("start start start start !!!!!!!!!!!! \n")

    #subscribe_messages()

    #subscriber_thread = threading.Thread(target=subscribe_messages, daemon=False)
    #subscriber_thread.start()

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

    print("end end end end !!!!!!!!!!!! \n")
    #subscribe_messages()
