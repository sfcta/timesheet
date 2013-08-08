<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
    import turbogears as tg
    import datetime
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
<script type="text/javascript" src="/static/sfcta.js"></script>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>View Timesheet - ${person.full_name} - ${ts.startdate}</title>
</head>

<body>

<style>
@page {
    size: letter landscape;
    margin: 1.5cm; margin-top: 1cm; 
}
</style>

<table width="100%">
<tr>
    <td align="left" valign="bottom"><font size="10pt"><b>Timesheet for: ${person.full_name}<br/>${ts.start} - ${ts.enddate}</b></font></td>
    <td align="center" valign="bottom"><font size="10pt">
        <span py:if="ts.status!=0"><b>X</b> Completed &nbsp;&nbsp;</span>
        <span py:if="ts.status>=3">&nbsp;&nbsp;&nbsp;&nbsp;<b>X</b> Approved &nbsp;&nbsp;</span>
    </font></td>
    <td align="right" valign="bottom">
        <img src="${tg.url('/static/images/logo.jpg')}" width="75" height="75"/>
    </td>
</tr>
</table>

<hr/>

        <table width="100%">

        <tr><td></td><td></td><td></td>
        <td align="center"><b>Mo</b></td><td align="center"><b>Tu</b></td><td align="center"><b>We</b></td><td align="center"><b>Th</b></td><td align="center"><b>Fr</b></td><td align="center" bgcolor="#dddddd"><b>Sa</b></td><td align="center" bgcolor="#dddddd"><b>Su</b></td>
        <td align="center"><b>Mo</b></td><td align="center"><b>Tu</b></td><td align="center"><b>We</b></td><td align="center"><b>Th</b></td><td align="center"><b>Fr</b></td><td align="center" bgcolor="#dddddd"><b>Sa</b></td><td align="center" bgcolor="#dddddd"><b>Su</b></td></tr>

        <tr><td><b>Charge&nbsp;&nbsp;</b></td><td width="35%"><b>Project</b></td><td align="right"><b>Totals&nbsp;&nbsp;&nbsp;</b></td>

            <td align="center" py:for="x in range(5)">${dates[x]}</td>
            <td align="center" py:for="x in range(2)" bgcolor="#dddddd">${dates[5+x]}</td>
            <td align="center" py:for="x in range(5)">${dates[7+x]}</td>
            <td align="center" py:for="x in range(2)" bgcolor="#dddddd">${dates[12+x]}</td>
        </tr>
        
        <tr><td>&nbsp;</td></tr>
        <tr py:for="x in range(len(rows))">
            <td><font size="9pt">${rows[x].get("charge")}&nbsp;&nbsp;&nbsp;</font></td>
            <td nowrap="true"><font size="9pt">${rows[x].get("proj")}</font></td>
            <td align="right"><font size="9pt" color="blue"><b>${rows[x].get("tothours")}&nbsp;&nbsp;&nbsp;&nbsp;</b></font></td>

            <td py:for="day in range(5)" align="center">${rows[x].get("hours")[day]}</td>
            <td py:for="day in range(2)" align="center">${rows[x].get("hours")[5+day]}</td>
            <td py:for="day in range(5)" align="center">${rows[x].get("hours")[7+day]}</td>
            <td py:for="day in range(2)" align="center">${rows[x].get("hours")[12+day]}</td>

        </tr>

        <tr><td>&nbsp;</td></tr>
        <tr><td></td><td align="left"><font size="9pt"><b>Total:</b></font></td>
            <td align="right"><font size="9pt" color="blue"><b>${coltotals[14]}&nbsp;&nbsp;&nbsp;&nbsp;</b></font></td>
            <td py:for="x in range(14)" align="center">
                <font size="9pt" color="blue"><b>${coltotals[x]}</b></font>
            </td>
        </tr>
        <tr><td>&nbsp;</td></tr>
        </table>

<hr/>
        
        <table>
        <tr><td><b>Project&nbsp;Notes:</b></td><td colspan="2"><b>Date:&nbsp;</b></td></tr>
        <tr><td>&nbsp;</td></tr>
        
        <span py:for="row in rows">
            <span py:if="row['rownotes']">
                <?python
                    notes = sorted(list(row['rownotes']))
                ?>
                <tr py:for="day in notes">
                    <td valign="top" nowrap="true">${notes.index(day)==0 and row.get('charge') or ''} - ${notes.index(day)==0 and row.get('proj') or ''}&nbsp;&nbsp;&nbsp;&nbsp;</td>
                    <td valign="top" align="left" colspan="2">${dates[day].replace('.','/')}&nbsp;:&nbsp; ${row['rownotes'][day]}</td>
                </tr>
                <tr><td>&nbsp;</td></tr>
            </span>
        </span>
        </table>

        <span py:if="ts.daynotes">
            <b>Daily Notes:</b><br/>
            <span py:for="d in sorted(ts.daynotes.keys())">
                ${dates[d].replace('.','/')}&nbsp;:&nbsp;&nbsp;
                ${ts.daynotes[d]}<br/>
            </span>
        </span>
        
<hr/>
<table><tr>
    <td align="left">(c) ${ts.startdate.strftime('%Y')} San Francisco County Transportation Authority</td>
</tr></table>

</body>
</html>
