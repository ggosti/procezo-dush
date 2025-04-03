
# Define classes Project, Group, and Record with relationships and data methods.
import os
import json

class Record:
    """
    Record model which are part of a groups.

    >>> record1 = Group(group_id=1, name="Test Record 1", path = "/path/project/group/record1")
    >>> record2 = Group(group_id=2, name="Test Record 2", path = "/path/project/group/record2")

    >>> record1.name
    'Test Record 1'

    >>> record2.name
    'Test Record 2'
    """
    def __init__(self, record_id, name, path, step, df):
        self.id = record_id
        self.name = name
        self.path = path
        self.step = step
        self.project = None
        self.version = None
        self.notes = {} #Column(String, nullable=True)
        self.parent_record = None
        self.group = None
        self.pars = None # I think this feature can be removed in future versions
        self.data = df  #df should be a Pandas DataFrame
        if 'time' in df.columns:
            self.timeKey = 'time'
        elif 'Time' in df.columns:
            self.timeKey = 'Time'
        elif 't' in df.columns:
            self.timeKey = 't'   
        else:
            self.timeKey = None

        self.child_records = []

    def set_ver(self, ver):
        self.version = ver

    def add_child_record(self, record):
        self.child_records.append(record)

    def isProcRecordInProcFile(self):
        pars = self.group.loadPars()
        return (self.name in pars['preprocessedVRsessions'].keys())
    
    def loadProcRecordFromProcFile(self):
        pars = self.group.loadPars()
        dfS = self.data[self.timeKey]
        tInt = pars['preprocessedVRsessions'][self.name]['t0'],pars['preprocessedVRsessions'][self.name]['t1']
        tInt1 = dfS.min(),dfS.max()
        assert tInt==tInt1, ('mismatch error between csv and pars',self.name,'tInt',tInt,'tInt1',tInt1)
        self.pars = pars['preprocessedVRsessions'][self.name]

    def putProcRecordInProcFile(self):
        pars = self.group.loadPars()
        dfS = self.data[self.timeKey]
        tInt = float(dfS.min()),float(dfS.max())
        pars['preprocessedVRsessions'][self.name] = {'t0':tInt[0],'t1':tInt[1]}
        self.pars = pars['preprocessedVRsessions'][self.name]
        self.group.updateParFile()


        

class Group:
    """
    Group model for managing groups of records which are part of a project.

    >>> group1 = Group(group_id=1, name="Test Group 1", path = "/path/project/group1")
    >>> group2 = Group(group_id=2, name="Test Group 2", path = "/path/project/group2")

    >>> group1.name
    'Test Group 1'

    >>> group2.name
    'Test Group 2'

    >>> record1 = Group(group_id=1, name="Test Record 1", path = "/path/project/group/record1")
    >>> record2 = Group(group_id=2, name="Test Record 2", path = "/path/project/group/record2")
    >>> group1.add_record(record1)
    >>> group1.add_record(record2)

    >>> [g.name for g in group1.records]
    ['Test Record 1', 'Test Record 2']
    
    """
    def __init__(self, group_id, name, path, step):
        self.id = group_id
        self.name = name
        self.path = path 
        self.step = step
        self.version = None
        self.pars_path = None # I think this feature can be removed in future versions
        self.pars = None # I think this feature can be removed in future versions
        self.panoramic = False
        self.startDate = None  
        self.endDate = None 
        self.notes = {} 


        self.parent_group = None
        self.project = None

        self.records = []
        self.child_groups = []

    def set_ver(self, ver):
        self.version = ver

    def set_panoramic(self, panoramic):
        self.panoramic = panoramic
        if self.parsFileExists():
            d = self.loadPars()
        self.pars['panoramic'] = True
        self.updateParFile()

    def add_record(self, record):
        self.records.append(record)

    def add_child_group(self, group):
        self.child_groups.append(group)

    def isParsLoaded(self):
        return self.pars is not None
    
    def parsFileExists(self):
        file = os.path.normpath(os.path.join( self.path,'pars.json') )
        return os.path.isfile(file)
    
    def loadPars(self):
        if self.isParsLoaded():
            pars = self.pars
        else:
            file = os.path.normpath(os.path.join( self.path,'pars.json') )
            self.pars_path = file
            with open(file) as f:
                pars = json.load(f)
            #print("loaded pars",file,pars)
            self.pars = pars
        # TODO: we will need to check if an other proc version is added'
        return pars
    
    def putPar(self):
        file = os.path.normpath(os.path.join( self.path,'pars.json') )
        print('putPar',file)
        print('self.name',self.name,self.parent_group)
        assert self.parent_group is not None, 'parent_group is None'
        pars = {'group': self.parent_group.name,
                'raw records folder': os.path.normpath(self.parent_group.path),
                'raw records': [r.name for r in self.parent_group.records],
                'bbox':{},
                'preprocessedVRsessions':{} }
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(pars, f, ensure_ascii=False, indent=4) 
        self.pars = pars
        return pars
    
    def updateParFile(self):
        file = os.path.normpath(os.path.join( self.path,'pars.json') )
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.pars, f, ensure_ascii=False, indent=4) 
        return self.pars


class Project:
    """
    Project model for managing projects folders containing groups and other attributes.


    >>> project1 = Project(project_id=1, name="Test Project 1",path = "/path/project1")
    >>> project2 = Project(project_id=2, name="Test Project 2",path = "/path/project2")

    >>> project1.name
    'Test Project 1'

    >>> project2.name
    'Test Project 2'

    >>> group1 = Group(group_id=1, name="Test Group 1", path = "/path/project1/group1")
    >>> group2 = Group(group_id=2, name="Test Group 2", path = "/path/project2/group2")
    >>> group3 = Group(group_id=1, name="Test Group 3", path = "/path/project2/group3")


    >>> group1.name
    'Test Group 1'

    >>> group2.name
    'Test Group 2'

    >>> project1.add_group(group1)

    >>> [g.name for g in  project1.groups]
    ['Test Group 1']

    >>> project2.add_group(group2)
    >>> project2.add_group(group3)

    >>> [g.name for g in  project2.groups]
    ['Test Group 2', 'Test Group 3']

    """
    def __init__(self, project_id, name, path, step):
        self.id = project_id
        self.name = name
        self.path = path #Column(String, nullable=True)
        self.step = step
        self.startDate = None  #Column(Date, nullable=True)
        self.endDate = None #endDate #Column(Date, nullable=True)
        self.notes = {} #Column(String, nullable=True)
        self.parent_project = None

        self.groups = []
        self.child_projects = []

    def add_group(self, group):
        self.groups.append(group)

    def add_child_project(self, project):
        self.child_projects.append(project)




