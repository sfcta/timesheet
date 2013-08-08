<form xmlns:py="http://purl.org/kid/ns#"
    name="${name}" action="${action}" method="${method}" class="tableform" autocomplete="off"
    py:attrs="form_attrs" >
<table>
    <tr><td align="left">New:</td>
        <td border="2">${addproj['code'].display()}</td>
        <td>${addproj['desc'].display()}</td>
    </tr><tr>
        <td colspan="3">
            <a class="actionbar" href="javascript:x('addnew')">Create Project</a>
        </td>
    </tr>
    <tr><td colspan="10"><br/><hr/></td></tr>
    
    <tr><td align="left" colspan="3"><b>Edit Projects:</b></td><td colspan="3"><b>Limited To Departments:</b></td>
    </tr><tr>
        <td><b>Hide&nbsp;&nbsp;</b></td> <td><b>Code</b></td> <td nowrap="true"><b>Description</b></td>
        <td py:for="d in depts" align="center" width="10%" valign="bottom">${d}</td>
    </tr>
    <span py:for="x in range(len(rows))">
        <tr py:if="x%2==0" bgcolor="#dddddd">
            <!-- 0:hide; 1:code; 2:description; 3:limits -->
            <td bgcolor="#ffffff">${rows[x][0].display()}</td>
            <td bgcolor="#ffffff">${rows[x][1]}&nbsp;</td>
            <td>${rows[x][2].display()}</td>
            <td py:for="cbox in rows[x][3]" align="center">
                ${cbox.display()}
            </td>
        </tr>
        <tr py:if="x%2==1">
            <td>${rows[x][0].display()}</td>
            <td>${rows[x][1]}&nbsp;</td>
            <td>${rows[x][2].display()}</td>
            <td py:for="cbox in rows[x][3]" align="center">
                ${cbox.display()}
            </td>
        </tr>
    </span>
</table>

<input type="hidden" name="whichlink" />
</form>
