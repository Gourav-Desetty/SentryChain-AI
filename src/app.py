from src.SentryChain.backend import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.SentryChain.backend.app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )