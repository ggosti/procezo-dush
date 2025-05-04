import os
import json
import numpy as np
import pandas as pd

from dash import Dash, html, dcc, callback, Output, Input, State
import dash
import plotly.graph_objects as go
#from flask import g

import utils
import timeSeriesInsightToolkit as tsi
import dash_app

from models import Record

def getVars2(data):
    print(data)
    return (data)

def get_preprocessed_record_names(data):
    data = json.loads(data) 
    project_name = data["project_name"]
    group_name = data["group_name"]
    print('get_preprocessed_record_names',group_name)
    if isinstance(group_name, str):#project_name in allowedProjects: 
        records = projObj.get_recods_in_project_and_group(project_name,group_name,step='proc',version='preprocessed-VR-sessions')
        fileNames = [re.name for re in records]
        #fileNames, dfSs  = loadData(group_name,project_name,version='preprocessed-VR-sessions')
        return str(fileNames)
    else:
        return str(None)


def myScatterEmpty(xlab,ylab):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            #x = x,
            #y = y,
            xaxis = 'x',
            yaxis = 'y',
            mode = 'markers',
            #marker = dict(
            #    color = 'rgba(0,0,0,0.3)',
            #    size = 3
            #)
        ))
    fig.add_trace(go.Histogram(
            #y = y,
            xaxis = 'x2',
            marker = dict(
                color = 'rgba(0,0,0,1)'
            )
        ))
    fig.add_trace(go.Histogram(
            #x = x,
            yaxis = 'y2',
            marker = dict(
                color = 'rgba(0,0,0,1)'
            )
        ))
        
    fig.update_layout(
        autosize = False,
        xaxis = dict(
            zeroline = True,
            domain = [0,0.85],
            showgrid = True,
            title = xlab  # Add x-axis label
        ),
        yaxis = dict(
            zeroline = True,
            domain = [0,0.85],
            showgrid = False,
            title = ylab  # Add y-axis label
        ),
        xaxis2 = dict(
            zeroline = False,
            domain = [0.9,1],
            showgrid = False
        ),
        yaxis2 = dict(
            zeroline = False,
            domain = [0.9,1],
            showgrid = False
        ),
        height = 900,
        width = 900,
        bargap = 0,
        hovermode = 'closest',
    )
    return fig

def myScatter(x,y,xlab,ylab,names):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            x = x,
            y = y,
            xaxis = 'x',
            yaxis = 'y',
            mode = 'markers',
            #marker = dict(
            #    color = 'rgba(0,0,0,0.3)',
            #    size = 3
            #)
            hovertext = names
        ))
    fig.add_trace(go.Histogram(
            y = y,
            xaxis = 'x2',
            nbinsy=100 ,
            #marker = dict(
            #    color = 'rgba(0,0,0,1)'
            #)
        ))
    fig.add_trace(go.Histogram(
            x = x,
            yaxis = 'y2',
            nbinsx=100 ,
            #marker = dict(
            #    color = 'rgba(0,0,0,1)'
            #)
        ))
        
    fig.update_layout(
        autosize = False,
        xaxis = dict(
            zeroline = True,
            domain = [0,0.85],
            showgrid = True,
            title = xlab  # Add x-axis label
        ),
        yaxis = dict(
            zeroline = True,
            domain = [0,0.85],
            showgrid = True,
            title = ylab  # Add y-axis label
        ),
        xaxis2 = dict(
            zeroline = False,
            domain = [0.87,1],
            showgrid = False
        ),
        yaxis2 = dict(
            zeroline = False,
            domain = [0.87,1],
            showgrid = False
        ),
        height = 900,
        width = 900,
        bargap = 0,
        hovermode = 'closest',
    )
    return fig

def loadData(group_name,project_name,version):
    #pathSesRec = procProjectsPath + project_name+'/'+group_name+'/preprocessed-VR-sessions' # or pathSesRec = rawProjectsPath + project_name+'/'+group_name
    #ids, fileNames, dfSs, df = tsi.readData(pathSesRec)
    #print(dfSs)
    records = projObj.get_recods_in_project_and_group(project_name,group_name,step='proc',version=version)
    fileNames = [re.name for re in records]
    dfSs = [re.data for re in records]
    print('records in proj:',[re.name for re in records])
    return fileNames, dfSs 

def getPaths(dfSs,panoramic = False):
    if not panoramic:
        #paths=tsi.getPaths(ids,dfSs,['posx','posy','posz'])
        paths = [tsi.getPath(dfS,['posx','posy','posz']) for dfS in dfSs]
        #_,x,y,z = np.vstack(paths).T
    else:
        #paths = tsi.getPaths(ids,dfSs,['dirx','diry','dirz'])
        paths = [tsi.getPath(dfS,['dirx','diry','dirz']) for dfS in dfSs]
        #_,u,v,w = np.vstack(paths).T
    #paths = ma.getVarsFromSession(pathSes,['pos'])[0]
    #ids, fileNames, [paths,dpaths] = ma.getVarsFromSession(pathSes,['pos','dir'])
    #if panoramic: paths=dpaths
    return paths

