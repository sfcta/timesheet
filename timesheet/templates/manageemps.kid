<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Manage Employees</title>
</head>
<body>
<a class="actionbar" href="${tg.url('/editperson')}">Add new employee</a>
<a class="actionbar" href="${tg.url('/index')}">Back</a>
<br/><b>Active Employees:</b>
<hr/>

<ul>
    <li py:for="person in active">
        <a href="${tg.url('/editperson/'+str(person.id))}">${person.full_name}</a>
</li>
</ul>

<br/><br/>
<b>Inactive Employees:</b>
<hr/>
<table width="80%"><tr><td width="80%" cellspacing="10px">
<span py:for="person in inactive">
       <a href="${tg.url('/editperson/'+str(person.id))}">${person.full_name}</a>
       -&nbsp;
</span>
</td></tr></table>

<br/>

</body>
</html>

