from sqlobject import *
connection = connectionForURI('sqlite:///c|/devdata.sqlite')
sqlhub.processConnection=connection

class Timesheet(SQLObject):
    class sqlmeta:
        fromDatabase=True

Timesheet.sqlmeta.addIndex(DatabaseIndex('whoseID',name="whoseindex"))
Timesheet.sqlmeta.addIndex(DatabaseIndex('startdate',name="startdateindex"))
Timesheet.sqlmeta.addIndex(DatabaseIndex('status',name="statusindex"))
Timesheet.createIndexes()


class Entry(SQLObject):
    class sqlmeta:
        fromDatabase=True

Entry.sqlmeta.addIndex(DatabaseIndex('sheetID',name="sheetindex"))
Entry.sqlmeta.addIndex(DatabaseIndex('project',name="projectindex"))
Entry.sqlmeta.addIndex(DatabaseIndex('charge', name="chargeindex"))
Entry.createIndexes()


class Project(SQLObject):
    class sqlmeta:
        fromDatabase=True

Project.sqlmeta.addIndex(DatabaseIndex('code',name="codeindex"))
Project.createIndexes()

