import pandas as pd
import os
import json

from models import Project, Group, Record


with open('config.json') as f:
    d = json.load(f)

rawProjectsPath = d['rawProjectsPath']
procProjectsPath = d['procProjectsPath']
allowedProjects = d['allowedProjects']

def get_records(path):
    """"
    Utility function for loading alist of records from a directory. It is assumed that the records are csv files.
    Only the files with the extension .csv are loaded.
    The function returns a list of tuples with the dataframe, the name of the record and the path to the record.
    The name of the record is the name of the file without the extension.
    The path to the record is the full path to the file.
    The function also sorts the records by name.

    >>> path = './test/records/raw/event1/group1/'
    >>> dfs = get_records(path)

    >>> [(df[0].shape, df[1], df[2]) for df in dfs] 
    [((100, 11), 'U1', './test/records/raw/event1/group1/U1.csv'), ((100, 11), 'U2', './test/records/raw/event1/group1/U2.csv'), ((100, 11), 'U3', './test/records/raw/event1/group1/U3.csv'), ((100, 11), 'U4', './test/records/raw/event1/group1/U4.csv')]


    """
    dfs = []
    record_names = os.listdir(path)
    record_names.sort()
    for record_name in record_names:
        record_path = os.path.join(path, record_name)
        if os.path.isfile(record_path) and record_path.endswith('.csv'):
            df = pd.read_csv(record_path, skipinitialspace=True)
            record_name = record_name.split('.')[0]
            dfs.append([df,record_name,record_path])
    return dfs


