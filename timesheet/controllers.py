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

import turbogears as tg
from turbogears import widgets
from turbogears.widgets import AjaxGrid, TableForm
from turbogears import validate, error_handler,validators

from turbogears import controllers, expose, flash, url
from turbogears import identity, redirect
from turbogears.toolbox.catwalk import CatWalk
from cherrypy import request, response
from timesheet.model import User,Timesheet,Entry,Group,Project,Department,TimePeriodNote
from sqlobject import DateTimeCol
from sqlobject.sqlbuilder import AND,OR

import os
import kid

# These are needed for PDF Export:
import ho.pisa as pisa

from datetime import datetime,timedelta
import csv, StringIO
import smtplib
import types

import model


# FORMS and globals -----------------------------------------------------------
def kidfile(name):
    return file(os.path.join('timesheet/templates',name)).read()

INCOMPLETE=0
COMPLETE=1
PAYROLLPREVIEW=2
APPROVED=3
LOCKED=4
VOID=5

TextStatus = ['Incomplete','Awaiting Approval','Payroll Preview (needs approval)','Approved','Sent to ADP','Void & Hide']
LilyOrder =  ["cEarn","O/T","cUsed","Hol","Jury","Sick","Brvmt","Vac","Float","Hours"]

ADPconversion = {
    "cEarn":    "X",
    "O/T":      "O/T Hours",
    "cUsed":    "C",
    "Hol":      "H",
    "Jury":     "J",
    "Sick":     "S",
    "Vac":      "V",
    "Float":    "F",
    "Pers":     "F",
    "Brvmt":    "D",
    "Hours":    "Reg Hours"
}

allDepts = []
for d in Department.select().orderBy("dept"):
    allDepts.append(str(d))

# -----------------------------------------------------------------------------
# Define some forms

class dateform_fields(widgets.WidgetsList):
    '''A date-picking form for creating timesheet sets'''
    start_date = widgets.CalendarDatePicker(
        label = "Pay Period END Date:  ",
        name = "end_date",
        format = '%m/%d/%Y',
        button_text = "Pick...",
        validator = validators.DateTimeConverter(format="%m/%d/%Y"))
    note = widgets.TextField('note',label='Flashbox Text:',default=None,attrs=dict(size="80"))


date_form = TableForm(
    'date_picker', fields = dateform_fields(), action = tg.url('createset'),
    submit_text = "Create timesheet set")

class from_to_fields(widgets.WidgetsList):
        from_date = widgets.CalendarDatePicker(
                label = "Start PPE: :",
                name = "from_date",
                format = '%m/%d/%Y',
                button_text = "Pick...",
                validator = validators.DateTimeConverter(format="%m/%d/%Y"))
        to_date = widgets.CalendarDatePicker(
                label = "Through PPE: :",
                name = "to_date",
                format = '%m/%d/%Y',
                button_text = "Pick...",
                validator = validators.DateTimeConverter(format="%m/%d/%Y"))

from_to_form = TableForm('FromToForm',
                   fields = from_to_fields(),
                   action = tg.url('/buildcrosstabs'),
                   submit_text = "Export to CSV"
               )

# -----------------------------------------------------------------------------
class EmployeeForm(TableForm):
    """Form for editing employee information and reviewing their timesheets."""
    params = ['textfields', 'ismanager', 'isactive', 'isintern', 'dept', 'approver','who','sheets','notes','addnote']
    template = kidfile('employee.kid')

class EmailForm(TableForm):
    params = ['me','person','note','ts']
    template = kidfile('emailform.kid')

class ProjectForm(TableForm):
    """Form for editing project information and reviewing their timesheets."""
    params = ['rows', 'depts', 'addproj']
    template = kidfile('projectform.kid')

class EditForm(TableForm):
    """Form for entering/editing timesheet data!"""
    params = ['dates','rows','entries', 'coltotals', 'notes']
    template = kidfile('editform.kid')

class ExportForm(TableForm):
    """Form for reviewing sheets for export to ADP Payroll"""
    params = ['sheets','notyet','already','period']
    template = kidfile('exportform.kid')

