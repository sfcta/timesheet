<form xmlns:py="http://purl.org/kid/ns#"
    name="${name}" action="${action}" method="${method}" class="tableform" autocomplete="off"
    py:attrs="form_attrs" >

<?python
    import datetime,cherrypy
    bberry = cherrypy.request.headers['User-Agent'].find('BlackBerry')>=0
?>
    <!-- Fullscreen table -->
    <table py:if="not bberry" width="100%">

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
        <td colspan="14">Notes: Click on a date, or double-click on a cell, to add notes.</td>
    </tr>

    <tr py:for="day,note in notes">
            <td colspan="2"></td>
            <td align="right" valign="top">${day}:&nbsp;</td>
            <td colspan="14">${note.display()}</td>
    </tr>
    </table>

    <!-- BlackBerry table -->
    <table py:if="bberry" width="100%">

    <tr><td align="center">Mo</td><td align="center">Tu</td><td align="center">We</td><td align="center">Th</td><td align="center">Fr</td><td align="center" bgcolor="#bbbbbb">Sa</td><td align="center" bgcolor="#bbbbbb">Su</td><td></td></tr>

    <tr><td>&nbsp;</td></tr>

    <span py:for="row in rows">
        <tr><td colspan="7"><a href="javascript:x('rm${row.get('id')}')">x</a>&nbsp;${row.get("charge").display()}</td></tr>
        <tr><td colspan="7">${row.get("proj").display()}</td></tr>

        <tr>
            <span py:for="day in range(7)">
                <span py:if="row.get('cellnotes') and day in row.get('cellnotes')">
                    <td class="has_note" align="center">
                        ${row.get("hours")[day].display()}
                        <input type="hidden" name="cellnotes" class="bubble_note"
                            value="${ '%d:%d/%s' % (rows.index(row), day, row.get('cellnotes')[day]) }"
                        />
                        <!-- <div class="note_tooltip"><span>${row.get('cellnotes')[day]}</span></div> -->
                    </td>
                </span>
                <span py:if="row.get('cellnotes')==None or day not in row.get('cellnotes')">
                    <td align="center" bgcolor="${day % 7 >=5 and '#bbbbbb' or ''}">
                            ${row.get("hours")[day].display()}
                    </td>
                </span>
            </span>
        </tr>
        <tr>
            <span py:for="day in range(7)">
                <span py:if="row.get('cellnotes') and day+7 in row.get('cellnotes')">
                    <td class="has_note" align="center">
                        ${row.get("hours")[day+7].display()}
                        <input type="hidden" name="cellnotes" class="bubble_note"
                            value="${ '%d:%d/%s' % (rows.index(row), day+7, row.get('cellnotes')[day+7]) }"
                        />
                        <div class="note_tooltip"><span>${row.get('cellnotes')[day+7]}</span></div>
                    </td>
                </span>
                <span py:if="row.get('cellnotes')==None or day+7 not in row.get('cellnotes')">
                    <td align="center" bgcolor="${(day+7) % 7 >=5 and '#bbbbbb' or ''}">
                            ${row.get("hours")[day+7].display()}
                    </td>
                </span>
            </span>
        </tr>
        <tr><td colspan="7" align="right"><font color="blue">Total: ${row.get("tothours").display()}</font></td></tr>
        <tr><td>&nbsp;</td></tr>
    </span>

    <tr>
        <td colspan="7">
            <img border="none" src="/static/images/plus.png" width="14" height="14"/>&nbsp;
            <a href="javascript:x('addrow')">Add Row</a>
        </td>
    </tr>
    <tr><td>&nbsp;</td></tr>

    <tr><td colspan="7"><b>Summary Totals:</b></td></tr>
    <tr><td py:for="tot in range(7)" align="center" style="background-color:palegoldenrod;">&nbsp;${coltotals[tot].display()}</td></tr>
    <tr><td py:for="tot in range(7)" align="center" style="background-color:palegoldenrod;">&nbsp;${coltotals[tot+7].display()}</td></tr>
    <tr><td>&nbsp;</td></tr>

    <tr py:for="day,note in notes">
            <td valign="top">${day}:&nbsp;</td>
            <td colspan="6">${note.display()}</td>
    </tr>
    </table>

    <span py:if="bberry">
        Actions:
        <ol>
            <li><a href="javascript:x('save')">Save/Close</a></li>
            <li><a href="javascript:x('review')">Review and Submit</a></li>
        </ol>
    </span>

    <input type="hidden" name="entries" value="${entries}" />
    <input type="hidden" name="whichlink" />
</form>
