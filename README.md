# Demo Server 
A server receiving post requests to  
1. Send GET requests to the source url to retrieve the byte data 
2. Process the byte data by manipulating with historical information
3. Send POST requests to the reporting url regarding the processed information

## Usage
Send POST requests(Scheduler) to the `/report` endpoint with the following request body:

```json
{
  "source": "string",
  "source_url": "string",
  "threshold": 0,
  "reporting_url": "string"
}
```
## Technology
1. FastAPI
2. Redis
3. Firestore

## System Diagram

![image](https://github.com/thomas-chiang/fastapi_service/assets/84237929/f30d0ffe-1465-49d6-9398-f1023f5c0df7)


## Getting Started

Build the Docker image:  
```
docker-compose build
```

To run the docker-compose environment: 
```
docker-compose up
```

To run unit test: 
```
docker-compose run --rm app py.test app/tests --cov=app
```