# -----------------------------------------------------------------------------
class Root(controllers.RootController):

    #Allow database editing, for now
    database = CatWalk(model)

    def buildProjectsByDept(self= None):
        pbd = {}
        lookup = []

        for d in list(Department.select().orderBy('dept')):
            pbd[d.id] = []
            lookup.append(d.id)

        for p in Project.select().orderBy("description"):

            # Skip hidden projects
            if p.hidden:
                continue

            # Only add the project for departments which have no limit list, or for which it is True
            for d in range(len(allDepts)):
                try:
                    if p.depts == None or p.depts[d] == True:
                        pbd[lookup[d]].append(p.description)
                except:
                        pbd[lookup[d]].append(p.description)
        return pbd

    def buildProjectLookup(self=None):
        plookup = {}
        pcodes = {}

        for p in Project.select().orderBy("description"):
            # Skip hidden projects
            if p.hidden:
                continue

            # Add to the global description lookup
            pcodes[p.code] = p.id

            plookup[p.description] = p
            # Also add the "..." version just in case
            if len(str(p))>30:
                truncatedname = str(p)[8:30]+"..."
                plookup[truncatedname] = p

        return pcodes, plookup

    projectsByDept = buildProjectsByDept()
    projectLookupByCode, projectLookupByDescription = buildProjectLookup()


    @expose(template="timesheet.templates.viewsheets")
    @identity.require(identity.not_anonymous())
    def index(self):
        """ List all timesheets for this person, plus a reviewer table if needed """

        me = identity.current.user

        # Get timesheets which belong to 'who', and are not yet sent to ADP
        mysheets = Timesheet.select(AND(Timesheet.q.whose==me,
                                        Timesheet.q.status<=APPROVED)).orderBy('startdate')

        # Get timesheets which 'who' needs to approve
        allapprovals = sorted(Timesheet.select(OR(Timesheet.q.status==COMPLETE,
                                                   Timesheet.q.status==PAYROLLPREVIEW)))

        mgrapprovals = []
        staffapprovals = []
        internapprovals = []
        managerview = []

        for sheet in allapprovals:
            # Special cases:
            if (sheet.whose.approver == me or "timesheet-admin" in tg.identity.current.groups):
                    if sheet.whose.isManager:
                        mgrapprovals.append(sheet)
                    elif sheet.whose.isIntern:
                        internapprovals.append(sheet)
                    else:
                        staffapprovals.append(sheet)

                    continue

            if (me.isManager):
                # Can't approve my own timesheet even if I'm a manager
                if (sheet.whose == me): continue

                # But I can approve it if it's in my dept or it's an intern
                if ((sheet.whose.dept == me.dept) or (sheet.whose.isIntern)):
                    if sheet.whose.isManager:
                        mgrapprovals.append(sheet)
                    elif sheet.whose.isIntern:
                        internapprovals.append(sheet)
                    else:
                        staffapprovals.append(sheet)

                    continue

        # Managers want to see the status of all their employees
        sheetsbydate = []
        if (me.isManager):
            opensheets = Timesheet.select(Timesheet.q.status<=APPROVED).orderBy('startdate')

            startd = ""
            sheetsbyname = []

            for sheet in opensheets:
                if (sheet.whose.dept != me.dept):
                    continue

                if (sheet.startdate == startd):
                    sheetsbyname.append(sheet)
                else:
                    if (len(sheetsbyname)>0): sheetsbydate.append(sheetsbyname)
                    sheetsbyname = [sheet]
                    startd = sheet.startdate

            if (len(sheetsbyname)>0): sheetsbydate.append(sheetsbyname)

        # Get timesheets which are already closed, for reference
        alloldsheets = Timesheet.select(AND(Timesheet.q.whose==me,
                                        Timesheet.q.status==LOCKED)).orderBy('startdate')
        oldsheets = {}
        for yr in range(datetime.now().year,2008,-1): oldsheets[yr] = []

        for sheet in alloldsheets:
            sheetyear = (sheet.startdate + timedelta(days=13)).year
            oldsheets[sheetyear].append(sheet)

        return dict(person=me, sheets=mysheets, oldsheets=oldsheets, managerview=sheetsbydate,
                    mgrapps=mgrapprovals, staffapps=staffapprovals, internapps=internapprovals)


    @expose(template='timesheet.templates.addset')
    @identity.require(identity.in_group("timesheet-admin"))
    def addset(self):
        return dict(form=date_form)

    @expose()
    @error_handler(addset)
    @validate(form=date_form)
    @validate(validators={'start_date': validators.DateValidator(after_now=True)})
    @identity.require(identity.in_group("timesheet-admin"))
    def createset(self, end_date, note):
        """ Add set of timesheets for active employees """

        # Now Mo wants everything done by END date, not start date, so let's count back
        real_start_date = end_date + timedelta(days = -13)

        # First check if this timesheet set already exists.  If so, just update the note.
        if list(Timesheet.select(Timesheet.q.startdate==real_start_date)):
            flash('That set already exists.  Updating note only.')
            try:
                # Replace old note
                thisnote = TimePeriodNote.select(TimePeriodNote.q.startdate==real_start_date).getOne()
                thisnote.note = note
            except:
                # Create a new note if one doesn't already exist
                TimePeriodNote(startdate=real_start_date,note=note)

            redirect(url('/index'))


        activeEmps = User.select(User.q.isActive)
        for each in activeEmps:
            t = Timesheet(whose=each, startdate=real_start_date)

            # No longer populating with default entries here, because user may wait until the
            # last moment to set their default.  We'll deal with it when it's time to edit
            # the timesheet instead.

        # If admin added a note to this time period, create a TimePeriodNote.
        if (note):
            TimePeriodNote(startdate=real_start_date,note=note)

        # All done
        flash('Added timesheets for pay period ending '+ end_date.strftime("%b %d, %Y") + ".")
        redirect(url('/index'))


    @expose()
    @error_handler(addset)
    @validate(form=date_form)
    @validate(validators={'start_date': validators.DateValidator(after_now=True)})
    @identity.require(identity.in_group("timesheet-admin"))
    def createonesheet(self, who, end_date, note):
        """ Add one timesheet for an employee """

        start_date = end_date - timedelta(days=13)

        p = User.select(User.q.id==who).getOne()
        t = Timesheet(whose=p, startdate=start_date)

        flash('Added timesheet for period ending '+ end_date.strftime("%b %d, %Y") + ".")
        redirect(url('/editperson/' + str(who)))


    @expose(template="timesheet.templates.editsheet")
    @identity.require(identity.not_anonymous())
    def edit(self,id):
        """ Edit this timesheet -- build the edit widgets for display """
        ts = Timesheet.select(Timesheet.q.id==id).getOne()
        who = ts.whose

        # Check permissions! Editing should ONLY be allowed if:
        # 1) You are super-admin; or,
        # 2) The timesheet is not yet locked AND you are its owner; or,
        # 3) The timesheet is not yet locked AND you are its special approver; or,
        # 4) Should managers be able to edit employee timesheets?  For now, yes.

        if identity.in_group("timesheet-admin") \
            or (identity.current.user.id==who.id and ts.status<LOCKED) \
            or (identity.current.user.id==who.approver.id and ts.status<LOCKED) \
            or (identity.current.user.isManager and ts.status<LOCKED):
                pass
        else:
            flash("Sorry, you cannot edit that timesheet.")
            raise redirect (url('/'))

        entries = Entry.select(Entry.q.sheet==ts).orderBy("id")

        # Don't start with an empty timesheet.
        if entries.count() == 0:

            # First see if the person has a default timesheet and use it if so.
            try:
                if who.defaultTimesheet:
                    for entry in Entry.select(Entry.q.sheet==who.defaultTimesheet):
                        Entry(sheet=ts, charge=entry.charge, project=entry.project)
                else:
                    # No default; just create one entry.
                    Entry(sheet=ts,charge="Hours",project=str(ts.whose.dept.defaultProject))

            except:
                # Fail; just create one entry.
                Entry(sheet=ts,charge="Hours",project=str(ts.whose.dept.defaultProject))

            # And finally recreate the entries list.
            entries = Entry.select(Entry.q.sheet==ts)

        # Unmark as complete if we're editing a previously-completed TS
        if (ts.status>=COMPLETE):
            flash("You must resubmit this timesheet for review after editing.")
            ts.status = INCOMPLETE
            ts.approvedBy = None
            ts.approvedOn = None

        # Build data for timesheet:  dates, rowdata, row id's, and column totals.
        dates = self.buildDates(ts.startdate)
        rowdata, entry_ids = self.buildRows(entries,who)

        # And daily notes too.
        notes = []
        if ts.daynotes != None and len(ts.daynotes)>0:
            for day in sorted(ts.daynotes.keys()):
                notewidget = widgets.TextArea(
                    name='note%d' % day, default=ts.daynotes[day],rows=1,cols=60)
                daytxt = dates[day].replace('.','/')
                notes.append([daytxt,notewidget])

        # Build the column-total labels
        coltotals = []
        for each in range(15):
            coltotals.append(widgets.Label(default=''))

        # And create a form using those rows.
        widgyform = EditForm(dates=dates,rows=rowdata, entries=entry_ids,
                             coltotals=coltotals, notes=notes,action='/savetimesheet')

        # Add a flashnote if this time period has an admin message from Mo
        try:
            toast = TimePeriodNote.select(TimePeriodNote.q.startdate == ts.startdate).getOne()
            if (toast):
                flash(toast.note)
        except:
            # Just ignore if there's no admin note
            pass

        return dict(person=who, ts=ts, form=widgyform)

    @expose(template="timesheet.templates.approve")
    @identity.require(identity.not_anonymous())
    def viewonly(self, timesheetnumber, review=False):
        """Look at this timesheet"""

        ts = Timesheet.select(Timesheet.q.id==timesheetnumber).getOne()
        who = ts.whose

        # Get the entries in the order Lily likes them
        entries = []
        for charge in LilyOrder:
            entries.extend(Entry.select(AND(Entry.q.sheet==ts,Entry.q.charge==charge)).orderBy("project"))

        # Build data for timesheet:  dates, rowdata, row id's, and column totals.
        dates = self.buildDates(ts.startdate)
        rowdata, coltotals, entry_ids = self.buildReadonlyRows(entries)

        # And create a dictionary using those rows
        return dict(person=who, ts=ts, dates=dates, rows=rowdata, entries=entry_ids,
                             coltotals=coltotals, me=None, review=review)

    @expose(template="timesheet.templates.approve")
    @identity.require(identity.not_anonymous())
    def approve(self, timesheetnumber, manager):
        """Approve this timesheet"""

        ts = Timesheet.select(Timesheet.q.id==timesheetnumber).getOne()
        who = ts.whose

        # Check permissions! Approval should ONLY be allowed if:
        # 1) You are super-admin; or,
        # 2) You are a manager (technically this isn't fair, but there are cases where one mgr may approve for another)
        # 3) You are special-approver for this timesheet's owner

        if identity.in_group("timesheet-admin") or \
            identity.current.user.isManager or \
            identity.current.user.id == ts.whose.approver.id:
                pass
        else:
            flash("Sorry, you cannot review that timesheet.")
            raise redirect (url('/'))

        if ts.status<COMPLETE or ts.status>=APPROVED:
            flash("That timesheet is either incomplete or has already been approved.")
            raise redirect (url('/'))

        entries = []
        for charge in LilyOrder:
            entries.extend(Entry.select(AND(Entry.q.sheet==ts,Entry.q.charge==charge)).orderBy("project"))

        # Build data for timesheet:  dates, rowdata, row id's, and column totals.
        dates = self.buildDates(ts.startdate)
        rowdata, coltotals, entry_ids = self.buildReadonlyRows(entries)

        # And create a dictionary using those rows
        return dict(person=who, ts=ts, dates=dates, rows=rowdata, entries=entry_ids,
                             coltotals=coltotals, me=manager)

    @expose()
    @identity.require(identity.not_anonymous())
    def approved(self, ts, me):
        t = Timesheet.select(Timesheet.q.id==int(ts)).getOne()

        # Check permissions! Approval should ONLY be allowed if:
        # 1) You are super-admin; or,
        # 2) You are a manager (technically this isn't fair, but there are cases where one mgr may approve for another)
        # 3) You are special-approver for this timesheet's owner

        if identity.in_group("timesheet-admin") or \
            identity.current.user.isManager or \
            identity.current.user.id == t.whose.approver.id:
                pass
        else:
            flash("Sorry, you cannot review that timesheet.")
            raise redirect (url('/'))

        t.approvedBy = int(me)
        t.approvedOn = datetime.now()
        t.status = APPROVED

        flash('Timesheet approved for '+t.whose.full_name+'.')
        redirect(url('/index'))

    @expose()
    @identity.require(identity.not_anonymous())
    def submit(self, ts):
        t = Timesheet.select(Timesheet.q.id==int(ts)).getOne()

        # Check permissions! Approval should ONLY be allowed if:
        # 1) You are super-admin; or,
        # 2) You are special-approver for this timesheet's owner

        if identity.in_group("timesheet-admin") or identity.current.user.id == t.whose.id:
                pass
        else:
            flash("Sorry, you cannot submit that timesheet.")
            raise redirect (url('/'))

        t.status = COMPLETE

        flash('Timesheet submitted for approval.')
        redirect(url('/index'))

    @expose(template=".templates.reject")
    @identity.require(identity.not_anonymous())
    def rejected(self, ts, me):
        """ Manager doesn't like this timesheet.  Ask why! """

        ts = Timesheet.select(Timesheet.q.id==ts).getOne()
        who = ts.whose

        # Check permissions! Approval should ONLY be allowed if:
        # 1) You are super-admin; or,
        # 2) You are a manager (technically this isn't fair, but there are cases where one mgr may approve for another)
        # 3) You are special-approver for this timesheet's owner

        if identity.in_group("timesheet-admin") or \
            identity.current.user.isManager or \
            identity.current.user.id == ts.whose.approver.id:
                pass
        else:
            flash("Sorry, you cannot review that timesheet.")
            raise redirect (url('/'))

        entries = []
        for charge in LilyOrder:
            entries.extend(Entry.select(AND(Entry.q.sheet==ts,Entry.q.charge==charge)).orderBy("project"))

        # Build data for timesheet:  dates, rowdata, row id's, and column totals.
        dates = self.buildDates(ts.startdate)
        rowdata, coltotals, entry_ids = self.buildReadonlyRows(entries)

        notewidget = widgets.TextArea(name="note",rows=4,cols=60)

        form = EmailForm(action='/sendemail', person=who, note=notewidget, ts=ts.id, me=me)

        # And create a dictionary using those rows
        return dict(person=who, ts=ts, dates=dates, rows=rowdata, entries=entry_ids,
                             coltotals=coltotals, me=me, form=form)


    @expose()
    @identity.require(identity.not_anonymous())
    def sendemail(self, **data):
        """ Send email explaining the rejection"""
        # TODO: Should check to make sure the reason is not blank.

        # See if we can get which link was clicked, and do the right thing
        whichlink = data['whichlink']

        if whichlink == "cancel":
            redirect(url('/index'))

        # Reject timesheet and send email.
        t = Timesheet.select(Timesheet.q.id==data['ts']).getOne()
        t.status = INCOMPLETE

        sender = User.select(User.q.id==data['from']).getOne()
        toaddr = t.whose.full_name + "<" + t.whose.email_address + ">"
        fromaddr = sender.full_name + "<" + sender.email_address + ">"

        msg = ("From: %s\r\nReply-To: %s\r\nTo: %s\r\nSubject: Timesheet needs to be resubmitted\r\n" % 
              (fromaddr, fromaddr, toaddr))

        msg = msg + "Your timesheet was sent back for editing by "+sender.full_name+"."
        if data['note'] != None and len(data['note'])>0:
            msg = msg + " The reason given was:\r\n\r\n"+data['note']

        msg = msg + '\r\n\r\nTo edit this timesheet, go to http://timesheets/edit/%d' % t.id

        try:
            mailserver = tg.config.get('mail.server','localhost')
            port = tg.config.get('mail.port',25)
            server = smtplib.SMTP(mailserver,port)
            server.set_debuglevel(1)
            server.sendmail(fromaddr, toaddr, msg)
            server.quit()
        except:
            flash('Sending email failed.  I tried; sorry.\r\nTimesheet marked rejected, but please notify them yourself...')
            redirect(url('/index'))

        flash('Email sent to '+t.whose.full_name+'.')
        redirect(url('/index'))

    @expose()
    @identity.require(identity.not_anonymous())
    def savetimesheet(self, **data):
        """ Save/Close timesheet being edited """

        # data returns a field "entries" with the list of row ID's
        # and then fields with names "0" thru "13" for each day, and
        # those are each arrays of strings, one string per row.  Fun!
        # So, let's parse it.

        daycols = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13']
        sheet = None

        # First get the rows on this page.
        rows = data['entries'].split(';')

        # Cell notes  - which take the form "row:day/text"
        cellnotes = {}
        if 'cellnotes' in data:
            fromweb = data['cellnotes']

            # Sometimes we get a string, sometimes we get a list *sigh*
            if type(fromweb) is types.UnicodeType: fromweb = data['cellnotes'],

            for cnote in fromweb:
                lookup = cnote[0:cnote.find('/')]
                cellnotes[lookup] = cnote[1+cnote.find('/'):]

        # Then go thru the rows and gather the hours & details
        totalhours = 0.0
        for row in range(len(rows)):
           # Hours
           hours = 14*[0.0]
           cellnotesforthisrow = {}

           for day in range(14):
                lookup = '%d:%d' % (row,day)
                h = data.get(lookup,'')
                if (h != ''):
                    try:
                        hours[day] = float(h)
                        totalhours += hours[day]
                    except:
                        continue

                # Cell notes by day
                if lookup in cellnotes:
                    cellnotesforthisrow[day] = cellnotes[lookup]

           # Grab the charge codes
           # This is hacky; for some reason I'm getting a string if there's only one row,
           # and a list if there's more than one row.  I'd prefer a list either way. :-(

           charge = data['Charge']
           project= data['Project']

           if len(rows)>1:
               charge = data['Charge'][row]
               project= data['Project'][row]

           # And now, save to database!! w00T!
           thisEntry = Entry.select(Entry.q.id==int(rows[row])).getOne()
           if sheet==None: sheet = thisEntry.sheet

           thisEntry.charge = charge
           thisEntry.hours = hours
           thisEntry.cellnotes = cellnotesforthisrow
           try:
                thisEntry.project = str(self.projectLookupByDescription[project])
           except:
                print "### UGH! Project codes changed!"
                self.projectLookupByCode,self.projectLookupByDescription = self.buildProjectLookup()
                thisEntry.project = str(self.projectLookupByDescription[project])


