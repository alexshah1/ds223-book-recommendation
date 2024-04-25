import uvicorn
from kitab.api.app import app
from kitab.db import db_info

if __name__=="__main__": 
    uvicorn.run(app, port=5552)