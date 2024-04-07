import uvicorn
from .kitab.api.app import app

if __name__=="__main__":
    uvicorn.run(app)