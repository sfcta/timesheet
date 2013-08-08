
function updatelabels() {
    var the_inputs = document.getElementsByTagName("input");
    var the_textfields = new Array();
    var the_labels = new Array();
    var coltotals = new Array();

    for (var n=0; n<the_inputs.length; n++) {
        if (the_inputs[n].size == "1") {
            the_textfields[the_textfields.length] = document.getElementsByTagName("input")[n];
        }
    }

    /* experimental -- i think this should grab the hour-entries on the read-only form */
    the_labels = document.getElementsByTagName("form_hours");
    if (the_labels.length>0) {
        the_textfields = the_labels;
    }

    for (var d=0; d<15; d++) {
        coltotals[d] = 0;
    }

    /* Row and col totals*/
    var rows = the_textfields.length / 14;
    for (var r=0; r<rows; r++) {
        var color = "green"
        var rowsum = parseFloat('0.0');
        for (var d=0; d<14; d++) {
            var entry = the_textfields[r*14+d].value;
            if (entry.length>0) {
                var tval = parseFloat(the_textfields[r*14 + d].value);
                rowsum += tval;
                coltotals[d] += tval;
                coltotals[14] += tval;
            }
        }
        if (isNaN(rowsum))  {
            rowsum = "ERR";
            color = "red"
        }
        if (rowsum==0) rowsum="";

        var ll = document.getElementsByTagName("label")[r];
        ll.innerHTML = rowsum; //.toFixed(2);
        ll.style.color = color;
    }

    /* Update columns */
    for (var d=0; d<15; d++) {
        var color = "green";
        if (coltotals[d] < 8) color = "blue";
        if (coltotals[d] > 8 && d<14) color = "purple";
        if (isNaN(coltotals[d])) {
            coltotals[d] = "ERR";
            color = "red";
        }

        if (coltotals[d]==0) coltotals[d]="";
        var ll = document.getElementsByTagName("label")[rows+d];
        ll.innerHTML = "&nbsp;" + coltotals[d]; //.toFixed(2);
        ll.style.color = color;
        if (d==14) {
            ll.style.fontWeight="bold";
            ll.innerHTML = "&nbsp;"+coltotals[d];
        }
    }
}


//rounds the input number to the desired precision
//and returns the rounded number

function roundToPrecision(inputNum, desiredPrecision){
  var precisionGuide = Math.pow(10, desiredPrecision);
  return( Math.round(inputNum * precisionGuide) / precisionGuide );
}

//converts the input number into a string and adds zeroes
//until the desired precision is reached and then
//returns the new string

function addZeroesToPrecision(inputNum, desiredPrecision){
  var numString = inputNum + "";
  var afterDecimalString = numString.substring(numString.search(/\./) + 1);
  while (afterDecimalString.length < desiredPrecision) {
    afterDecimalString += "0";
    numString += "0";
  }
  return(numString);
}

addLoadEvent(updatelabels);

function addBubble () {
  var previous_note_text = '';
  previous_note = findChildElements($(this).parentNode, ['input[type="hidden"]']);
  if (previous_note.length >0) {
    previous_note_text = previous_note[0].value.substring(1+previous_note[0].value.indexOf("/"));
  }
  forEach(findChildElements($(this).parentNode, ['input[type="hidden"]']), removeElement);
  forEach(findChildElements($(this).parentNode, ['div.note_tooltip']), removeElement);
  var newBubble = DIV({'class': 'entry_bubble'}, DIV({'class': 'bubble_pointy'}, DIV({'class': 'bubble_pointy-inner'}, null)), DIV({'class': 'main_bubble'}, SPAN('Note:'), TEXTAREA({'id':'bubble-textarea'}, previous_note_text)));
  var textarea = findChildElements($(newBubble), ['textarea'])[0];
  connect(textarea, 'onblur', saveAndDestroyBubble);
  insertSiblingNodesAfter($(this), newBubble);
  textarea.focus();
}

function saveAndDestroyBubble() {
    row = $(this).parentNode.parentNode.parentNode;
    inputField = findChildElements($(row), ['input[type="text"]'])[0]
    if ($(this).value.length > 0) {
        appendChildNodes(row, INPUT({
            'type': 'hidden',
            'name': 'cellnotes',
            'class': 'note',
            'value': inputField.name+'/'+$(this).value
        }));
        appendChildNodes(row, DIV({
            'class': 'note_tooltip'
        }, SPAN($(this).value)));
        addElementClass(row, 'has_note');
    } else {
        removeElementClass(row, 'has_note');
    }
    forEach(findChildElements($(row), ['div.entry_bubble']), removeElement);
}

// Copyright (C) 2008 www.cryer.co.uk
// Script is free to use provided this copyright header is included.
function CursorKeyDown(e,topName,leftName,bottomName,rightName)
{
  if (!e) e=window.event;
  var selectName;
  switch(e.keyCode)
  {
  case 37:
    // Key left.
    selectName = leftName;
    break;
  case 38:
    // Key up.
    selectName = topName;
    break;
  case 39:
    // Key right.
    selectName = rightName;
    break;
  case 40:
    // Key down.
    selectName = bottomName;
    break;
  }
  if (!selectName) return;
  var controls = document.getElementsByName(selectName);
  if (!controls) return;
  if (controls.length != 1) return;
  controls[0].focus();
}



addLoadEvent(function () {
  forEach($$('input[type="text"]'), function(el) {
    connect(el, 'ondblclick', addBubble)
  })
});