def load_data(project_dir,step,projects,groups,records):
    """
    Utility function for loading datastructure give the path of the directory with the projects.
    >>> projects = []
    >>> groups = []
    >>> records = []
    >>> projects, groups, records = load_data('./test/records/raw/', 'raw', projects, groups, records)
    >>> [(p.id, p.name) for p in projects]
    [(1, 'event1'), (2, 'event2')]
    >>> project = projects[0]
    >>> [(g.id, g.name) for g in project.groups]
    [(1, 'group1'), (2, 'group2')]
    >>> group = project.groups[0]
    >>> [(r.id, r.name, r.step,r.version) for r in group.records]
    [(1, 'U1', 'raw', None), (2, 'U2', 'raw', None), (3, 'U3', 'raw', None), (4, 'U4', 'raw', None)]

    >>> projects = []
    >>> groups = []
    >>> records = []
    >>> projects, groups, records = load_data("./test/records/proc/", 'proc', projects, groups, records)
    >>> [(p.id, p.name) for p in projects]
    [(1, 'event1'), (2, 'event2')]
    >>> project = projects[0]
    >>> [(g.id, g.name, g.project.name,g.step,g.version) for g in project.groups]
    [(1, 'group1', 'event1', 'proc', 'preprocessed-VR-sessions'), (2, 'group1', 'event1', 'proc', 'preprocessed-VR-sessions-gated'), (3, 'group2', 'event1', 'proc', 'preprocessed-VR-sessions'), (4, 'group2', 'event1', 'proc', 'preprocessed-VR-sessions-gated')]
    >>> group = project.groups[0]
    >>> [(r.id, r.name, r.step,r.version) for r in group.records]
    [(1, 'U1-preprocessed', 'proc', 'preprocessed-VR-sessions'), (2, 'U2-preprocessed', 'proc', 'preprocessed-VR-sessions')]
    

    """

    # Create proc projects dir for each raw project dir if it does not exist
    #print('Create proc projects dir for each raw project dir if it does not exist',project_dir, step)
    if step == 'raw':
        project_names = os.listdir(project_dir)
        project_names.sort()
        for project_name in project_names:
            #print('project_name',project_name)
            if project_name in allowedProjects:
                project_path = os.path.join(procProjectsPath, project_name)
                #print('project_path',project_path)
                if not os.path.exists(project_path):
                    #print('make project_path')
                    os.makedirs(project_path)

    # Create proc group dir for each raw goup dir if it does not exist
    if step == 'raw':
        project_names = os.listdir(project_dir)
        project_names.sort()
        for project_name in project_names:
            if project_name in allowedProjects:
                project_path = os.path.join(project_dir, project_name)
                if os.path.isdir(project_path):
                    group_names = os.listdir(project_path)
                    group_names.sort()
                    for group_name in group_names:
                        group_path = os.path.join(project_path, group_name)
                        #print('group_path',group_path)
                        if os.path.isdir(group_path):
                            if not os.path.exists(os.path.join(procProjectsPath, project_name, group_name)):
                                os.makedirs(os.path.join(procProjectsPath, project_name, group_name))
                            for ver in ['preprocessed-VR-sessions','preprocessed-VR-sessions-gated']:
                                if not os.path.exists(os.path.join(procProjectsPath, project_name, group_name, ver)):
                                    os.makedirs(os.path.join(procProjectsPath, project_name, group_name, ver))

    # Load projects
    projectsInner = []
    i = len(projects) +1
    project_names = os.listdir(project_dir)
    project_names.sort()
    for project_name in project_names:
        project_path = os.path.join(project_dir, project_name)
        #print('project_path',project_path)
        if os.path.isdir(project_path):
            project = Project(i, f"{project_name}",project_path,step)
            project.step = step
            #print(project.name,project.step)
            i = i + 1
            projectsInner.append(project)
    projects = projects + projectsInner
    #print('projectsInner', [(p.id, p.name, p.path) for p in projectsInner])
    

    # Load groups
    groupsInner = []
    i = len(groups) + 1
    if step == 'raw':
        for project in projectsInner:
            group_names = os.listdir(project.path)
            group_names.sort()
            for group_name in group_names:
                group_path = os.path.join(project.path, group_name)
                group_path = os.path.normpath(group_path)
                #print('group_path',group_path)
                #if os.path.isfile(group_path) and group_path.endswith('.csv'):
                if os.path.isdir(group_path):
                    group = Group(i, f"{group_name}",group_path,step)
                    group.project = project
                    i = i + 1
                    groupsInner.append(group)
                    project.add_group(group)
        #print('groupsInner', [(g.id, g.name, g.path) for g in groupsInner])

    if step == 'proc':
        for project in projectsInner:
            group_names = os.listdir(project.path)
            group_names.sort()
            for group_name in group_names:
                group_path = os.path.join(project.path, group_name)
                group_path = os.path.normpath(group_path)
                if os.path.isdir(group_path):
                    for ver in os.listdir(group_path):
                        ver_path = os.path.join(group_path, ver)
                        if os.path.isdir(ver_path):
                            group = Group(i, f"{group_name}", group_path, step)
                            group.set_ver(ver)
                            group.project = project
                            i = i + 1
                            groupsInner.append(group)
                            project.add_group(group)  
    groups = groups + groupsInner  

    # Load records
    recordsInner = []
    i = len(records) + 1
    if step == 'raw':
        for group in groups:
            dfs = get_records(group.path)
            for df,record_name,record_path in dfs:
                record = Record(i, record_name, record_path, 'raw', df)
                record.group = group
                record.project = group.project
                i = i + 1
                recordsInner.append(record)
                group.add_record(record)

    if step == 'proc':
        for group in groups:
            #for ver in os.listdir(group.path):
            ver = group.version
            #print(group.name,'ver',ver)
            if ver is not None:
                ver_path = os.path.join(group.path, ver)
                if os.path.isdir(ver_path):
                    dfs = get_records(ver_path)
                    for df,record_name,record_path in dfs:
                        record = Record(i, record_name, record_path, 'proc',df)
                        record.set_ver(ver)
                        record.group = group
                        record.project = group.project
                        i = i + 1
                        recordsInner.append(record)
                        group.add_record(record)
    records = records + recordsInner
    

    return projects,groups,records 

