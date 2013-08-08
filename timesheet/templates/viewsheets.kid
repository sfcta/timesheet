<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
    import datetime,cherrypy
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="master.kid">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Timesheets - ${person.full_name}</title>
</head>
<body>
<?python
    bberry = cherrypy.request.headers['User-Agent'].find('BlackBerry')>=0
?>

<b>Welcome, ${person.full_name}</b>&nbsp;&nbsp; - &nbsp;&nbsp;<a href="${tg.url('/logout')}">Logout</a>
<br/>
<hr/>

<!-- This outer table container holds admin pieces on the right-nav side. -->
<table width="100%" cellspacing="5"><tr>
<td valign="top">

    <!-- My Timesheets -->
	<table width="100%">
	<tr><td py:if="not bberry" valign="top" align="left"><img src="${tg.url('/static/images/pencil.jpg')}" alt="X"/></td>
    <td py:if="not bberry">&nbsp;&nbsp;</td>
	<td align="left" nowrap="true">
	    <b>My Current Timesheets</b>
	    <br/>
	    <br/>
	    <table borderwidth="0" cellpadding="1">
	    <tr><th nowrap="true">Timesheet Period:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>&nbsp;</th><th>Complete</th><th>&nbsp;&nbsp;Approved&nbsp;&nbsp;</th><th align="right">&nbsp;&nbsp;Hours</th></tr>
	    <tr py:for="timesheet in sheets">
            <td py:if="timesheet.status==0" nowrap="true"><a href="${tg.url('/edit/'+str(timesheet.id))}">${timesheet.start} - ${timesheet.enddate}</a></td>
            <td py:if="timesheet.status>=1" nowrap="true"><a href="${tg.url('/viewonly/'+str(timesheet.id))}">${timesheet.start} - ${timesheet.enddate}</a></td>
            <td width="10%">&nbsp;</td>

            <td py:if="timesheet.status==0" align="center">--</td>
            <td py:if="timesheet.status>=1" align="center"><img src="${tg.url('/static/images/ok-small.png')}" alt="X"/></td>

            <td py:if="timesheet.approvedBy == None" align="center">--</td>
            <td py:if="timesheet.approvedBy != None" align="center"><img src="${tg.url('/static/images/ok-small.png')}" alt="X"/></td>

            <td align="right">${timesheet.totalhours}</td>
	    </tr>
	    <tr><td>&nbsp;</td></tr>
	    </table>
	</td>
	<td width="100%">&nbsp;</td>
	</tr></table>
	<br/>
	<hr/>

    <!-- Department Timesheets -->
	<span py:if="len(managerview)>0">
	<table width="100%">
	<tr><td py:if="not bberry" valign="top" align="left"><img src="${tg.url('/static/images/heads.png')}" alt="X"/></td>
    <td py:if="not bberry">&nbsp;&nbsp;</td>
	<td align="left" nowrap="true">
	    <b>${person.dept} Staff:&nbsp;&nbsp;Current Timesheets</b>
	    <br/>
	    <br/>
        <!-- Fullscreen Table -->
	    <table py:if="not bberry" borderwidth="0" cellpadding="1">
	    <tr><th nowrap="true">Period:&nbsp;</th><th nowrap="true">&nbsp;&nbsp;Who:</th><th>&nbsp;</th><th>Complete</th><th>&nbsp;&nbsp;Approved&nbsp;&nbsp;</th><th align="right">&nbsp;&nbsp;Hours</th></tr>
	    <span py:for="pd in managerview">
		<tr py:for="sheet in pd">
		    <td nowrap="true" py:content="pd.index(sheet)==0 and (sheet.start + ' - ' + sheet.enddate) or '' "></td>

		    <td py:if="sheet.status==1" nowrap="true"><a href="${tg.url('/approve/'+str(sheet.id)+'/'+str(person.id))}">
		        &nbsp;&nbsp;${sheet.whose.full_name}&nbsp;&nbsp;&nbsp;</a></td>
		    <td py:if="sheet.status!=1" nowrap="true"><a href="${tg.url('/viewonly/'+str(sheet.id))}">
		        &nbsp;&nbsp;${sheet.whose.full_name}&nbsp;&nbsp;&nbsp;</a></td>

		    <td width="10%">&nbsp;</td>
		    <td py:if="sheet.status==0" align="center"> -- </td>
		    <td py:if="sheet.status>=1" align="center"><img src="${tg.url('/static/images/ok-small.png')}" alt="X"/></td>

		    <td py:if="sheet.approvedBy == None" align="center"> -- </td>
		    <td py:if="sheet.approvedBy != None" align="center"><img src="${tg.url('/static/images/ok-small.png')}" alt="X"/></td>

            <td align="right">${sheet.totalhours}</td>
		</tr>
		<tr><td>&nbsp;</td></tr>
	    </span>
	    </table>

        <!-- BlackBerry Table -->
   	    <table py:if="bberry" borderwidth="0" cellpadding="1">
	    <span py:for="pd in managerview">
            <tr><td colspan="3">${pd[0].start} - ${pd[0].enddate}</td></tr>
            <tr py:for="sheet in pd">
                <td py:if="sheet.status==1" nowrap="true"><a href="${tg.url('/approve/'+str(sheet.id)+'/'+str(person.id))}">
                    ${sheet.whose.full_name}</a></td>
                <td py:if="sheet.status!=1" nowrap="true"><a href="${tg.url('/viewonly/'+str(sheet.id))}">
                    ${sheet.whose.full_name}</a></td>

                <td py:if="sheet.status==0" align="center"> -- </td>
                <td py:if="sheet.status>=1" align="center"><img src="${tg.url('/static/images/ok-small.png')}" alt="X"/></td>

                <td py:if="sheet.approvedBy == None" align="center"> -- </td>
                <td py:if="sheet.approvedBy != None" align="center"><img src="${tg.url('/static/images/ok-small.png')}" alt="X"/></td>
            </tr>
		<tr><td>&nbsp;</td></tr>
	    </span>
	    </table>

	</td>
	<td width="100%">&nbsp;</td>
	</tr></table>
	<br/>
	<hr/>
	</span>


    <!-- Sheets Needing Approval -->
    <span py:if="len(mgrapps)+len(staffapps)+len(internapps)>0">
	<table width="100%">
	<tr><td valign="top" py:if="not bberry"><img src="${tg.url('/static/images/attn.jpg')}" alt="X"/></td>
    <td py:if="not bberry">&nbsp;&nbsp;</td>
	<td width="100%">
	    <b>Timesheets&nbsp;Needing&nbsp;Approval</b>
	    <br/><br/>

        <!-- Fullscreen -->
	    <table py:if="not bberry" borderwidth="0" cellpadding="1">

	    <tr py:if="len(mgrapps)>0"><td>Managers:</td><td>&nbsp;</td><td>Period</td><td>&nbsp;</td><td>Dept</td></tr>
	    <tr py:for="ts in mgrapps">
		    <td nowrap="true">&nbsp;&nbsp;&nbsp;<a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.whose.full_name}</a></td>
		    <td width="10%"></td>
		    <td nowrap="true"><a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.start} - ${ts.enddate}</a></td>
		    <td width="10%"></td>
		    <td nowrap="true">${ts.whose.dept}</td>
	    </tr>
	    <tr py:if="len(mgrapps)>0"><td>&nbsp;</td></tr>

	    <tr py:if="len(staffapps)>0"><td>Staff:</td><td>&nbsp;</td><td>Period</td><td>&nbsp;</td><td>Dept</td></tr>
	    <tr py:for="ts in staffapps">
		    <td nowrap="true">&nbsp;&nbsp;&nbsp;<a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.whose.full_name}</a></td>
		    <td width="10%"></td>
		    <td nowrap="true"><a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.start} - ${ts.enddate}</a></td>
		    <td width="10%"></td>
		    <td nowrap="true">${ts.whose.dept}</td>
	    </tr>
	    <tr py:if="len(staffapps)>0"><td>&nbsp;</td></tr>

	    <tr py:if="len(internapps)>0"><td>Interns:</td><td>&nbsp;</td><td>Period</td><td>&nbsp;</td><td>Dept</td></tr>
	    <tr py:for="ts in internapps">
		    <td nowrap="true">&nbsp;&nbsp;&nbsp;<a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.whose.full_name}</a></td>
		    <td width="10%"></td>
		    <td nowrap="true"><a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.start} - ${ts.enddate}</a></td>
		    <td width="10%"></td>
		    <td nowrap="true">${ts.whose.dept}</td>
	    </tr>
	    </table>

        <!-- BlackBerry -->
	    <table py:if="bberry" borderwidth="0" width="100%">

	    <tr py:if="len(mgrapps)>0"><td>Managers:</td></tr>
	    <span py:for="ts in mgrapps">
		    <tr><td nowrap="true"><a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.whose.full_name}</a></td></tr>
		    <tr width="100%"><td width="100%" align="right" nowrap="true">${ts.start} - ${ts.enddate}</td></tr>
	    </span>
	    <tr py:if="len(mgrapps)>0"><td>&nbsp;</td></tr>

	    <tr py:if="len(staffapps)>0"><td>Staff:</td></tr>
	    <span py:for="ts in staffapps">
		    <tr><td nowrap="true"><a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.whose.full_name}</a></td></tr>
		    <tr width="100%"><td width="100%" align="right" nowrap="true">${ts.start} - ${ts.enddate}</td></tr>
	    </span>
	    <tr py:if="len(staffapps)>0"><td>&nbsp;</td></tr>

	    <tr py:if="len(internapps)>0"><td>Interns:</td></tr>
	    <span py:for="ts in internapps">
		    <tr><td nowrap="true"><a href="${tg.url('/approve/'+str(ts.id)+'/'+str(person.id))}">${ts.whose.full_name}</a></td></tr>
		    <tr width="100%"><td width="100%" align="right" nowrap="true">${ts.start} - ${ts.enddate}</td></tr>
	    </span>
	    </table>

	</td><td width="100%">&nbsp;</td>
	</tr></table>
  	<br/>
	<hr/>
	</span>

    <!-- Archived Timesheets -->
	<table width="100%">
	<tr><td  py:if="not bberry" valign="top"><img src="${tg.url('/static/images/search.jpg')}" alt="X"/></td>
    <td py:if="not bberry">&nbsp;&nbsp;</td>
	<td width="100%">
	    <b>Archived&nbsp;Timesheets</b><br/>Pay period ending:<br/><br/>

	    <table borderwidth="0" cellpadding="1">
        <tr py:for="year in sorted(oldsheets,reverse=True)">
            <td valign="top"><b>${str(year)}&nbsp;&nbsp;&nbsp;&nbsp;</b></td>
            <td valign="top">
                <span py:for="timesheet in oldsheets[year]"><a href="${tg.url('/viewonly/'+str(timesheet.id))}">${timesheet.enddatewithoutyear}</a> - </span>
            <br/><br/>
            </td>
	    </tr></table>
	</td><td width="100%">&nbsp;</td>
	</tr></table>

