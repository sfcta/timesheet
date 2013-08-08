<form xmlns:py="http://purl.org/kid/ns#"
        name="${name}" action="${action}" method="${method}" class="tableform" autocomplete="off"
        py:attrs="form_attrs" >
        
        ${note.display()}

    <input type="hidden" name="whichlink" />
    <input type="hidden" name="to" value="${person}" />
    <input type="hidden" name="from" value="${me}" />
    <input type="hidden" name="ts" value="${ts}" />
    
</form>