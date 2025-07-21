from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/rag")
async def rag_query(request: QueryRequest):
    response = app.state.rag_chain.invoke(request.query)
    return {"query": request.query, "answer": response}

def run_api(rag_chain, vector_store, host="0.0.0.0", port=8000):
    app.state.rag_chain = rag_chain
    # app.state.vector_store = vector_store
    print(f"Total data points: {vector_store.get()['ids'].__len__()}")
    import uvicorn
    uvicorn.run(app, host=host, port=port)