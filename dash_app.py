import dash
#import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Output, Input, State
from utils import ProjectsClass
import utils
from dash_apps import records_proc, group_proc

import json


def update_variable(pathname):
    project_name = '<None>'
    group_name = '<None>'
    record_name = '<None>'
    nameList = pathname.split('/')
    length = len(nameList)
    print('nameList update vars',nameList,length)
    if length > 1:
        existing_project_names = [pr.name for pr in projObj.projects]
        print('existing_project_names',existing_project_names)
        project_name = '<None>' 
        if nameList[1] in existing_project_names: #len(project_name) == 0:
            project_name = nameList[1]
        print('project_name',project_name,len(project_name))
    if length > 2:
        existing_group_names = [gr.name for gr in projObj.get_groups_in_project(project_name,'raw') ]
        group_name = '<None>' 
        if nameList[2] in existing_group_names:
            group_name = nameList[2]
    if length > 3: 
        existing_records_names = [re.name for re in projObj.get_recods_in_project_and_group(project_name,group_name,'raw') ]
        print('record_name',record_name, nameList[3],existing_records_names)
        if not nameList[3] == 'group_proc':
            record_name = '<None>' 
            if nameList[3] in existing_records_names:
                record_name = nameList[3]
        print(record_name)
    return f"Project: {project_name}",f"Group: {group_name}",f"Record: {record_name}"

def update_group_variables(pathname):
    print("update_record_variables",pathname)
    nameList = pathname.split('/')
    length = len(nameList)
    print('nameList',nameList,length)
    d = {'project_name': None, 'group_name': None, 'record_name': None}
    if length > 2:
        project_name = nameList[2]
        print('project_name',project_name,len(project_name))
        if len(project_name) == 0:
            project_name = None
        d['project_name'] = project_name
    if length > 3:
        group_name = nameList[3]
        d['group_name'] = group_name
    if length > 4: 
        record_name = nameList[4]
        if not record_name == 'group_proc':
            d['record_name'] = record_name
        else:
            del d['record_name']
    jsonD = json.dumps(d)
    #print(empty_json)
    return jsonD #pd.DataFrame().to_json()



def display_page(pathname):
    print("display_page",pathname)
    nameList = pathname.split('/')
    length = len(nameList)
    print('nameList',nameList,length,nameList[-1])
    if length == 6  and nameList[-1] == 'record_proc':
        return records_proc.layout1   
    elif length == 5 and nameList[-1] == 'group_proc':
        return group_proc.layout1
    if nameList[-1] == '' or length < 6:
        return None
    else:
        return '404'
    #elif pathname == '/page2':
    #    return layout2
    #else:
    #    return '404'


    
def init_callbacks(app):
    app.callback(
        Output("project-name", "children"),
        Output("group-name", "children"),
        Output("record-name", "children"),
        Input('url', 'pathname'),
    )(update_variable)
    app.callback(
        Output("variables", "data"),  
        Input('url', 'pathname'),
    )(update_group_variables)
    app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )(display_page)

#import ssl
#from flask import g
#import json

#ssl._create_default_https_context = ssl._create_unverified_context


# If initializing Dash app using Flask app as host
#app = Dash(server=g.cur_app, url_base_pathname=url_path)
app = dash.Dash(__name__)#,  external_stylesheets=[dbc.themes.BOOTSTRAP]  )

with open('config.json') as f:
    d = json.load(f)

rawProjectsPath = d['rawProjectsPath']
procProjectsPath = d['procProjectsPath']
allowedProjects = d['allowedProjects']

steps = ['raw','proc']#'raw',
stepsPaths = {'raw':rawProjectsPath,'proc':procProjectsPath}#{'raw':rawProjectsPath,'proc':procProjectsPath}

projObj = utils.loadProjects(steps,stepsPaths)

print('projects')
for p in projObj.projects:
    print(p.id, p.name,p.path,p.step)
 
print('groups')
for g in projObj.groups:
    print(g.id, g.name,g.version,g.name,g.project.name,g.step)     

print('records')
for r in projObj.records:
    print(r.id, r.name,r.version,r.group.name,r.group.id,r.project.name,r.step)   

# End if

# If initializing Dash app for middleware
#app = Dash(requests_pathname_prefix=url_path)

# End if

project_name = '<None>'
group_name = '<None>'
record_name = '<None>'

app.layout =  html.Div([
        # represents the browser address bar and doesn't render anything
        dcc.Location(id='url', refresh=False),
        html.A(id="logout-link", children="Main page", href="/"),
        html.Div(id='project-name', children = f"Project: {project_name}"),
        #html.P(children="Project:"),
        #dcc.Input(id="project-input1", type="text", placeholder=project_name),
        html.Div(id='group-name', children = f"Group: {group_name}"),
        html.Div(id='record-name', children = f"Record: {record_name}"),
        html.Div(id='page-content'),
        dcc.Store(id='variables'),
])

#group_proc.init_app_group_proc()
#records_proc.init_app_records_proc()
init_callbacks(app)
#return app.server


    
    #records_proc.init_callbacks_records_proc(app)
    #group_proc.init_callbacks_group_proc(app)

    #By default, Dash applies validation to your callbacks, which performs checks such as validating the types of callback arguments and checking to see whether the specified Input and Output components actually have the specified properties.
    #app.config.suppress_callback_exceptions = True


if __name__ == "__main__":
    app.run(debug=True)