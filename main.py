import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from dash_app import app as vars
from edit_record_app import app as edit_record
from edit_group_app import app as edit_group


# Define the FastAPI server
app = FastAPI()
# Mount the Dash app as a sub-application in the FastAPI server
app.mount("/vars", WSGIMiddleware(vars.server))
app.mount("/edit_record", WSGIMiddleware(edit_record.server))
app.mount("/edit_group", WSGIMiddleware(edit_group.server))

# Define the main API endpoint
@app.get("/")
def index():
    return "Hello"


# Start the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, port=8087, host="0.0.0.0")