#           except:
#               pass  # This does happen if saving a TS before entries made.  Hopefully OK...?

        # Save the timesheet notes, too
        dict = sheet.daynotes
        if dict == None:
            dict = {}
        for day in range(14):
            try:
                txt = data['note%d' % day]
                dict[day] = txt
            except:
                pass
        sheet.daynotes = dict

        # See if we can get which link was clicked, and do the right thing
        whichlink = data['whichlink']

        if whichlink == "addrow":
            # Create a new row
            row = Entry(sheet=sheet)

            # Set the default project, if one has been defined
            if sheet.whose.dept.defaultProject:
                row.project = str(sheet.whose.dept.defaultProject)

            # Continue editing the sheet
            raise redirect(url('/edit/%d' % sheet.id))

        elif whichlink == "review":
            # Clean up the user's mess: 1) remove extra notes
            dict = sheet.daynotes
            if dict != None and len(dict)>0:
                for k,v in dict.items():
                    if v.strip() == "":
                        del dict[k]
                sheet.daynotes = dict

            # Clean up the user's mess: 2) remove entry lines with no hours
            for e in list(Entry.select(Entry.q.sheet==sheet)):
                if e.totalhours == 0.0:
                    Entry.delete(e.id)

            # Now show review page so user can verify and submit timesheet
            flash('*** FINAL REVIEW: %.1f total hours. This timesheet isn\'t final until you click "Submit for Approval".' % (totalhours,))
            raise redirect(url('/viewonly/%d/%d' % (sheet.id,True)))

        elif whichlink.startswith("rm"):
            id = int(whichlink[2:])
            row = Entry.select(Entry.q.id==id).getOne()
            if (row != None):
                Entry.delete(id)
            raise redirect(url('/edit/%d' % sheet.id))

        elif whichlink.startswith('addnote'):
            id = int(whichlink[7:])

            # This is weird, but it has to handle no-notes and existing-notes.
            dict = sheet.daynotes
            if dict == None or len(dict)==0:
                dict = {id:""}
            elif id not in dict:
                dict[id] = ""
            sheet.daynotes = dict

            raise redirect(url('/edit/%d' % sheet.id))

        elif whichlink == "makedefault":
            who = sheet.whose
            who.defaultTimesheet = sheet
            flash('Default timesheet saved.  Future timesheets will use this as template.')
            raise redirect(url('/edit/%d' % sheet.id))

        raise redirect(url('/index'))


    @expose(template=".templates.exportwhat")
    @identity.require(identity.in_group("timesheet-admin"))
    def export(self):
        """ Show a simple list of the timesheet PERIODS that are still open/unresolved. """
        allopensheets = Timesheet.select(Timesheet.q.status<LOCKED).orderBy("-startdate")
        timeperiods = {}

        # First get all open sheets and remember their time periods
        for sheet in allopensheets:
            period = sheet.startdate
            if period in timeperiods:
                timeperiods[period] = timeperiods[period] + 1
            else:
                timeperiods[period] = 1

        # Then get all closed sheets and remember their time periods too!
        allclosedsheets = Timesheet.select(Timesheet.q.status==LOCKED).orderBy("-startdate")
        closedtimeperiods = []

        for sheet in allclosedsheets:
            period = sheet.startdate
            if (period not in timeperiods) and (period not in closedtimeperiods):
                closedtimeperiods.append(period)

        return dict(periods=timeperiods, closedperiods=closedtimeperiods)


    @expose(template=".templates.export")
    @identity.require(identity.in_group("timesheet-admin"))
    def exportts(self, startdate):
        """ Show list of exportable timesheets for transfer to ADP or PDF"""
        allsheets = sorted(list(Timesheet.select(Timesheet.q.startdate==startdate)))

        # Do some magic to split the sheets into groups.
        sheets = []
        notyetsheets = []
        alreadysentsheets = []
        period = ""

        for s in allsheets:
            if s.status<PAYROLLPREVIEW or s.status==VOID:  # if s.status<APPROVED or s.status==VOID:
                notyetsheets.append([s,TextStatus[s.status]])
            elif s.status == LOCKED:
                alreadysentsheets.append([s,TextStatus[s.status]])
            else:
                sheetid = str(s.id)
                checkbox = widgets.CheckBox(sheetid,label="xx",default=True) #s.whose.full_name)
                sheets.append([s,checkbox])
            if period == "":
                period = s.start + ' - ' + s.enddate

        # Get summary stats of hours in each category. (test with alreadysentsheets first.)
        for charges in LilyOrder:
                rows = []
                for ft in alreadysentsheets:
                    rows.extend(Entry.select(AND(Entry.q.sheet==ft[0],Entry.q.charge==charges)))

                tothours = 0
                for ee in rows:
                    tothours += ee.totalhours
                print charges, tothours

        widgyform = ExportForm(action='/exportnow', sheets=sheets, notyet=notyetsheets,
                                already=alreadysentsheets, period=startdate)

        # Return an array of arrays, so timesheets are categorized by start-date.
        return dict(form=widgyform, period=period)

    @expose()
    @identity.require(identity.in_group("timesheet-admin"))
    def exportnow(self, **data):
        """ Create CSV file of exportable sheets, then lock those sheets """

        # Skip everything if user hit Cancel
        whichlink = data['whichlink']
        if (whichlink == "cancel"):
            raise redirect(url('/index'))

        # But if user clicked "Export" or "Lock", then let's start the madness.
        # Get list of export sheets from web form --
        # apparently only the keys which are checked 'true' are passed from the submit button.
        exportSheets = []
        boxes = data.keys()
        for box in boxes:
            try:
                exportSheets.append(Timesheet.select(Timesheet.q.id==box).getOne())
            except:
                pass # Other form widgets with non-numeric ID's will just be ignored

        # If User clicked "Lock" then just mark them locked and quit
        if (whichlink == "lock"):
            for sheet in exportSheets:
                sheet.status = LOCKED
            flash("%d timesheet(s) marked as 'Sent to ADP'." % len(exportSheets))
            raise redirect(url('/export'))

        # If here then user must have hit "Export", let's do it!
        ADPlist = self.buildCSVfile(exportSheets)

        fnames = ["Co Code","Batch ID","File #", "Temp Dept",
             "Reg Hours", "O/T Hours", "Memo Code", "Memo Amount", "Hours 3 Code", "Hours 3 Amount"
        ]

        outputCSV = StringIO.StringIO()
        outputCSV.write("Co Code,Batch ID,File #,Temp Dept,Reg Hours,O/T Hours,Memo Code,Memo Amount,Hours 3 Code,Hours 3 Amount\r\n")

        writer = csv.DictWriter(outputCSV, dialect='excel',fieldnames=fnames) #,quoting=csv.QUOTE_NONNUMERIC)
        for sheet in ADPlist:
            writer.writerow(sheet)

        # Make CherryPy webserver return a CSV file instead of a webpage
        response.headers['Content-Type'] = "application/x-download"
        response.headers['Content-Disposition'] = 'attachment; filename="PRVEWEPI.CSV"'

        for sheet in exportSheets:
            # Mark all exported sheets as LOCKED, *except* for sheets which are in
            # Payroll Preview.  Those should stay where they are so JLM can see 'em.
            if (sheet.status != PAYROLLPREVIEW):
                sheet.status = LOCKED

        # This will return a raw file to the browser, which should ask user
        # to save/open directly
        return outputCSV.getvalue()

    @expose()
    def copy(self,ts,who):
        return "Not implemented yet..."

    @expose(template=".templates.editprojects")
    @identity.require(identity.in_group("timesheet-admin"))
    def editprojects(self):
        """ Manage the list of billable projects, and the depts which can bill to them """

        projs = list(Project.select().orderBy("code"))
        numDepts = len(allDepts)
        rows = []

        for row in range(len(projs)):
            project = projs[row]

            pCode = project.code
            pDesc = widgets.TextField("desc",default=project.description,attrs=dict(size="40"))
            pHidden=widgets.CheckBox("hide/%d" % (row,), default=project.hidden)
            limits = []

            # TODO to check whether there's a dept-list for this project
            for d in range(numDepts):
                cboxName = "limit/%d/%d" % (row,d)
                if project.depts == None:
                    limits.append(widgets.CheckBox(cboxName,default=False))
                else:
                    try:
                        limits.append(widgets.CheckBox(cboxName,default=project.depts[d]))
                    except:
                        limits.append(widgets.CheckBox(cboxName,default=False))

            rows.append([pHidden,pCode,pDesc,limits])

        # Set up the add-project fields
        addproj = {}
        addproj['code'] = widgets.TextField("addcode",default='',attrs=dict(size="6"))
        addproj['desc'] = widgets.TextField("adddesc",default='',attrs=dict(size="40"))

        projForm = ProjectForm(rows=rows,depts=allDepts,addproj=addproj,action='/updateprojectlist')
        return dict(form=projForm)


    @expose()
    @identity.require(identity.in_group("timesheet-admin"))
    def updateprojectlist(self, **data):
        """ Update the big project list """

        # See if we can get which link was clicked, and do the right thing
        whichlink = data['whichlink']

        if whichlink == "cancel":
            redirect(url('/'))

        # Add a new project?
        if whichlink == 'addnew':
            msg = ''
            if data['addcode'] and len(data['addcode'])==6 and data['adddesc']:
                Project(code=data['addcode'].upper(),description=data['adddesc'])
                msg = 'Project %s added.' % data['addcode']
            else:
                msg = 'Six-letter project code and a description needed.'

            flash(msg)
            redirect('/editprojects')


        # Otherwise, let's go thru the edits:
        codes = list(Project.select().orderBy('code'))
        descs = data['desc']

        # Now analyze all these rows of checkboxes!
        for row in range(len(codes)):
            limits = []
            useLimits = False
            hidden = False

            # Test if project is hidden
            cboxname = "hide/%d" % (row,)
            try:
                answer = data[cboxname]
                hidden = True
            except:
                hidden = False

            # Test dept-level limits
            for d in range(len(allDepts)):
                cboxname = "limit/%d/%d" % (row,d)
                try:
                    answer = data[cboxname]
                    limits.append(True)
                    useLimits = True
                except:
                    limits.append(False)

            # Now for this project, update the description and the checkboxes
            p = codes[row]
            p.description = descs[row]
            p.depts = useLimits and limits or None
            p.hidden = hidden

        # Update GLOBAL projects by Department list -- so we don't have to rebuild for every pageview
        self.projectsByDept = self.buildProjectsByDept()
        self.projectLookupByCode = self.projectLookupByDescription = None

        flash('Project descriptions and departments saved.')
        redirect(url('/'))

    @expose(template='timesheet.templates.manageemps')
    @identity.require(identity.in_group("timesheet-admin"))
    def manageemps(self):
        """ Manage employee list """
        active = User.select(User.q.isActive).orderBy("full_name")
        inactive = User.select(User.q.isActive==False).orderBy("full_name")

        return dict(active=active,inactive=inactive)

    @expose(template=".templates.editperson")
    @identity.require(identity.in_group("timesheet-admin"))
    def editperson(self,who="new",name="xx"):
        """ Edit a person's attributes"""
        p = None
        dName = "Full Name"
        dLogin = "userid"
        dEmail = "who@sfcta.org"
        dADP = ""
        dApprover = ""
        dIsMgr = False
        dIsActive = True
        dIsIntern = False
        dDept = ""
        dID = -1
        dNotes = []
        
        try:
            p = User.select(User.q.id==who).getOne()
            dName = p.full_name
            dLogin = p.user_name
            dEmail = p.email_address
            dADP = p.adpFileNumber
            dApprover = p.approver
            dIsMgr = p.isManager
            dIsActive = p.isActive
            dIsIntern = p.isIntern
            dDept = p.dept
            dID = p.id
            dNotes = p.notes
        except:
            pass

        if dNotes==None: 
            dNotes=[]

        textfields = []
        approvers = ['None']
        x = User.select(User.q.isActive==True).orderBy("full_name")
        for p in x:
            approvers.append(p.full_name)

        textfields.append(widgets.TextField("name",default=dName))
        textfields.append(widgets.TextField("login",default=dLogin))
        textfields.append(widgets.TextField("email",default=dEmail))
        textfields.append(widgets.TextField("adp",default=dADP))

        approverName = dApprover and dApprover.full_name or "None"
        wApprovers = widgets.SingleSelectField("approver",options=approvers,default=approverName)

        wIsManager = widgets.CheckBox("isManager",default=dIsMgr)
        wIsIntern  = widgets.CheckBox("isIntern",default=dIsIntern)
        wIsActive  = widgets.CheckBox("isActive",default=dIsActive)

        wDept = widgets.SingleSelectField("dept",options=allDepts,default=dDept)

        wNewNote = widgets.TextField("newnote",default='',attrs=dict(size='55'))

        empsheets = list(Timesheet.select(Timesheet.q.whose==who).orderBy('-startdate'))
        sheets = []
        for sheet in empsheets:
            tsStatus = widgets.SingleSelectField("status",options=TextStatus,default=TextStatus[sheet.status],
                validator=validators.NotEmpty)
            sheets.append([sheet,tsStatus])

        EmpForm = EmployeeForm(textfields=textfields, dept=wDept, approver=wApprovers,
                                ismanager=wIsManager, isactive=wIsActive, 
                                isintern= wIsIntern, who=dID,
                                sheets=sheets, addnote=wNewNote, notes=dNotes,
                                action='/updateperson')

        # Add field to create one new timesheet for this employee
        DateForm = None
        if (dID != -1):
            DateForm = TableForm('date_picker', fields = dateform_fields(),
                action = tg.url('/createonesheet/'+str(dID)), submit_text = "Create timesheet")

        return dict(form=EmpForm, dateform=DateForm)

    @expose()
    @identity.require(identity.in_group("timesheet-admin"))
    def updateperson(self, **data):
        """ Update this person's attributes """

        # See if we can get which link was clicked, and do the right thing
        whichlink = data['whichlink']

        if whichlink == "cancel":
            redirect(url('/manageemps'))

        if whichlink == 'addnote':
            person = User.select(User.q.id==data['who']).getOne()
            note = data['newnote']
            if len(note)<1:
                raise redirect(url('/editperson/%s' % person.id))
            
            if person.notes == None or len(person.notes)==0:
                person.notes = [note]
            else:
                n = list(person.notes)
                n.append(note)
                person.notes = n
            
            raise redirect(url('/editperson/%s' % person.id))

        if whichlink[:2] == 'rm':
            person = User.select(User.q.id==data['who']).getOne()
            delete_which_note = int(whichlink[2:])
            n = list(person.notes)
            n.pop(delete_which_note)
            person.notes = n
            
            raise redirect(url('/editperson/%s' % person.id))


        if whichlink == "save":
            # First see if it's creating a new employee or editing an existing one
            person = None
            if data['who'] == "-1":
                person = User(full_name="X",email_address="xx@sfcta.org",user_name="userID",password = "xx")
            else:
                person = User.select(User.q.id==data['who']).getOne()

            # And now update all the person fields
            person.full_name =  data['name']
            person.user_name =  data['login'].lower()
            person.email_address =  str(data['email'])
            try:
                person.adpFileNumber =  int(data['adp'])
            except:
                pass

            # Checkboxes don't show up in "data" if they're not checked :-(
            try:
                person.isManager = data['isManager']
            except:
                person.isManager = False

            try:
                person.isActive = data['isActive']
            except:
                person.isActive = False

            try:
                person.isIntern = data['isIntern']
            except:
                person.isIntern = False

            # Grab dropdown values
            d = data['dept']
            chosenDept = Department.select(Department.q.dept==d).getOne()
            person.dept = chosenDept

            d = data['approver']
            if d !="None":
                chosenApprover = User.select(User.q.full_name==d).getOne()
                person.approver =  chosenApprover
            else:
                person.approver = None

            # Grab Timesheet status values.  Wrappy in "try" in case no timesheets exist.
            try:
                d = data['status']
                empsheets = list(Timesheet.select(Timesheet.q.whose==data['who']).orderBy('-startdate'))

                for sheet in range(len(empsheets)):
                    try:
                        empsheets[sheet].status=TextStatus.index(d[sheet])
                    except:
                        empsheets[sheet].status=TextStatus.index(d)
            except:
                pass

            # Save note, too, if there is one
            note = data['newnote']
            if len(note)>0:
                if person.notes == None or len(person.notes)==0:
                    person.notes = [note]
                else:
                    n = list(person.notes)
                    n.append(note)
                    person.notes = n

            flash("Saved "+person.full_name+".")
            redirect(url('/manageemps'))

    @identity.require(identity.in_group("timesheet-admin"))
    @expose(template="timesheet.templates.crosstabs")
    def crosstabs(self):
        return dict(form=from_to_form)

    @expose()
    @validate(form=from_to_form)
    @validate(validators={'from_date': validators.DateValidator(),'to_date': validators.DateValidator()})
    @identity.require(identity.in_group("timesheet-admin"))
    def buildcrosstabs(self,from_date,to_date):

        # UI reveals the PPE, but we need the startdate which is 14 days earlier
        from_date = from_date - timedelta(days=14)
        to_date =   to_date   - timedelta(days=13)

        sheets = list(Timesheet.select(
                      AND(Timesheet.q.startdate>=from_date,Timesheet.q.startdate<=to_date)))

        if sheets:
            outputCSV = StringIO.StringIO()
            outputCSV.write("Employee,PPE,TS-Status,Type,Code,Description,Hours,Notes\r\n")

            for sheet in sheets:
                if sheet.status<VOID:
                    for entry in Entry.select(Entry.q.sheet==sheet):
                        outputCSV.write('%s,%s\r\n' % (sheet,entry))

            outputCSV.flush()

            # Make CherryPy webserver return a CSV file instead of a webpage
            response.headers['Content-Type'] = "application/x-download"
            response.headers['Content-Disposition'] = 'attachment; filename="timesheet-export.csv"'

            return outputCSV.getvalue()

        raise(redirect('/crosstabs'))


    @expose()
    @identity.require(identity.in_group("timesheet-admin"))
    def pdf(self, stat="sent", startdate=""):

        allsheets = sorted(Timesheet.select(Timesheet.q.startdate==startdate))
        sheets = []

        for s in allsheets:
            if s.status<PAYROLLPREVIEW or s.status==VOID:  # is this right?  Should this be APPROVED?
                if stat=="incomplete": sheets.append(s)
            elif s.status == LOCKED:
                if stat=="sent": sheets.append(s)
            elif stat=="approved":
                sheets.append(s)

        htmlbucket = ""

        for sheet in sheets:
            htmlbucket += self.buildHTMLforTimesheetPDF(sheet.id)
            htmlbucket += "\n <pdf:nextpage /> \n"

        enddate = sheet.startdate + timedelta(days=13)

        outputpdf = StringIO.StringIO()
        pdf = pisa.CreatePDF(htmlbucket, outputpdf, xhtml=True, path="http://timesheets")

        fname = "Timesheets-"+stat+"-"+enddate.strftime("%Y-%b-%d")+".pdf"

        # Make CherryPy webserver return a PDF file instead of a webpage
        response.headers['Content-Type'] = "application/x-download"
        response.headers['Content-Disposition'] = 'attachment; filename='+fname

        # This will return a raw file to the browser, which should ask user
        # to open/save directly
        return outputpdf.getvalue()


    @expose(template="timesheet.templates.start")
    def default(self,*kargs):
        return "Not implemented yet..."

