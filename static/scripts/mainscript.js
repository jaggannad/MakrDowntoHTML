var next_cursor = '';
var prev_cursor = '';
var cursorlist = [''];

function fetchposts(ready, name){
    $.get('/initialcontents/'+next_cursor, function(data, status){
        if(data.success == true){
            var i = 0;
            var firstcontent = 0;

            document.getElementById('rightcolcontents').innerHTML = "<h3>Recent Conversions!</h3><hr>";

            while(data.content[i]){
                if(ready == true && firstcontent == 0 && data.content[i]['createdby'] == name){
                    document.getElementById('middlecolcontentdiv').innerHTML = data.content[i]['markupcontent'];
                    document.getElementById('middlecolcontenttext').innerHTML = data.content[i]['markupcontent'];
                }
                createacordian(data.content[i]);
                i++; firstcontent++;
            }
            if(data.more == true){
                cursorlist.push(data.next_cursor);
                prev_cursor = next_cursor;
                next_cursor = data.next_cursor;
            }
            else{
                prev_cursor = next_cursor;
                next_cursor = 'none';
            }
        }
        else{
            if(data.content == []){
                document.getElementById('rightcolcontents').innerHTML = "<h3>Sorry no feeds to display...</h3><hr>";
            }
        }
    });
}
function createacordian(data){
    var id = data['id'];
    var markupcontent = data.markupcontent.replace(/\n/g, ' ');
    markupcontent = markupcontent.replace(/'/g, /"/g);
    var $accordion = $("<div>", {id: 'acordian'+id});
    var $classcard = $("<div>", {id: "classcard"+id, class: 'card'});
    var $classcardheader = $("<div>", {id:"heading"+id, class:"card-header"});
    var $h5 = $("<h5>", {id: "h5"+id, class: "mb-0"});
    var $editlink = $("<a>", {id: "editlink"+id, href: "/redefine?contentid="+data['id'], target: 'blank', style: "float: right;"});
    var $viewlink = $("<a>", {id: "viewlink"+id, href: "/view?contentid="+data['id'], target: 'blank', style: "float: right; padding-right: 15px;"});
    var $date = $("<span>", {id: "date"+id, style: "float: right; padding-right: 15px;"});
    var $button = $("<button>", {id: "button"+id, class: "btn btn-link collapsed", 'data-toggle': "collapse", 'data-target': "#collapse"+id, 'aria-expanded': "false", 'aria-controls': "collapse"+id});
    var $classcollapse = $("<div>", {id: "collapse"+id, class: "collapse", 'aria-labelledby': "heading"+id, 'data-parent': "#accordion"});
    var $classcardbody = $("<div>", {id: "classcardbody"+id, class: "card-body", onclick: "showSelectedContent('"+markupcontent+"')"});

    $('#rightcolcontents').append($accordion);
    $accordion.append($classcard);
    $classcard.append($classcardheader);
    $classcardheader.append($h5);
    $h5.append($button);
    $h5.append($editlink);
    $h5.append($viewlink);
    $classcardheader.append($date);
    $classcard.append($classcollapse);
    $classcollapse.append($classcardbody);

    document.getElementById("button"+id).innerHTML = "Created By: "+data.createdby+"&nbsp;&nbsp;<span style='background: black; color: black;'>|</span>&nbsp; Desc: "+data.desc;
    document.getElementById("classcardbody"+id).innerHTML = "<pre>"+data.markdowncontent+"</pre>";

    document.getElementById("editlink"+id).innerHTML = "<i class='fas fa-pencil-alt'></i>";
    document.getElementById("viewlink"+id).innerHTML = "<i class='fas fa-eye'></i>";
    document.getElementById("date"+id).innerHTML = "<small>"+data.timestamp+"</small>";
}
function showSelectedContent(data){
    document.getElementById('Mostrecent').innerHTML = "VIEW CONTENTS";
    data.replace(' ', /\n/g);
    document.getElementById('middlecolcontentdiv').innerHTML = data;
    document.getElementById('middlecolcontenttext').value = data;
    console.log(data);
}

function fetchprevcontent(){
    if(prev_cursor != ''){
        index = cursorlist.indexOf(prev_cursor)-1;
        if(index >= 0){
            next_cursor = cursorlist[index];
            prev_cursor = cursorlist[index];
            fetchposts(false, '');
        }
    }
}

function fetchnextcontent(){
    if(next_cursor != 'none'){
        fetchposts(false, '');
    }
}

function switchoff(url){
    var choice = window.confirm("Are you sure you want to log out?");
     if(choice ==  true){
        window.location.replace(url);
     }
}
function htmlconversion(url, isPreview){
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify ({
            markdowntxt: document.getElementById('markdowntxt').value,
            description: document.getElementById('desc').value,
            preview: isPreview
        }),
        success: function(response){
            document.getElementById('middlecolcontentdiv').innerHTML = response.content;
            document.getElementById('middlecolcontenttext').value = response.content;
            if(isPreview == 'false'){
                window.alert("Posted content successfully");
            }
        },
        contentType: "application/json",
        dataType: 'json'
    });
}
function changeView(){
    if(document.getElementById('middlecolcontentdiv').style.display == 'none'){
        document.getElementById('middlecolcontenttext').style.display = 'none';
        document.getElementById('middlecolcontentdiv').style.display = 'block';
        document.getElementById('viewbtn').innerHTML = 'VIEW ESCAPED HTML';
    }
    else{
        document.getElementById('middlecolcontentdiv').style.display = 'none';
        document.getElementById('middlecolcontenttext').style.display = 'block';
        document.getElementById('viewbtn').innerHTML = 'VIEW RENDERED HTML';
    }
}