def link_projects(projects):
    """
    Link project to parent project and child projects

    Parameters:
    ----------

    projects : list of Project objects
        List of Project objects to link.
    
    Returns variables:
    -------

    projects : list of Project objects
        List of Project objects with linked parent and child projects.

    Example:
    ---------
    >>> projects = [Project(1, 'event1', './test/records/raw/event1', 'raw'), Project(2, 'event1', './test/records/proc/event1', 'proc')]

    >>> projects = link_projects(projects)
    >>> [(p.name, p.step, p.parent_project.name if p.parent_project else None) for p in projects]
    [('event1', 'raw', None), ('event1', 'proc', 'event1')]
    >>> projects[0].child_projects[0].name  # 'event1'
    'event1'
    >>> projects[1].parent_project.name  # 'event1'
    'event1'
    """
    # link project to parent project and child projects
    for p in projects:
        if p.step == 'raw':
            for p2 in projects:
                if (p2.step == 'proc') and (p2.name == p.name):
                    p2.parent_project = p
                    p.add_child_project(p2)
    return projects

def link_groups(groups):
    # link group to parent group and child groups
    for g in groups:
        if g.step == 'raw':
            #print('g',g.name,g.project.name,g.step)
            for g2 in groups:
                #print('g2',g2.name,g2.project.name,g2.step)
                if (g2.step == 'proc') and (g2.project.name == g.project.name) and (g2.name == g.name) and (g2.version == 'preprocessed-VR-sessions'):
                    g2.parent_group = g
                    g.add_child_group(g2)
        if g.step == 'proc' and g.version == 'preprocessed-VR-sessions':
            for g2 in groups:
                if (g2.step == 'proc') and (g2.project.name == g.project.name) and (g2.name == g.name) and (g2.version == 'preprocessed-VR-sessions-gated'):
                    g2.parent_group = g
                    g.add_child_group(g2)
    return groups

def link_records(records):
    # link records to parent record and child records
    for r in records:
        if r.step == 'raw':
            #print('r',r.name,r.group.name,r.project.name,r.step,r.version)
            for r2 in records:
                #if (r2.step == 'proc') and (r2.project.name == r.project.name) and (r2.group.name == r.group.name) and (r2.name.startswith(r.name)) and (r2.version == 'preprocessed-VR-sessions'):
                #    print('r2',r2.name,r2.group.name,r2.project.name,r2.step,r2.version,r2.name.startswith(r.name))
                if (r2.step == 'proc') and (r2.project.name == r.project.name) and (r2.group.name == r.group.name) and (r2.name.startswith(r.name)) and (r2.version == 'preprocessed-VR-sessions'):
                    r2.parent_record = r
                    r.add_child_record(r2)
                    #print('r2',r2.id,r2.name,r2.group.name,r2.project.name,r2.step,r2.version,r.child_records)
        if r.step == 'proc' and r.version == 'preprocessed-VR-sessions':
            for r2 in records:
                if (r2.step == 'proc') and (r2.project.name == r.project.name) and (r2.group.name == r.group.name) and (r2.name.startswith(r.name)) and (r2.version == 'preprocessed-VR-sessions-gated'):
                    r2.parent_record = r
                    r.add_child_record(r2)
    return records

def update_put_group_pars(group):
    # Check if group has a pars.json file and update it or create it
    assert isinstance(group, Group) and group.step == 'proc', 'group must be a Group object and step must be proc'
    #print('group.parent_group path',group.parent_group.path)
    if group.parsFileExists():
        pars = group.loadPars()
    else:
        pars = group.putPar()
    #print('pars',pars)
    keeperPath = os.path.normpath(os.path.join( group.path,group.version) ) # group.path +'/preprocessed-VR-sessions'
    if not os.path.exists(keeperPath):
        os.makedirs(keeperPath)
    keepers = os.listdir(keeperPath)   
    return pars,keepers

def update_put_groups_pars(groups):
    procGroups = [g for g in groups if (g.step == 'proc') and (g.version == 'preprocessed-VR-sessions')]
    for group in procGroups:
        pars,keepers = update_put_group_pars(group)
        #print('keepers',keepers)
        for g in group.records:
            assert g.name+'.csv' in keepers, 'record '+g.name+' not in keepers'+str(keepers)

