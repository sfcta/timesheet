<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
    import datetime,cherrypy
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
      py:extends="master.kid">
<head>

<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>

<title py:if="me != None">${person.full_name} - ${ts.startdate} - Approve Timesheet</title>
<title py:if="me == None">View Timesheet - ${person.full_name} - ${ts.startdate}</title>

<STYLE type="text/css">

    .cells {
        empty-cells:show;
        text-align:center;
        font-size:small;
    }

</STYLE>
</head>

<body>
<?python
    bberry = cherrypy.request.headers['User-Agent'].find('BlackBerry')>=0
?>

<span py:if="not bberry" width="100%">
<!-- Actions List for Web -->
    <span py:if="me != None">
        <a class="actionbar" href="${tg.url('/approved/'+str(ts.id)+'/'+me)}">Approve this Timesheet</a>
        <a class="actionbar" href="${tg.url('/rejected/'+str(ts.id)+'/'+me)}">Reject and Send Back</a>
        <a class="actionbar" href="${tg.url('/index')}">Cancel</a>
    </span>

    <span py:if="(me==None) and (review==False)">
        <span py:if="ts.status!=4 or 'timesheet-admin' in tg.identity.groups">
            <a class="actionbar" href="${tg.url('/edit/')+str(ts.id)}">Edit this Timesheet</a>
        </span>
        <a class="actionbar" href="${tg.url('/index')}">Back</a>
    </span>

    <span py:if="(me==None) and (review)">
        <a class="actionbar" href="${tg.url('/submit/')+str(ts.id)}">Submit for Approval</a>
        <a class="actionbar" href="${tg.url('/edit/')+str(ts.id)}">Continue Editing</a>
    </span>
</span>

<b py:if="me != None">Approve Timesheet for: ${person.full_name}</b>
<b py:if="me == None">${person.full_name}</b>
<br/>

<span py:if="bberry"><b>${ts.start} - ${ts.enddate}</b></span>

<!--- Header rows -->
<b>${ts.start} - ${ts.enddate}</b>
<span py:if="ts.status!=0"> &nbsp;&nbsp;&nbsp;&nbsp;<img src="${tg.url('/static/images/ok-small.png')}" alt="X"/>
    <b><font color="#888">Completed</font></b></span>
<span py:if="ts.status>=3"> &nbsp;&nbsp;&nbsp;&nbsp;<img src="${tg.url('/static/images/ok-small.png')}" alt="X"/>
    <font color="#888">
        <b>Approved</b>
        <span py:if="'timesheet-admin' in tg.identity.groups">
                &nbsp;(by ${ts.approvedBy.full_name}<span py:if="ts.approvedOn">, ${ts.approvedOn.strftime('%b %d, %Y')}</span>)
        </span>
    </font>
</span>

<hr/>

