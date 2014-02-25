<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
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
<title>Manage Employees</title>
</head>
<body>
<a class="actionbar" href="javascript:x('save')">Save Changes</a>
<a class="actionbar" href="/">Cancel</a>
<br/><b>Edit Employee:</b>
<hr/>

<!-- This outer table container holds admin pieces on the right-nav side. -->
<table width="100%"><tr>
    <td valign="top">

        ${form.display()}
    </td>
    <td py:if="dateform != None and 'timesheet-admin' in tg.identity.groups" align="right" valign="top">
	    <table cellspacing="10" border="1" cellpadding="10" bgcolor="#ffffcc">
            <tr><td valign="top" cellpadding="5">
                <b>&nbsp;Create New Timesheet for this Employee:</b>
                <br/>&nbsp;Pick the END DATE of the pay period (i.e. the SUNDAY of the last week)
                <br/><br/>${dateform.display()}
        	</td></tr><tr><td>&nbsp;</td></tr>
        </table>
    </td>
</tr></table>

<br/>

</body>
</html>