def getDurationAndVariability(paths):
    #thTime = 35
    #thVar = 0.1#1.#0.1#1.#0.4 #2.5

    totTimes = []
    totVars = []
    for path in paths:
        t,x,y,z = path.T
        totTime = t[-1]-t[0]
        totTimes.append(totTime)
        totVar = np.var(x)+np.var(y)+np.var(z)
        totVars.append(totVar)
    return totTimes,totVars

def update_graph(data,value,x_filter = [0., 360.], y_filter = [0., 2.]):
    data = json.loads(data) 
    project_name = data["project_name"]
    group_name = data["group_name"]
    #print('x_filter',x_filter)
    print('update_graph',group_name)
    panoramic = False
    if "Panoramic" in value:
        panoramic = True
    if isinstance(group_name, str):#project_name in allowedProjects: 
        procGroup = projObj.get_group(project_name,group_name,'proc',version='preprocessed-VR-sessions')
        dfSs = [re.data for re in procGroup.records]
        fileNames = [re.name for re in procGroup.records]
        #fileNames, dfSs = loadData(group_name,project_name,version='preprocessed-VR-sessions')
        #dff = df[df.country == value]
        paths = getPaths(dfSs,panoramic=panoramic)
        totTimes,totVars = getDurationAndVariability(paths)
        dfScalar = pd.DataFrame({'variance':totVars,'session time (s)':totTimes,'fileNames':fileNames} )
        x = dfScalar['session time (s)']
        y = dfScalar['variance']
        names = dfScalar['fileNames']
        fig = myScatter(x,y,xlab = 'session time (s)' ,ylab = 'variance ($m^2$)',names = names)  #px.scatter(dfScalar,x='session time (s)', y='variance', marginal_x="histogram", marginal_y="histogram",hover_data=['fileNames'])
        fig.add_shape(type="rect",
            x0=x_filter[0], y0=y_filter[0], x1=x_filter[1], y1=y_filter[1],
            line=dict(
                color="RoyalBlue",
                width=2,
            ),
            fillcolor="LightSkyBlue",
            layer="below",
        )
        
        xmin = np.floor(x.min()) 
        xmax = np.ceil(x.max())
        ymin = np.floor(y.min()) 
        ymax = np.ceil(y.max())

        return fig, str(x_filter), xmin, xmax, {xmin: str(xmin), xmax: str(xmax)}, str(y_filter), ymin, ymax, {ymin: str(ymin), ymax: str(ymax)}
    else:
        fig = myScatterEmpty(xlab = 'session time (s)' ,ylab = 'variance')
        return fig, str(x_filter), 0.0, 360.0, {0: '0', 360.: '360'}, str(y_filter), 0.0, 2.0, {0: '0.0', 2.: '2.0'}

def get_saved_preprocessed_gated_record_names(data):
    data = json.loads(data) 
    project_name = data["project_name"]
    group_name = data["group_name"]
    print(group_name)
    if isinstance(group_name, str):#project_name in allowedProjects: 
        #fileNames, dfSs  = loadData(group_name,project_name,version='preprocessed-VR-sessions')
        records = projObj.get_recods_in_project_and_group(project_name,group_name,step='proc',version='preprocessed-VR-sessions-gated')
        fileNames = [re.name for re in records]
        
        return str(fileNames)
    else:
        return str(None)
    
def get_selected_preprocessed_gated_record_names(data,xRange,yRange):
    data = json.loads(data) 
    project_name = data["project_name"]
    group_name = data["group_name"]
    print(group_name)
    thTime0,thTime1 = json.loads(xRange)
    thVar0,thVar1 = json.loads(yRange)
    print('xRange',json.loads(xRange),thTime0,thTime1)
    print('yRange',yRange)
    if isinstance(group_name, str):#project_name in allowedProjects: 
        #fileNames, dfSs  = loadData(group_name,project_name,version='preprocessed-VR-sessions')
        records = projObj.get_recods_in_project_and_group(project_name,group_name,step='proc',version='preprocessed-VR-sessions')
        fileNames = [re.name for re in records]
        print('file names',fileNames)
        dfSs = [re.data for re in records]
        paths = getPaths(dfSs)
        totTimes,totVars = getDurationAndVariability(paths)
        ungatedFileNames = []

        for fName,totVar,totTime in zip(fileNames, totVars, totTimes):
            #print('fName',fName)
            if (totVar >= thVar0) and (totVar <= thVar1) and (totTime >= thTime0) and (totTime <= thTime1):
                ungatedFileNames.append(fName)
                print('session in ',fName)
                #assert session in d['preprocessedVRsessions'], "session not in preprocessedVRsessions "+session
                #d['preprocessedVRsessions-gated'][session] = d['preprocessedVRsessions'][session]
                #if 'ID' in dfS.columns: dfS = dfS.drop(columns=['ID', 'filename'])
                #dfS.to_csv(gatedPath+'/'+session+'-preprocessed.csv',index=False,na_rep='NA')
            else:
                print('session out',fName)
                #tsi.drawPath(path, dpath=None, BBox=None)
        return json.dumps(ungatedFileNames)
    else:
        return json.dumps([])
    
