Run locally:
```aiignore
adk api_server
```
or
```aiignore
adk web
```



Задеплоить [agent.py](weather_time_agent/agent.py) как агента:
```
export GOOGLE_CLOUD_PROJECT=llm-food-classifier-project
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=True
export SERVICE_NAME="test-agent-service1"
```


```
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
--service_name=$SERVICE_NAME \
--with_ui \
./multi_tool_agent
```


Open in browser 
```
https://test-agent-service1-97930199870.us-central1.run.app/
```
Request API:
```aiignore
export APP_URL="https://test-agent-service1-97930199870.us-central1.run.app"

export TOKEN=$(gcloud auth print-identity-token)



curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps



curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/apps/multi_tool_agent/users/user_123/sessions/session_abc \
    -H "Content-Type: application/json" \
    -d '{"state": {"preferred_language": "English", "visit_count": 5}}'




curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "multi_tool_agent",
    "user_id": "user_123",
    "session_id": "session_abc",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": "What is the weather?"
        }]
    },
    "streaming": false
    }'
```


Запустить как Python скрипт:
```aiignore
export GOOGLE_API_KEY=AIzaSyBN1q5M4n_fYqmEYs8iat3i_j_dluNllTg 
export GOOGLE_GENAI_USE_VERTEXAI=FALSE  
python3 main.py 
```

```aiignore
curl -X POST http://localhost:8080/custom_webhook  -H "Content-Type: application/json" -d '{"message": "Hello from PubSub!"}' 
```

Docker:
```aiignore
docker build . -t llm_weather
docker run -p 8080:8080 llm_weather 
```



export GOOGLE_CLOUD_PROJECT=llm-food-classifier-project
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_GENAI_USE_VERTEXAI=True
export SERVICE_NAME="test-agent-service1"

[Deploy to Cloud Run:](https://google.github.io/adk-docs/deploy/cloud-run)
```aiignore
gcloud run deploy llm-weather-service \
--source . \
--region $GOOGLE_CLOUD_LOCATION \
--project $GOOGLE_CLOUD_PROJECT \
--allow-unauthenticated \
--set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
# Add any other necessary environment variables your agent might need
```