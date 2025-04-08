import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

import utils

from dash_app import app as vars
from edit_record_app import app as edit_record
from edit_group_app import app as edit_group


with open('config.json') as f:
    d = json.load(f)

rawProjectsPath = d['rawProjectsPath']
procProjectsPath = d['procProjectsPath']
allowedProjects = d['allowedProjects']

def load_data_projObj():
    steps = ['raw','proc']#'raw',
    stepsPaths = {'raw':rawProjectsPath,'proc':procProjectsPath}#{'raw':rawProjectsPath,'proc':procProjectsPath}

    projObj = utils.loadProjects(steps,stepsPaths)

    # print('projects')
    # for p in projObj.projects:
    #     print(p.id, p.name,p.path,p.step)
    
    # print('groups')
    # for g in projObj.groups:
    #     print(g.id, g.name,g.version,g.name,g.project.name,g.step)     

    # print('records')
    # for r in projObj.records:
    #     print(r.id, r.name,r.version,r.group.name,r.group.id,r.project.name,r.step)  

    return projObj

projObj = load_data_projObj()

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

@app.get('/<project_name>')
def get_project(project_name):
    """Get all groups in a project"""
    print("project_name",project_name)#,allowedProjects)
    if project_name in allowedProjects:
        rawProjectGroups = projObj.get_groups_in_project(project_name,'raw')
        return {'groups':rawProjectGroups}
    else:
        return {'error':'Project not allowed'}


# Start the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, port=8087, host="0.0.0.0")
