"""RAG routes â€” index dataset, query with context."""
import sys, pathlib
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.deps import get_current_user, get_api_key
from app.services.data_store import get as get_df

router = APIRouter(prefix="/rag", tags=["RAG"])

def _boot():
    p = str(pathlib.Path(__file__).resolve().parents[3] / "services")
    if p not in sys.path: sys.path.insert(0, p)

class RAGQuery(BaseModel):
    question: str

@router.post("/index")
def index(user: dict = Depends(get_current_user)):
    _boot()
    from agents.rag.rag_agent import index_dataframe
    df = get_df(user["sub"])
    if df is None: raise HTTPException(404, "No dataset found")
    count = index_dataframe(user["sub"], df)
    return {"message": f"Indexed {count} chunks"}

@router.post("/query")
def query(req: RAGQuery, api_key: str = Depends(get_api_key),
          user: dict = Depends(get_current_user)):
    _boot()
    from agents.rag.rag_agent import query as rag_query
    answer = rag_query(user["sub"], req.question, api_key)
    return {"answer": answer, "type": "text"}
