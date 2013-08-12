<form xmlns:py="http://purl.org/kid/ns#"
    name="${name}" action="${action}" method="${method}" class="tableform"
    py:attrs="form_attrs" >

    <!-- Fullscreen table -->
    <table width="100%">

    <tr><td></td><td></td><td></td>
    <td align="center">Mo</td><td align="center">Tu</td><td align="center">We</td><td align="center">Th</td><td align="center">Fr</td><td align="center" bgcolor="#bbbbbb">Sa</td><td align="center" bgcolor="#bbbbbb">Su</td>
    <td align="center">Mo</td><td align="center">Tu</td><td align="center">We</td><td align="center">Th</td><td align="center">Fr</td><td align="center" bgcolor="#bbbbbb">Sa</td><td align="center" bgcolor="#bbbbbb">Su</td></tr>

    <tr><td></td><td>Charge</td><td>Project</td>
    <td align="center" py:for="x in range(5)"                  >${dates[x]}</td>
    <td align="center" py:for="x in range(2)" bgcolor="#bbbbbb">${dates[5+x]}</td>
    <td align="center" py:for="x in range(5)"                  >${dates[7+x]}</td>
    <td align="center" py:for="x in range(2)" bgcolor="#bbbbbb">${dates[12+x]}</td>
    <td align="center">&nbsp;<b>Total</b></td></tr>

    <tr py:for="row in rows">
        <td><a href="javascript:x('rm${row.get('id')}')">x</a>&nbsp;</td>
        <td>${row.get("charge").display()}</td>
        <td>${row.get("proj").display()}</td>
        <span py:for="day in range(14)">
            <span py:if="row.get('cellnotes') and day in row.get('cellnotes')">
                <td class="has_note" align="center">
                    ${row.get("hours")[day].display()}
                    <input type="hidden" name="cellnotes" class="bubble_note"
                        value="${ '%d:%d/%s' % (rows.index(row), day, row.get('cellnotes')[day]) }"
                    />
                    <div class="note_tooltip"><span>${row.get('cellnotes')[day]}</span></div>
                </td>
            </span>
            <span py:if="row.get('cellnotes')==None or day not in row.get('cellnotes')">
                <td align="center" bgcolor="${day % 7 >=5 and '#bbbbbb' or ''}">
                        ${row.get("hours")[day].display()}
                </td>
            </span>
        </span>
        <td align="right"><font color="blue">${row.get("tothours").display()}</font></td>
    </tr>

    <tr><td></td>
        <td><a href="javascript:x('addrow')">
        <img border="none" src="/static/images/plus.png" width="14" height="14"/>&nbsp;Row</a></td>
        <td align="right"><b>Total:&nbsp;&nbsp;</b></td>
        <td py:for="tot in coltotals" align="left">
            ${tot.display()}
        </td>
    </tr>

    <tr><td>&nbsp;</td></tr>

    <tr><td colspan="3"></td>
        <td colspan="14">Notes: Double-click on a cell to add notes.</td>
    </tr>

    <tr py:for="day,note in notes">
            <td colspan="2"></td>
            <td align="right" valign="top">${day}:&nbsp;</td>
            <td colspan="14">${note.display()}</td>
    </tr>
    </table>

    <input type="hidden" name="entries" value="${entries}" />
    <input type="hidden" name="whichlink" />
</form>
