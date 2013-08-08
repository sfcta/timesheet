<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
    import datetime,cherrypy
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<script type="text/javascript" src="/static/sfcta.js"></script>
<script language="JavaScript" type="text/javascript">
<!--
function x( selectedtype )
{
  document.form.whichlink.value = selectedtype ;
  document.form.submit() ;
}
-->
</script>

<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Reject Timesheet</title>
</head>

<body>
<?python
    bberry = cherrypy.request.headers['User-Agent'].find('BlackBerry')>=0
?>

<b py:if="not bberry">Reject Timesheet - ${person.full_name}</b>
<b py:if="bberry">Reject Timesheet<br/>${person.full_name}</b>
<br/>

<table width="100%"><tr>
    <td align="left">${ts.start} - ${ts.enddate}</td>
    <td py:if="not bberry" align="right">
        <span py:if="ts.status!=0"><img src="${tg.url('/static/images/ok-small.png')}" alt="X"/> Completed</span>
        <span py:if="ts.status>=3">&nbsp;&nbsp;&nbsp;&nbsp;<img src="${tg.url('/static/images/ok-small.png')}" alt="X"/> Approved</span>
    </td>
</tr></table>

<hr/>

<div py:if="not bberry">
    <table width="100%">
    <tr><td></td><td></td><td></td>
    <td align="center"><b>Mo</b></td><td align="center"><b>Tu</b></td><td align="center"><b>We</b></td><td align="center"><b>Th</b></td><td align="center"><b>Fr</b></td><td align="center" bgcolor="#dddddd"><b>Sa</b></td><td align="center" bgcolor="#dddddd"><b>Su</b></td>
    <td align="center"><b>Mo</b></td><td align="center"><b>Tu</b></td><td align="center"><b>We</b></td><td align="center"><b>Th</b></td><td align="center"><b>Fr</b></td><td align="center" bgcolor="#dddddd"><b>Sa</b></td><td align="center" bgcolor="#dddddd"><b>Su</b></td></tr>

    <tr><td><b>Charge&nbsp;</b></td><td><b>Project</b></td><td align="right"><b>Totals&nbsp;&nbsp;&nbsp;</b></td>

        <td align="center" py:for="x in range(5)">${dates[x]}</td>
        <td align="center" py:for="x in range(2)" bgcolor="#dddddd">${dates[5+x]}</td>
        <td align="center" py:for="x in range(5)">${dates[7+x]}</td>
        <td align="center" py:for="x in range(2)" bgcolor="#dddddd">${dates[12+x]}</td>
    </tr>

    <tr><td>&nbsp;</td></tr>
    <tr py:for="x in range(len(rows))" bgcolor="${('Hours'!=rows[x].get('charge')) and '#ffff88' or ((x%2==0) and '#eeeeee' or '')}">
        <td>${rows[x].get("charge")}</td>
        <td nowrap="true">${rows[x].get("proj")}</td>
        <td align="right"><font color="blue"><b>${rows[x].get("tothours")}&nbsp;&nbsp;&nbsp;&nbsp;</b></font></td>

        <td py:for="day in range(5)" align="center">${rows[x].get("hours")[day]}</td>
        <td py:for="day in range(2)" align="center">${rows[x].get("hours")[5+day]}</td>
        <td py:for="day in range(5)" align="center">${rows[x].get("hours")[7+day]}</td>
        <td py:for="day in range(2)" align="center">${rows[x].get("hours")[12+day]}</td>

    </tr>

    <tr><td>&nbsp;</td></tr>
    <tr><td></td><td align="left"><b>Total:</b></td>
        <td align="right"><font color="blue"><b>${coltotals[14]}&nbsp;&nbsp;&nbsp;&nbsp;</b></font></td>
        <td py:for="x in range(14)" align="center">
            <font color="blue"><b>${coltotals[x]}</b></font>
        </td>
    </tr>
    <tr><td>&nbsp;</td></tr>
    <span py:if="ts.daynotes != None">
        <tr><td></td><td></td><td align="left"><b>Notes:</b></td></tr>
        <tr py:if="len(ts.daynotes)>0">
            <td></td><td></td>
            <td colspan="15">
                <table>
                    <tr py:for="d in sorted(ts.daynotes.keys())"><td></td>
                        <td valign="top" bgcolor="#eeeedd" align="right">${dates[d].replace('.','/')}&nbsp;:&nbsp;&nbsp;</td>
                        <td valign="top" bgcolor="#eeeedd">${ts.daynotes[d]}</td>
                    </tr>
                </table>
            </td>
        </tr>
    </span>
    </table>
    <br/>
</div>

<b>Please explain why this timesheet is being rejected:</b><br/>
This will be emailed to ${person.full_name} along with a request to resubmit the timesheet.<br/>

${form.display()}

<div py:if="not bberry">
<a class="actionbar" href="javascript:x('cancel')">Cancel</a>
<a class="actionbar" href="javascript:x('sendemail')">Reject and Send Back</a>
</div>

<div py:if="bberry">
    Actions:
    <ol>
        <li><b><a href="javascript:x('sendemail')">Reject and Send Back</a></b></li>
        <li><b><a href="javascript:x('cancel')">Cancel</a></b></li>
    </ol>
</div>

</body>
</html>