</td>

<!-- Admin Panel -->
<td py:if="(not bberry) and 'timesheet-admin' in tg.identity.groups" align="right" valign="top">
	<table cellspacing="10" border="1" cellpadding="10" bgcolor="#ffffcc">
        <tr><td valign="top" cellpadding="5">
		    <b><font size="+1">Administrator&nbsp;Panel</font></b><br/><br/>
		    <b>Biweekly Payroll Tasks:</b><br/>
		    <a href="${tg.url('/addset')}">Create&nbsp;timesheet&nbsp;set&nbsp;for&nbsp;active&nbsp;employees</a>
		    <br/><a href="${tg.url('/export')}">Export/Print completed timesheets</a>

            <br/><br/>
		    <b>Reporting:</b>
            <br/><a href="${tg.url('/crosstabs')}">Create Excel Table for Reports</a>

		    <br/><br/>
		    <b>Timesheet System Admin:</b>
            <br/><a href="${tg.url('/manageemps')}">Manage Employee List</a>
            <br/><a href="${tg.url('/editperson')}">Add New Employee</a>
		    <br/><a href="${tg.url('/editprojects')}">Edit Project Categories</a>

            <br/>
    	</td></tr><tr><td>&nbsp;</td></tr>
    </table>
</td></tr></table>

<br/><hr/>
</body>
</html>

