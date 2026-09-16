from fastapi import FastAPI, Query
from .client.rq_client import queue
from .queues.worker import process_query

app = FastAPI()

@app.get("/")
def root():
    return {"status":"Server is up and running"}


@app.post("/chat")
def chat(query: str = Query(..., description="The chat query of user.")):
    job = queue.enqueue(process_query, query)

    return {"status": "Queued", "job_id": job.id}

@app.get("/job-status")
def get_result(job_id:str = Query(..., description="Job Id")):
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()

    return {"result": result}