def save_selected_records(data, selected_rec_names,xRange,yRange, n_clicks):
    #print('n_clicks',n_clicks )
    #print('data',data )
    #print('selected_rec_names',selected_rec_names )
    selectedNames = json.loads(selected_rec_names)
    #print('selected_rec_names',selectedNames )
    thTime0,thTime1 = json.loads(xRange)
    thVar0,thVar1 = json.loads(yRange)

    if n_clicks>0:
        print("Save ",data)
        dff = json.loads(data) #= pd.read_json(data)
        project_name = dff['project_name']
        group_name = dff['group_name']
        pregatedGroup = projObj.get_group(project_name,group_name,'proc',version='preprocessed-VR-sessions')
        gatedGroup = projObj.get_group(project_name,group_name,'proc',version='preprocessed-VR-sessions-gated')
        gatedPath = pregatedGroup.path + '/preprocessed-VR-sessions-gated'
        print('gatedGroup.records',gatedGroup.records)
        for record in gatedGroup.records:
            os.remove(record.path)
            record_name = record.name
            print('record_name to remove',record_name)
            projObj.remove_record(record)#,project_name,group_name,version='preprocessed-VR-sessions-gated')


        d = {}
        if pregatedGroup.parsFileExists():
            d = pregatedGroup.loadPars()
        #print('ungatedGroup pars',ungatedGroup.path,ungatedGroup.pars_path) 
        #print('ungatedGroup pars',ungatedGroup.pars) 
        #print(d['preprocessedVRsessions'])
        d['gated'] = {'thVar >=':thVar0,'thVar <=':thVar1,'thTime >=':thTime0,'thTime <=':thTime1}
        d['preprocessedVRsessions-gated'] = {}
        #print('d',d)

        for fName in selectedNames:
            print('fName',fName)
            record =projObj.get_record(project_name,group_name,fName,'proc',version='preprocessed-VR-sessions')
            #pathSes = record.group.path
            record_path = os.path.join(gatedPath,fName+'.csv')
            print('record',record.name)#,pathSes)

            # i = len(utils.records) + 1
            # ungatedRecord = Record(i, fName, record_path, 'proc', record.data) 
            # ungatedRecord.set_ver('preprocessed-VR-sessions-gated')
            # ungatedRecord.group = ungatedGroup
            # ungatedRecord.project = ungatedGroup.project
            # ungatedGroup.add_record(ungatedRecord)
            # ungatedRecord.parent_record = record
            # record.add_child_record(ungatedRecord)
            # utils.records.append(ungatedRecord)
            ungatedRecord = projObj.add_record(record,gatedGroup,fName,record_path, record.data, version='preprocessed-VR-sessions-gated')
            d['preprocessedVRsessions-gated'][fName] = d['preprocessedVRsessions'][fName]

            ungatedRecord.data.to_csv(record_path,index=False,na_rep='NA')

        tsi.writeJson(pregatedGroup.pars_path,d)

def setPanoramiCheckValuse(data):
    dff = json.loads(data) #= pd.read_json(data)
    project_name = dff['project_name']
    group_name = dff['group_name']
    value=[]
    #rawGroup = projObj.get_group(project_name,group_name,'raw')
    pregatedGroup = projObj.get_group(project_name,group_name,'proc',version='preprocessed-VR-sessions')
    if pregatedGroup.parsFileExists():
        d = pregatedGroup.loadPars()
        if 'panoramic' in d:
            value = ["Panoramic"]
    return value


def getPanoramiCheckValuse(data,value):
    dff = json.loads(data) #= pd.read_json(data)
    project_name = dff['project_name']
    group_name = dff['group_name']
    #rawGroup = projObjInt.get_group(project_name,group_name,'raw')
    pregatedGroup = projObj.get_group(project_name,group_name,'proc',version='preprocessed-VR-sessions')
    if pregatedGroup.parsFileExists():
        d = pregatedGroup.loadPars()
        if 'panoramic' in d:
            value = ["Panoramic"]
    #print(value)
    if "Panoramic" in value:
        #print("Panoramic")
        #rawGroup.set_panoramic(True)
        pregatedGroup.set_panoramic(True)

