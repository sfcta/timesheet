<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
    import datetime
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Export Timesheets to ADP</title>
</head>
<body>
<a class="actionbar" href="/">Back</a>
<br/><b>Export Timesheets</b><br/>
<hr/>
<p>Choose a time period from the list below:</p>

<table borderwidth="0" cellspacing="1">
    <tr py:for="period,howmany in periods.iteritems()">
        <td nowrap="true"><a href="${tg.url('/exportts/'+str(period))}">
            &nbsp;&nbsp;&nbsp;&nbsp;${period.strftime('%b %d')} - ${(period + datetime.timedelta(days=13)).strftime('%b %d, %Y')}&nbsp;&nbsp;&nbsp;</a></td>
        <td nowrap="true">${howmany} open timesheets</td>
    </tr>
</table>
<br/>

<table borderwidth="0" cellspacing="1">
    <tr py:for="period in closedperiods">
        <td nowrap="true"><a href="${tg.url('/exportts/'+str(period))}">
            &nbsp;&nbsp;&nbsp;&nbsp;${period.strftime('%b %d')} - ${(period + datetime.timedelta(days=13)).strftime('%b %d, %Y')}&nbsp;&nbsp;&nbsp;</a></td>
    </tr>
</table>
<br/>

</body>
</html>
