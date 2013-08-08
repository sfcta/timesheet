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
<title>Manage Project Codes</title>
</head>

<body>
<a class="actionbar" href="javascript:x('save')">Save Changes</a>
<a class="actionbar" href="javascript:x('cancel')">Back</a>
<br/><b>Project Codes:</b>
<hr/>
<br/>
${form.display()}

</body>
</html>