def update_put_record_pars(record):#,keepers):
    #find out if allready preprocessed. If trough check if csv and info in json match
    # Check if record group has a pars.json file and update it or create it
    assert isinstance(record, Record) and record.step == 'proc', 'record must be a Record object and step must be proc'
    assert record.group.parsFileExists(), 'it is assumed that pars are loaded in the group before that in the record with update_put_group_pars or update_put_groups_pars'
    pars = record.group.loadPars()
    if record.isProcRecordInProcFile():
        record.loadProcRecordFromProcFile()
    else:
        record.putProcRecordInProcFile()

def update_put_records_pars(records):
    procRecords = [r for r in records if (r.step == 'proc') and (r.version == 'preprocessed-VR-sessions')]
    for record in procRecords:
        update_put_record_pars(record)

def load_data_and_link(steps,stepsPaths, projects, groups, records):
    print('load projects')
    for step in steps:  
        projects,groups,records = load_data(stepsPaths[step], step, projects, groups, records)


    print('steps')
    for s in steps:
        print(s)
    print('-projects')
    for p in projects:
        print('-',p.name,p.step)
        #for g in p.groups:
        #    print('--',g.name,g.step)
                #for r in g.records:
                #    print('---',r.name,r.step)

    print('load project lineage')
    projects = link_projects(projects)
    print('load group lineage')
    groups = link_groups(groups)
    print('load record lineage')
    records = link_records(records)

    update_put_groups_pars(groups)
    update_put_records_pars(records)
    return projects, groups, records


if __name__ == "__main__":

    steps = ['raw','proc']#'raw',
    stepsPaths = {'raw':'./test/records/raw/','proc':'./test/records/proc/'} #{'raw':rawProjectsPath,'proc':procProjectsPath}
    projects = []
    groups = []
    records = []

    projects, groups, records = load_data_and_link(steps,stepsPaths, projects, groups, records)

        #print('projects')
        #print([(p.name,p.step) for p in projects])
        #print('groups')
        #print([(g.name, g.project.name, g.project.step) for g in groups])
        #print('records')
 
    for g in groups:
        if g.project.name == 'event1' and g.name == 'group1':
            print(g.id, g.name,g.version,g.name,g.project.name,g.step)     

    for r in records:
        if r.project.name == 'event1' and r.group.name == 'group1' and r.name.startswith('U1'):
            print(r.id, r.name,r.version,r.group.name,r.group.id,r.project.name,r.step)        
    
    print('---------------------------------')
    print('---------------------------------')



    
    print('projects parents')
    print([(p.name,p.step, p.parent_project.name, p.parent_project.step ) for p in projects if p.parent_project is not None])

    print('projects childs')
    print([(p.name,p.step, [(cp.name,cp.step) for cp in p.child_projects] ) for p in projects])
    

    g = groups[0]
    print('group 0',g.name,g.project.name,g.step)
    print('childs group 0')
    for cg in g.child_groups:
        print('child group',cg.name,cg.project.name,cg.step,cg.version)
        for gg in cg.child_groups:   
            print('grandchild group',gg.name,gg.project.name,gg.step,gg.version)




    for i in range(2): #range(20):
        r = records[i]
        print('record '+str(i),r.name,r.group.name,r.project.name,r.step)
        print('childs record '+str(i))
        if len(r.child_records) > 0:
            for cr in r.child_records:
                print('child record',cr.name,cr.group.name,cr.project.name,cr.step,cr.version)
                #for gr in cr.child_records:   
                #    print('grandchild record',gr.name,gr.group.name,gr.project.name,gr.step,gr.version) """

    

    
    cgroup = groups[0].child_groups[0]
    print('cgroup',cgroup.name,cgroup.pars, cgroup.step)
    print('cgroup record',[(cg.name,cg.step,cg.pars) for cg in cgroup.records])
