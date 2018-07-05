var next_cursor = '';
var prev_cursor = '';
var cursor_list = [''];

function fetch_posts(ready, name){
    $.get('/initial-contents/'+next_cursor, function(data, status){
        if(data.success == true){
            var i = 0;
            var first_content = 0;

            document.getElementById('rightcolcontents').innerHTML = "";
            document.getElementById('rightcolcontentsheading').innerHTML = "<h3>Recent Conversions!</h3><hr>";
            document.getElementById('viewbtn').style.display = 'block';
            document.getElementById('pagination').style.display = 'block';

            while(data.content[i]){
                if(ready == true && first_content == 0 && data.content[i]['created_by'] == name){
                    document.getElementById('middlecolcontentdiv').innerHTML = data.content[i]['markup_content'];
                    document.getElementById('middlecolcontenttext').innerHTML = data.content[i]['markup_content'];
                    first_content++;
                    document.getElementById('Mostrecent').innerHTML = 'Last Modified'
                }
                create_acordian(data.content[i]);
                i++;
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
            document.getElementById('rightcolcontentsheading').innerHTML = "<h3>Sorry no feeds to display...</h3><hr>";
            document.getElementById('viewbtn').style.display = 'none';
            document.getElementById('pagination').style.display = 'none';
        }
        else{
            document.getElementById('rightcolcontentsheading').innerHTML = "<h3>Could not fetch feeds! Server Error!...</h3><hr>";
        }
    });
}
function create_acordian(data){
    var id = data['id'];
    var markup_content = data.markup_content.replace(/\n/g, ' ');
    markup_content = markup_content.replace(/'/g, /"/g);
    var $accordion = $("<div>", {id: 'acordian'+id});
    var $class_card = $("<div>", {id: "classcard"+id, class: 'card'});
    var $class_card_header = $("<div>", {id:"heading"+id, class:"card-header", style: 'overflow-x: scroll;'});
    var $h5 = $("<h5>", {id: "h5"+id, class: "mb-0"});
    var $edit_link = $("<a>", {id: "editlink"+id, href: "/redefine?content_id="+data['id'], target: 'blank', style: "float: right;"});
    var $view_link = $("<a>", {id: "viewlink"+id, href: "/view?content_id="+data['id'], target: 'blank', style: "float: right; padding-right: 15px;"});
    var $date = $("<span>", {id: "date"+id, style: "clear: both; float: right; padding-right: 15px;"});

    var $button = $("<button>", {id: "button"+id, class: "btn btn-link collapsed", 'data-toggle': "collapse", 'data-target': "#collapse"+id,
    'aria-expanded': "false", 'aria-controls': "collapse"+id, style: 'float: left; word-break:break-all; overflow-x: scroll;'});

    var $class_collapse = $("<div>", {id: "collapse"+id, class: "collapse", 'aria-labelledby': "heading"+id, 'data-parent': "#accordion"});
    var $class_card_body = $("<div>", {id: "classcardbody"+id, class: "card-body", onclick: "show_selected_content('"+markup_content+"')"});

    $('#rightcolcontents').append($accordion);
    $accordion.append($class_card);
    $class_card.append($class_card_header);
    $class_card_header.append($h5);
    $h5.append($button);
    $h5.append("<br><br>");
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
            description: document.getElementById('newmarkdowndesc').value,
            preview: is_preview
        }),
        success: function(response){
            document.getElementById('middlecolcontentdiv').innerHTML = response.content;
            document.getElementById('middlecolcontenttext').value = response.content;
            document.getElementById('viewbtn').style.display = 'block';
            if(is_preview == 'false'){
                if(!($('#popups').length))
                    popup("Posted content successfully");
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

function popup(content){
    var $popups = $("<div>", {id: 'popups',
    style: 'width: 30%; height: 100px; position: absolute; top: 15%; left: 35%; background: white; border-radius: 10px;'
     +'color: black; text-align: center; z-index: 100;' });

    $('body').append($popups);
    document.getElementById('popups').innerHTML = "<hr><p style='padding: auto;'><code>"+content+"!</code></p><hr>";
    $('#popups').fadeOut(3000, function(){
        $('#popups').remove();
    });
}

function new_markdown_validate(url, isPreview){
    var content = '';
    if(document.getElementById('markdowntxt').value!='' && document.getElementById('newmarkdowndesc').value!=''){
        html_conversion(url, isPreview);
    }
    else{
        content = 'Description';
        if(document.getElementById('markdowntxt').value == '')
            content = 'MarkDown';

        if(!($('#popups').length))
            popup("Please enter some "+content);
    }
}

// nav bar script

function checklink(url){
    if(window.location != 'https://syncmarkdown.appspot.com'+url){
          window.location.replace(url);
    }
}


function fetch_members(url, user_name){
    $.get(url, function(data, status){
            if(data.success){

                $('#alreadyhereheader').append("Already here in <code>"+ data.team_name +"</code>")
                var i=0;
                while(data.content[i]){
                    if(data.content[i] ===  user_name)
                        $('#alreadyherecontentslist').append("<li style='color: red; font-size: 1.5em;'>You</li>");
                    else
                        $('#alreadyherecontentslist').append("<li>"+ data.content[i] +"</li>");
                    i++;
                }
            }
        });
}


function addnewmember(url){
    if(document.getElementById('newmemberemail').value != "" &&  document.getElementById('newmembername').value != ""){
        $.ajax({
            type: 'POST',
            url: url,
            data: JSON.stringify({
                'new_member_email': document.getElementById('newmemberemail').value,
                'new_member_name': document.getElementById('newmembername').value
            }),
            success: function(response){
                if(!($('#popups').length)){
                    popup(response.desc);
                }

                if(response.success)
                    $('#alreadyherecontentslist').append("<li>"+ document.getElementById('newmembername').value +"</li>");
                document.getElementById('newmembername').value = "";
                document.getElementById('newmemberemail').value = "";
            },
            contentType: 'application/json',
            dataType: 'json'
        });
    }
    else{
        if(!($('#popups').length)){
            popup("Please fill-in all the fields!");
        }
    }
}
// nav bar script ends here
