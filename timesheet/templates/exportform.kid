<form xmlns:py="http://purl.org/kid/ns#"
    name="${name}" action="${action}" method="${method}" class="tableform" autocomplete="off"
    py:attrs="form_attrs" >
    
    <hr/>
    <table width="100%"><tr>

    <span py:if="len(sheets)>0">
        <td valign="top"><b>Sheets ready for export/closeout:&nbsp;&nbsp;</b><br/>
        (<a href="/pdf/approved/${period}">Print these ${len(sheets)} sheets</a>)<br/><br/>
        <table>
            <tr><td><b>Select&nbsp;&nbsp;</b></td><td><b>Name</b></td></tr>
            <tr py:for="sheet in sheets">
                <td>${sheet[1].display()}</td>
                <td bgcolor='${sheet[0].status==2 and "#ffbb00" or "#ffffff"}'>
                    <a href="/editperson/${sheet[0].whose.id}">${sheet[0].whose.full_name}</a>&nbsp;&nbsp;&nbsp;
                    <font size="-3">
                        <a href="${tg.url('/viewonly/%d' % sheet[0].id)}">view sheet
                        ${sheet[0].status==2 and " (Preview!)" or ""}</a>
                    </font>
                </td>
            </tr>
            <tr><td>&nbsp;</td></tr>

        </table>
        </td>
     </span>
    
     <span py:if="len(already)>0">
            <td valign="top"><b>Sheets already locked/sent to ADP:</b><br/>
                (<a href="/pdf/sent/${period}">Print these ${len(already)} sheets</a>)<br/><br/>
                <table><tr><td><b>Name:</b>&nbsp;&nbsp;</td><td><b>Status:</b></td></tr>
                    <tr py:for="sheet,status in already">
                        <td nowrap="true"><a href="/editperson/${sheet.whose.id}">${sheet.whose.full_name}</a>&nbsp;&nbsp;&nbsp;</td>
                        <td nowrap="true"><a href="/viewonly/${sheet.id}">${status}</a></td>
                    </tr>
                </table>
                <br/>
            </td>

            <td width="100px">&nbsp;</td>
     </span>
            
        <span py:if="len(notyet)>0">
            <td valign="top"><b>Sheets not ready for ADP:</b><br/>
                (<a href="/pdf/incomplete/${period}">Print these ${len(notyet)} sheets</a>)<br/><br/>
                <table><tr><td><b>Name:</b>&nbsp;&nbsp;</td><td><b>Status:</b></td></tr>
                    <tr py:for="sheet,status in notyet" bgcolor="${sheet.status>0 and '#ffff88' or ''}">
                        <td nowrap="true"><a href="/editperson/${sheet.whose.id}">${sheet.whose.full_name}</a>&nbsp;&nbsp;&nbsp;</td>
                        <td nowrap="true"><a href="/viewonly/${sheet.id}">${status}</a></td>
                    </tr>
                </table>
                <br/>
            </td>
        </span>
    </tr></table>

        
    <input type="hidden" name="whichlink" />
</form>
