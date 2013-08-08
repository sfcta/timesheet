<form xmlns:py="http://purl.org/kid/ns#"
    name="${name}" action="${action}" method="${method}" class="tableform" autocomplete="off"
    py:attrs="form_attrs" >

<table>
    <tr><td>Full Name:&nbsp;</td><td>${textfields[0].display()}</td></tr>
    <tr><td>Login:</td><td>${textfields[1].display()}</td></tr>
    <tr><td>Email:</td><td>${textfields[2].display()}</td></tr>
    <tr><td>Department:</td><td>${dept.display()}</td></tr>
    <tr><td>ADP File Number:</td><td>${textfields[3].display()}</td></tr>
    <tr><td>Also Approved By:&nbsp;</td><td>${approver.display()}</td></tr>
    <tr><td>Dept Manager:</td><td>${ismanager.display()}</td></tr>
    <tr><td>Intern:</td><td>${isintern.display()}</td></tr>
    <tr><td>Active:</td><td>${isactive.display()}</td></tr>
</table>

<br/>
<b>Employment History and Notes:</b><br/><br/>

<span class="empnote" py:if="notes != None" py:for="x in range(len(notes))">
    <a class="deleteme" href="javascript:x('rm${x}')">X</a>
    ${notes[x]}<br/><br/>
</span>

${addnote.display()}
<a class="actionbarleft" href="javascript:x('addnote')">Add New Note</a>

<br/><br/><br/><br/>
<b>Timesheets:</b>
<br/>

<table><tr><td>Period:</td><td>Status:</td></tr>
    <tr py:for="ts,status in sheets">
        <td nowrap="true"><a href="${tg.url('/viewonly/%d' % ts.id)}">${ts.start} - ${ts.enddate}&nbsp;&nbsp;&nbsp;</a></td>
        <td>${status.display()}</td>
    </tr>
</table>

<input type="hidden" name="whichlink" />
<input type="hidden" name="who" value="${who}" />

</form>