def init_callbacks(app):

    dash_app.init_callback_vars(app)

    app.callback(
        Output("group-vars","children"),
        Input("variables", "data"),
    )(getVars2)
    app.callback(
        Output("preprocessed-record-names", "children"),
        Input("variables", "data"),
    )(get_preprocessed_record_names)
    app.callback(
        Output("panoramic-checklist","value"),
        Input("variables", "data"),
    )(setPanoramiCheckValuse)
    app.callback(
        State("variables", "data"),
        Input("panoramic-checklist","value"),
    )(getPanoramiCheckValuse)
    app.callback(
        Output("scatter-plot", "figure"), 
        Output("x-slider-output", "children"), 
        Output("x-slider-2", "min"),
        Output("x-slider-2", "max"), 
        Output("x-slider-2", "marks"), 
        Output("y-slider-output", "children"), 
        Output("y-slider", "min"),
        Output("y-slider", "max"), 
        Output("y-slider", "marks"),
        Input("variables", "data"),
        Input("panoramic-checklist","value"),
        Input("x-slider-2", "value"),
        Input("y-slider", "value"),
    )(update_graph)
    app.callback(
        Output("preprocessed-gated-record-names", "children"),
        Input("variables", "data"),
    )(get_saved_preprocessed_gated_record_names)
    app.callback(
        Output("preprocessed-gated-selected-record-names", "children"),
        State("variables", "data"),
        Input("x-slider-output", "children"),
        Input("y-slider-output", "children"),
    )(get_selected_preprocessed_gated_record_names)
    app.callback(
        #Output('container-button-basic', 'children'),
        State('variables', 'data'),
        State("preprocessed-gated-selected-record-names", "children"),
        State("x-slider-output", "children"),
        State("y-slider-output", "children"),
        Input('save-gate', 'n_clicks'),
        prevent_initial_call=True
    )(save_selected_records)

def load_data_projObj():
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

    return projObj

projObj = load_data_projObj()

app = dash.Dash(__name__, requests_pathname_prefix='/edit_group/')#,  external_stylesheets=[dbc.themes.BOOTSTRAP]  )


project_name = '<None>'
group_name = '<None>'
record_name = '<None>'


layout1 = html.Div(
        [
            html.H1(children="Group Proc.", style={"textAlign": "center"}),
            html.P(children="Gate records in a group from immersive and not-immersive explorations of Aton 3D " 
                              + "models which were captured with Merkhet. "
                              + "Records in a group are gated according to time duration and variance."),
            html.P(id='group-vars'), #dcc.Store(id='variables')
            dcc.Checklist(["Panoramic"], [], id="panoramic-checklist", inline=True),
            html.P(children= "Preprocessed records pre-gate:"),
            html.P(id="preprocessed-record-names", children= "< None >"),
            dcc.Graph(id="scatter-plot"),
            html.P(children="Gate range x-axis"),
            html.P(id="x-slider-output",children=str([0., 360.])),
            dcc.RangeSlider(
                    id='x-slider-2',
                    min=0, max=360., #step=1.,
                    marks={0: '0', 360.: '360'},
                    value=[0., 360.]
                    ),
            html.P(children="Gate range y-axis"),
            html.P(id="y-slider-output",children=str([0., 2.])),
            dcc.RangeSlider(
                    id='y-slider',
                    min=0, max=2., #step=0.01,
                    marks={0: '0', 2.: '2.'},
                    value=[0., 2.]
                    ),
            html.P(children= "Saved preprocessed records post-gate:"),
            html.P(id="preprocessed-gated-record-names", children= "< None >"),
            html.P(children= "Selected preprocessed records post-gate:"),
            html.P(id="preprocessed-gated-selected-record-names", children= "< None >"),
            html.Button('Save selected records', id='save-gate', n_clicks=0),
            dcc.Store(id='group-variables'),
        ])

app.layout =  html.Div([
        # represents the browser address bar and doesn't render anything
        dcc.Location(id='url', refresh=False),
        html.A(id="logout-link", children="Main page", href="/"),
        html.Div(id='project-name', children = f"Project: {project_name}"),
        #html.P(children="Project:"),
        #dcc.Input(id="project-input1", type="text", placeholder=project_name),
        html.Div(id='group-name', children = f"Group: {group_name}"),
        html.Div(id='record-name', children = f"Record: {record_name}"),
        layout1, #html.Div(id='page-content'),
        dcc.Store(id='variables'),
])

init_callbacks(app)
#return app.server



if __name__ == "__main__":
    app.run(debug=True)