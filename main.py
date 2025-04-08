import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

import json

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
async def index():
    return "Hello"

# define the API endpoint to get all projects
@app.get('/projects') 
async def get_projects() -> dict[str, list[str]]: #dict[str, list[str]]:
    """Get all projects"""
    rawProjects = projObj.projects
    rawProjectsNames = [p.name for p in rawProjects if p.step == 'raw'] 
    #print("rawProjects",[{'name':p.name,'step':p.step} for p in rawProjects])
    return {'projects':rawProjectsNames}

# Define the API endpoint to get all groups in project
@app.get('/groups/{project_name}')
async def get_project(project_name:str) -> dict[str, list[str]] | dict[str, str]:
    """Get all groups in a project"""
    #print("project_name",project_name)#,allowedProjects)
    if project_name in allowedProjects:
        rawProjectGroups = projObj.get_groups_in_project(project_name,'raw')
        return {'groups':[g.name for g in rawProjectGroups]}
    else:
        return {'error':'Project not allowed'}
    
# Define the API endpoint to get all records in group
@app.get('/records/{project_name}/{group_name}')
async def get_group(project_name:str, group_name:str) -> dict[str, list[str]] | dict[str, str]:
    """Get all records in a group"""
    #print("group_name",group_name)
    if project_name in allowedProjects:
        rawGroupRecords = projObj.get_recods_in_project_and_group(project_name,group_name,'raw',version=None) # get_records_in_group(project_name,group_name,'raw')
        return {'records':[r.name for r in rawGroupRecords]}
    else:
        return {'error':'Project not allowed'}


# Start the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, port=8087, host="0.0.0.0",)
