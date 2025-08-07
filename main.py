from fastapi import FastAPI, Request
from weather_time_agent.agent import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types

#agent = Agent(name="manual-agent")
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
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
