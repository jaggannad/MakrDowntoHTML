var next_cursor = '';
var prev_cursor = '';
var cursor_list = [''];

function fetch_posts(ready, name){
    $.get('/initial-contents/'+next_cursor, function(data, status){
        if(data.success == true){
            var i = 0;
            var first_content = 0;

            document.getElementById('rightcolcontents').innerHTML = "<h3>Recent Conversions!</h3><hr>";

            while(data.content[i]){
                if(ready == true && first_content == 0 && data.content[i]['createdby'] == name){
                    document.getElementById('middlecolcontentdiv').innerHTML = data.content[i]['markupcontent'];
                    document.getElementById('middlecolcontenttext').innerHTML = data.content[i]['markupcontent'];
                }
                create_acordian(data.content[i]);
                i++; first_content++;
            }
            if(data.more == true){
                cursor_list.push(data.next_cursor);
                prev_cursor = next_cursor;
                next_cursor = data.next_cursor;
            }
            else{
                prev_cursor = next_cursor;
                next_cursor = 'none';
            }
        }
        else if(data.content == null){
            document.getElementById('rightcolcontents').innerHTML = "<h3>Sorry no feeds to display...</h3><hr>";
        }
        else{
            document.getElementById('rightcolcontents').innerHTML = "<h3>Could not fetch feeds! Server Error!...</h3><hr>";
        }
    });
}
function create_acordian(data){
    var id = data['id'];
    var markup_content = data.markup_content.replace(/\n/g, ' ');
    markup_content = markup_content.replace(/'/g, /"/g);
    var $accordion = $("<div>", {id: 'acordian'+id});
    var $class_card = $("<div>", {id: "classcard"+id, class: 'card'});
    var $class_card_header = $("<div>", {id:"heading"+id, class:"card-header"});
    var $h5 = $("<h5>", {id: "h5"+id, class: "mb-0"});
    var $edit_link = $("<a>", {id: "editlink"+id, href: "/redefine?content_id="+data['id'], target: 'blank', style: "float: right;"});
    var $view_link = $("<a>", {id: "viewlink"+id, href: "/view?content_id="+data['id'], target: 'blank', style: "float: right; padding-right: 15px;"});
    var $date = $("<span>", {id: "date"+id, style: "float: right; padding-right: 15px;"});
    var $button = $("<button>", {id: "button"+id, class: "btn btn-link collapsed", 'data-toggle': "collapse", 'data-target': "#collapse"+id, 'aria-expanded': "false", 'aria-controls': "collapse"+id});
    var $class_collapse = $("<div>", {id: "collapse"+id, class: "collapse", 'aria-labelledby': "heading"+id, 'data-parent': "#accordion"});
    var $class_card_body = $("<div>", {id: "classcardbody"+id, class: "card-body", onclick: "show_selected_content('"+markup_content+"')"});

    $('#rightcolcontents').append($accordion);
    $accordion.append($class_card);
    $class_card.append($class_card_header);
    $class_card_header.append($h5);
    $h5.append($button);
    $h5.append($edit_link);
    $h5.append($view_link);
    $class_card_header.append($date);
    $class_card.append($class_collapse);
    $class_collapse.append($class_card_body);

    document.getElementById("button"+id).innerHTML = "Created By: "+data.created_by+"&nbsp;&nbsp;<span style='background: black; color: black;'>|</span>&nbsp; Desc: "+data.desc;
    document.getElementById("classcardbody"+id).innerHTML = "<pre>"+data.markdown_content+"</pre>";

    document.getElementById("editlink"+id).innerHTML = "<i class='fas fa-pencil-alt'></i>";
    document.getElementById("viewlink"+id).innerHTML = "<i class='fas fa-eye'></i>";
    document.getElementById("date"+id).innerHTML = "<small>"+data.timestamp+"</small>";
}
function show_selected_content(data){
    document.getElementById('Mostrecent').innerHTML = "VIEW CONTENTS";
    data.replace(' ', /\n/g);
    document.getElementById('middlecolcontentdiv').innerHTML = data;
    document.getElementById('middlecolcontenttext').value = data;
    console.log(data);
}

function fetch_prev_content(){
    if(prev_cursor != ''){
        index = cursor_list.indexOf(prev_cursor)-1;
        if(index >= 0){
            next_cursor = cursor_list[index];
            prev_cursor = cursor_list[index];
            fetch_posts(false, '');
        }
    }
}

function fetch_next_content(){
    if(next_cursor != 'none'){
        fetch_posts(false, '');
    }
}

function switch_off(url){
    var choice = window.confirm("Are you sure you want to log out?");
     if(choice ==  true){
        window.location.replace(url);
     }
}
function html_conversion(url, is_preview){
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify ({
            markdown_txt: document.getElementById('markdowntxt').value,
            description: document.getElementById('desc').value,
            preview: is_preview
        }),
        success: function(response){
            document.getElementById('middlecolcontentdiv').innerHTML = response.content;
            document.getElementById('middlecolcontenttext').value = response.content;
            if(is_preview == 'false'){
                window.alert("Posted content successfully");
            }
        },
        contentType: "application/json",
        dataType: 'json'
    });
}
function change_View(){
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