# ---------------------------------------------------------------------------
# Helper functions, not exposed!

    def buildHTMLforTimesheetPDF(self, timesheetnumber):
        """ Build a PDF of a timesheet."""
        ts = Timesheet.select(Timesheet.q.id==timesheetnumber).getOne()
        who = ts.whose
        entries = []
        for charge in LilyOrder:
            entries.extend(Entry.select(AND(Entry.q.sheet==ts,Entry.q.charge==charge)).orderBy("project"))

        # Build data for timesheet:  dates, rowdata, row id's, and column totals.
        dates = self.buildDates(ts.startdate)
        rowdata, coltotals, entry_ids = self.buildReadonlyRows(entries)

        pdftemplate = kid.Template(file='timesheet/templates/pdf.kid',
            person=who, ts=ts, dates=dates, rows=rowdata, entries=entry_ids,coltotals=coltotals)

        htmlstuff = pdftemplate.serialize(encoding='ascii')
        return htmlstuff


    # Build list of dates for a 2-week period
    def buildDates(self, startdate):
        dates = []
        for x in range(14):
            day = startdate + timedelta(days=x)
            dates.append('%d.%d' % (int(day.strftime("%m")), int(day.strftime('%d'))))
        return dates

    # Build data entry form
    def buildRows(self, entries, who):
        rowdata = []
        entry_ids = ""
        rownum = 1
        options = ["Hours","Sick","Vac","Hol","Float","O/T","Jury","Brvmt","cEarn","cUsed"]

        projectlist = self.projectsByDept[who.dept.id]
        rows = list(entries)

        # Be sure project lookups are refreshed
        if self.projectLookupByCode == None:
            self.projectLookupByCode, self.projectLookupByDescription = self.buildProjectLookup()

        # Loop entry rows and create the data entry widgets
        for x in range(len(rows)):
            row = entries[x]

            # this could break if the person has an invalid charge code; e.g. a code to which they
            # are no longer authorized to charge. use the default project if it fails.
            try:
                id = self.projectLookupByCode[row.project[:6]]
            except:
                id = who.dept.defaultProject.id

            prj = Project.select(Project.q.id==id).getOne()

            wCharge = widgets.SingleSelectField("Charge",
                    options=options,
                    default=row.charge)

            wProject= widgets.SingleSelectField("Project",
                    options=projectlist,
                    default=prj.description)

            # build the row of 14 daily textfield entries
            wHours = []

            for day in range(14):
                # Build arrow-key magic:
                top = left = bottom = right = 'undefined'
                if x > 0:
                    top = '\'%d:%d\'' % (x-1,day)
                if day >0:
                    left = '\'%d:%d\'' % (x,day-1)
                if x < len(rows)-1:
                    bottom = '\'%d:%d\'' % (x+1,day)
                if day < 13:
                    right = '\'%d:%d\'' % (x,day+1)
                keymapper="CursorKeyDown(event,%s,%s,%s,%s)" % (top,left,bottom,right)

                wHours.append(widgets.TextField('%d:%d'%(x,day), # name is now row:day
                    default = row.hours[day] or '', # This suppresses 0.0 cells.
                    attrs=dict(size="1", style="width:32px", autocomplete="off",
                               onchange="updatelabels()",
                               onkeydown=keymapper),
                    validator=validators.Number()))

            cellnotes = row.cellnotes

            # create the rowtotal label
            lbl = widgets.Label('lbl',default='')
            rownum += 1

            # and the full datarow with dropdowns, text entries, and total label
            rowdata.append(dict(id=row.id, charge=wCharge, proj=wProject, hours=wHours,
                                cellnotes=cellnotes, tothours=lbl))

            # this is used to have a parseable list of entries on this page
            entry_ids += ';%d' % row.id

        # Trim the trailing semicolon before returning answers.
        entry_ids = entry_ids[1:]

        return rowdata, entry_ids

    # Build data view for read-only (approval) page etc
    def buildReadonlyRows(self, entries):
        rowdata = []
        coltotals = [0 for x in range(15)]
        entry_ids = ""
        grandtotal = 0
        rownum = 1


        # Loop entry rows and create the data view widgets
        for row in entries:
            wCharge = row.charge
            wProject= row.project

            if len(wProject) >= 6:
                try:
                    wProject = str(Project.select(Project.q.code==wProject[:6]).getOne())
                except:
                    continue

            # build the row of 14 daily entries
            wHours = []

            rowtot = 0.0
            for day in range(14):
                hours = row.hours[day]
                if hours > 0:
                    wHours.append(hours)
                    rowtot += hours
                    coltotals[day] += hours
                else:
                    wHours.append(" ")

            # create the rowtotal label
            lbl = rowtot
            coltotals[14] += rowtot
            rownum += 1

            # row-specific notes
