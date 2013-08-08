"""  

  http://github.com/sfcta/timesheet

  Timesheet, Copyright 2013 San Francisco County Transportation Authority
                            San Francisco, CA, USA
                            http://www.sfcta.org/
                            info@sfcta.org

  This file is part of Timesheet.

  Timesheet is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Timesheet is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with Timesheet.  If not, see <http://www.gnu.org/licenses/>.
  
"""

from datetime import datetime,timedelta
import pkg_resources
pkg_resources.require("SQLObject>=0.7.1")
from turbogears.database import PackageHub
# import some basic SQLObject classes for declaring the data model
# (see http://www.sqlobject.org/SQLObject.html#declaring-the-class)
from sqlobject import SQLObject, SQLObjectNotFound, RelatedJoin
# import some datatypes for table columns from SQLObject
# (see http://www.sqlobject.org/SQLObject.html#column-types for more)
from sqlobject import *
from turbogears import identity

__connection__ = hub = PackageHub('timesheet')

"""
# Note 1: to change the model in-place, do the following from the python prompt:

from sqlobject import *
connection = connectionForURI('sqlite:///c|/devdata.sqlite')
sqlhub.processConnection=connection
class XXX(SQLObject):
    class sqlmeta:
        fromDatabase=True

# NOTE!  User table is actually class 'tg_user', not class 'User'.  Special!!

# Then, some examples:
XXX.sqlmeta.addColumn(PickleCol("colname", default={}), changeSchema=True))
XXX.sqlmeta.addColumn(Col("colname", foreignKey='Project', sqlType='INT', default=None), changeSchema=True))


# Note 2: to add table INDEXES in-place, do the following from python prompt (after note 1):
(note also, colname is "colname" if a regular column, and "colnameID" if a foreign key. Whew!

XXX.sqlmeta.addIndex(DatabaseIndex('colname', name='indexname'))
XXX.createIndexes()

"""
textStatus = ['Incomplete','Awaiting Approval','Payroll Preview','Approved','Sent to ADP','Void & Hide']

class Timesheet(SQLObject):
    whose = ForeignKey('User', default=None)
    startdate = DateCol(default=None)
    approvedBy = ForeignKey('User', default=None)
    approvedOn = DateCol(default=None)
    status = IntCol(default=0) # 0:incomplete, 1:complete, 2:approved, 3:rejected, 4:locked
    daynotes = PickleCol(default={})

    whoseindex = DatabaseIndex(whose)
    startdateindex = DatabaseIndex(startdate)
    statusindex = DatabaseIndex(status)

    # Enddate property.  Neat!
    def _get_enddate(self):
        enddate = self.startdate + timedelta(days=13)
        return enddate.strftime("%b %d, %Y")

    # PPE: Pay Period Ending
    def _get_ppe(self):
        return (self.startdate + timedelta(days=13))

    def _get_enddatewithoutyear(self):
        enddate = self.startdate + timedelta(days=13)
        return enddate.strftime("%b %d")

    def _get_start(self):
        return self.startdate.strftime("%b %d")

    def _get_totalhours(self):
        hours = 0
        entries = Entry.select(Entry.q.sheet==self)
        for row in entries:
            hours += row.totalhours
        return hours

    def __cmp__(self, other):
        return cmp(self.whose.full_name,other.whose.full_name)

    def __str__(self):
        return '%s,"%s","%s"' % (self.whose.full_name,self._get_enddate(),textStatus[self.status])



class TimePeriodNote(SQLObject):
    startdate = DateCol(default=None)
    note = StringCol(default=None)
    dateindex = DatabaseIndex(startdate)


class Entry(SQLObject):
    sheet = ForeignKey('Timesheet',default=None)
    project = StringCol(default='')
    charge = StringCol(default='Hours')
    hours = PickleCol(default=14*[0.0])
    cellnotes = PickleCol(default={})

    sheetindex = DatabaseIndex(sheet)
    chargeindex = DatabaseIndex(charge)
    projectindex = DatabaseIndex(project)

    # Use props to calculate row total
    def _get_totalhours(self):
        return sum(self.hours)

    # CSV crosstab export uses this string representation:
    def __str__(self):        
        all_notes = '\r\n'.join(self.cellnotes.values())
        all_notes = '"%s"' % all_notes

        return '%s,%s,%s,%f,%s' % (self.charge, self.project[:6], self.project[8:], sum(self.hours),all_notes)

class Project(SQLObject):
    code = StringCol(length=12, default="<none>")
    description = StringCol(length=40, default="")
    hidden = BoolCol(default=False)
    depts = PickleCol(default=[])

    codeindex = DatabaseIndex(code)

    def __str__(self):
        return "%s: %s" % (self.code, self.description)

class Department(SQLObject):
    dept = StringCol(length=30, default="")
    defaultProject = ForeignKey('Project', default=None)
    def __str__(self):
        return self.dept

# ----------------------------------------------------------------------------
# the identity model

class Visit(SQLObject):
    """
    A visit to your site
    """
    class sqlmeta:
        table = 'visit'

    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName='by_visit_key')
    created = DateTimeCol(default=datetime.now)
    expiry = DateTimeCol()

    def lookup_visit(cls, visit_key):
        try:
            return cls.by_visit_key(visit_key)
        except SQLObjectNotFound:
            return None
    lookup_visit = classmethod(lookup_visit)

class VisitIdentity(SQLObject):
    """
    A Visit that is link to a User object
    """
    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName='by_visit_key')
    user_id = IntCol()

class Group(SQLObject):
    """
    An ultra-simple group definition.
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = 'tg_group'

    group_name = UnicodeCol(length=20, alternateID=True,
                            alternateMethodName='by_group_name')
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = RelatedJoin('User', intermediateTable='user_group',
                        joinColumn='group_id', otherColumn='user_id')

    # collection of all permissions for this group
    permissions = RelatedJoin('Permission', joinColumn='group_id',
                              intermediateTable='group_permission',
                              otherColumn='permission_id')

class User(SQLObject):
    """
    Reasonably basic User definition.
    Probably would want additional attributes.
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = 'tg_user'

    defaultTimesheet = ForeignKey('Timesheet', default=None)
    isActive = BoolCol(default=True)
    isManager = BoolCol(default=False)
    isIntern  = BoolCol(default=False)
    dept = ForeignKey('Department', default=None)
    adpFileNumber = IntCol(default=0)
    notes = PickleCol(default=[])

    # from TurboGears identity system:
    user_name = UnicodeCol(length=16, alternateID=True,
                           alternateMethodName='by_user_name')
    email_address = UnicodeCol(length=255, alternateID=True,
                               alternateMethodName='by_email_address')
    full_name = UnicodeCol(length=255)
    password = UnicodeCol(length=40)
    created = DateTimeCol(default=datetime.now)
    approver = ForeignKey('User', default=None)

    groups = RelatedJoin('Group', intermediateTable='user_group',
                         joinColumn='user_id', otherColumn='group_id')

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms |= set(g.permissions)
        return perms

    def _set_password(self, cleartext_password):
        """Runs cleartext_password through the hash algorithm before saving."""
        password_hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(password_hash)

    def set_password_raw(self, password):
        """Saves the password as-is to the database."""
        self._SO_set_password(password)

class Permission(SQLObject):
    """
    A relationship that determines what each Group can do
    """
    permission_name = UnicodeCol(length=16, alternateID=True,
                                 alternateMethodName='by_permission_name')
    description = UnicodeCol(length=255)

    groups = RelatedJoin('Group',
                         intermediateTable='group_permission',
                         joinColumn='permission_id',
                         otherColumn='group_id')