<!-- Standard Charges Table -->
        <table py:if="not bberry" width="100%">
        <tr class="cells">
            <td></td><td></td><td></td>
            <td align="center"><b>Mo</b></td><td align="center"><b>Tu</b></td><td align="center"><b>We</b></td><td align="center"><b>Th</b></td><td align="center"><b>Fr</b></td><td align="center" bgcolor="#dddddd"><b>Sa</b></td><td align="center" bgcolor="#dddddd"><b>Su</b></td>
            <td align="center"><b>Mo</b></td><td align="center"><b>Tu</b></td><td align="center"><b>We</b></td><td align="center"><b>Th</b></td><td align="center"><b>Fr</b></td><td align="center" bgcolor="#dddddd"><b>Sa</b></td><td align="center" bgcolor="#dddddd"><b>Su</b></td>
        </tr>

        <tr><td><b>Charge&nbsp;</b></td><td><b>Project</b></td><td align="right"><b>Totals&nbsp;&nbsp;&nbsp;</b></td>
            <td align="center" py:for="x in range(14)" bgcolor="${x % 7 >=5 and '#dddddd' or '#ffffff'}">${dates[x]}</td>
        </tr>

        <tr><td>&nbsp;</td></tr>
        <span py:for="row in rows">
            <?python rownotes = row.get("rownotes") ?>
            <tr bgcolor="${('Hours'!=row.get('charge')) and '#ffff88' or ((rows.index(row)%2==0) and '#eeeeee' or '')}">
                <td>${row.get("charge")}</td>
                <td nowrap="true">${row.get("proj")}</td>
                <td align="right"><font color="blue"><b>${row.get("tothours")}&nbsp;&nbsp;&nbsp;&nbsp;</b></font></td>
                <td py:for="day in range(14)" align="center" bgcolor="${rownotes and (day in rownotes) and '#a0ffa0' or ''}" title="${rownotes and (day in rownotes) and rownotes[day] or ''}">
                    ${row.get("hours")[day]}
                </td>
            </tr>
        </span>

        <tr><td>&nbsp;</td></tr>
        <tr><td></td><td align="left"><b>Total:</b></td>
            <td align="right"><font color="blue"><b>${coltotals[14]}&nbsp;&nbsp;&nbsp;&nbsp;</b></font></td>
            <td py:for="x in range(14)" align="center"><font color="blue"><b>${coltotals[x]}</b></font>
            </td>
        </tr>
        <tr><td>&nbsp;</td></tr>
        </table>

        <!-- BlackBerry Charges Table -->
        <table py:if="bberry" width="100%">

        <tr><td colspan="7"><b>Summary: <font color="blue">${coltotals[14]} hours.</font></b></td></tr>
        <tr class="cells"><td>M</td><td>T</td><td>W</td><td>R</td><td>F</td><td>S</td><td>S</td></tr>
        <tr class="cells">
            <td py:for="day in range(5)" style="background-color:palegoldenrod;">&nbsp;${coltotals[day]}</td>
            <td py:for="day in range(2)" style="background-color:moccasin;">&nbsp;${coltotals[5+day]}</td>
        </tr>
        <tr class="cells">
            <td py:for="day in range(5)" style="background-color:palegoldenrod;">&nbsp;${coltotals[7+day]}</td>
            <td py:for="day in range(2)" style="background-color:moccasin;">&nbsp;${coltotals[12+day]}</td>
        </tr>

        <tr><td colspan="7">&nbsp;</td></tr>
        <tr><td colspan="7"><b>Details:</b></td></tr>
        <tr><td colspan="7">&nbsp;</td></tr>

        <span py:for="row in rows">
            <tr bgcolor="${'Hours'!=row.get('charge') and '#ffff88' or '#eeeeee'}">
                <td colspan="7">${row.get("charge")!='Hours' and row.get("charge") or '' } ${row.get("proj")}</td></tr>
            <tr class="cells">
                <td py:for="day in range(5)" style="background-color:palegoldenrod;">&nbsp;${row.get("hours")[day]}</td>
                <td py:for="day in range(2)" style="background-color:moccasin;">&nbsp;${row.get("hours")[5+day]}</td>
            </tr>
            <tr class="cells">
                <td py:for="day in range(5)" style="background-color:palegoldenrod;">&nbsp;${row.get("hours")[7+day]}</td>
                <td py:for="day in range(2)" style="background-color:moccasin;">&nbsp;${row.get("hours")[12+day]}</td>
            </tr>
            <tr>
                <td colspan="7" align="right"><font color="blue">Total ${row.get("charge")}: ${row.get("tothours")}</font></td></tr>
            <tr>
                <td colspan="7">&nbsp;</td></tr>
        </span>
        </table>

        <hr/>

        <!-- Standard Project Notes Table -->
        <table py:if="not bberry">
        <tr><td colspan="2"><b>Project Notes:</b></td><td><b>Date:&nbsp;&nbsp;</b></td><td><b>Note:</b></td></tr>
        <tr><td>&nbsp;</td></tr>

        <span py:for="row in rows">
            <span py:if="row['rownotes']">
                <?python
                    notes = list(row['rownotes'])
                    notes.sort()
                ?>
                <tr py:for="day in notes">
                    <td valign="top">${notes.index(day)==0 and row.get('charge') or ''}&nbsp;&nbsp;</td>
                    <td nowrap="${bberry and 'false' or 'true'}" valign="top">${notes.index(day)==0 and row.get('proj') or ''}&nbsp;&nbsp;&nbsp;&nbsp;</td>
                    <td valign="top" align="left" bgcolor='#a0ffa0'>${dates[day].replace('.','/')}</td>
                    <td valign="top" align="left">${row['rownotes'][day]}</td>
                </tr>
                <tr><td>&nbsp;</td></tr>
            </span>
        </span>
        </table>

        <!-- BlackBerry Project Notes Table -->
        <table py:if="bberry">
        <tr><td colspan="3"><b>Project Notes:</b></td></tr>
        <tr><td colspan="3">&nbsp;</td></tr>

        <span py:for="row in rows">
            <span py:if="row['rownotes']">
                <?python
                    notes = list(row['rownotes'])
                    notes.sort()
                ?>
                <tr>
                    <td colspan="3" style="background-color:palegoldenrod;">${row.get('charge')} ${row.get('proj')}</td>
                </tr>
                <tr class="cell" py:for="day in notes">
                    <td valign="top" align="left">${dates[day].replace('.','/')}:</td>
                    <td colspan="2" valign="top" align="left">${row['rownotes'][day]}</td>
                </tr>
                <tr><td colspan="3">&nbsp;</td></tr>
            </span>
        </span>
        </table>

        <!-- Day Notes Table -->
        <table py:if="ts.daynotes">
            <tr><td align="left" colspan="2"><b>Daily Notes:</b></td></tr>
            <tr py:if="len(ts.daynotes)>0">
                <td colspan="15">
                    <table>
                        <tr py:for="d in sorted(ts.daynotes.keys())"><td></td>
                            <td valign="top" align="right">${dates[d].replace('.','/')}&nbsp;:&nbsp;&nbsp;</td>
                            <td valign="top">${ts.daynotes[d]}</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        <br/>

<!-- Actions List for BBerry -->
<div py:if="me != None">
    <span py:if="bberry">
        Actions:
        <ol>
        <li><a href="${tg.url('/approved/'+str(ts.id)+'/'+me)}">Approve this Timesheet</a></li>
        <li><a href="${tg.url('/rejected/'+str(ts.id)+'/'+me)}">Reject and Send Back</a></li>
        <li><a href="${tg.url('/index')}">Cancel</a></li>
        </ol>
    </span>
</div>

</body>
</html>
