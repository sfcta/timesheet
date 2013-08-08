<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
    import datetime
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
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
<title>Export Timesheets</title>
</head>
<body>
<a class="actionbar" href="javascript:x('export')">Export Marked Timesheets to ADP</a>
<a class="actionbar" href="javascript:x('lock')">Lock Marked Timesheets</a>
<a class="actionbar" href="javascript:x('cancel')">Back</a>
<b>Export Timesheets</b><br/>${period}<br/>

${form.display()}

<br/>

</body>
</html>