#            rownotes = []
#            for day in row.cellnotes:
#                    rownotes.append(day, row.cellnotes[day])

            # and the full datarow with dropdowns, text entries, and total label
            rowdata.append(dict(id=row.id,charge=wCharge,proj=wProject,hours=wHours,
                                tothours=lbl,rownotes=row.cellnotes))
            # this is used to have a parseable list of entries on this page
            entry_ids += ';%d' % row.id

        # Trim the first semicolon before returning answers.
        entry_ids = entry_ids[1:]

        # Remove column totals if there's no data
        for col in range(15):
            if coltotals[col] < 0.01:
                coltotals[col] = ""

        return rowdata, coltotals, entry_ids

    # Build CSV output for ADP
    def buildCSVfile(self, sheets):
        """ Remap the entries in this set of timesheets to the proper ADP format.
        This entails one line per project-code, with multiple columns for each hourly charge type. """

        allrows = []

        for sheet in sheets:
            projectCodes = {}
            for entry in Entry.select(Entry.q.sheet==sheet):
                project = entry.project[:6]  # First six letters are always the proj code

                # Set up basic columns
                charges = {"Co Code":"VEW", "Batch ID":None}
                charges["File #"] = sheet.whose.adpFileNumber
                charges["Temp Dept"] = project

                # Regular and O/T are handled one way by ADP
                if entry.charge == "Hours" or entry.charge == 'O/T':
                    charges[ADPconversion[entry.charge]] = entry.totalhours

                # Comp earned is handled another way by ADP
                elif entry.charge == "cEarn":
                    charges["Memo Code"] = "C"
                    charges["Memo Amount"] = entry.totalhours

                # And everything else is handled yet another way by ADP
                else:
                    charges["Hours 3 Code"] = ADPconversion[entry.charge]
                    charges["Hours 3 Amount"] = entry.totalhours

                allrows.append(charges)

        # Return the list of dictionaries:  entries x project-charges.  Whack.
        return allrows

# ---------------------------------------------------------------------------

    @expose(template="timesheet.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous and identity.was_login_attempted() \
                and not identity.get_identity_errors():
            redirect(tg.url(forward_url or previous_url or '/', kw))

        forward_url = None
        previous_url = request.path

        if identity.was_login_attempted():
            msg = _("Incorrect credentials.  Bad password?")
        elif identity.get_identity_errors():
            msg = _("You must log in to use the timesheet system.")
        else:
            msg = _("Please log in.")
            forward_url = request.headers.get("Referer", "/")

        response.status = 403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
            original_parameters=request.params, forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        redirect("/")

