var next_cursor = '';
var prev_cursor = '';
var cursor_list = [''];


function re_initialize_cursors(){
    next_cursor = '';
    prev_cursor = '';
    cursor_list = [''];
}

function fetch_posts(ready, name, current_team){
    $.get('/initial-contents/'+next_cursor, function(data, status){
        if(data.success == true && data.content != null && data.content.length > 0){
            var i = 0;
            var first_content = 0;
            document.getElementById('rightcolcontents').innerHTML = "";
            document.getElementById('rightcolcontentsheading').innerHTML = "<h3>Recent Conversions!</h3><hr>";
            document.getElementById('viewbtn').style.display = 'block';
            document.getElementById('pagination').style.display = 'block';
            document.getElementById('rightcolcontents').innerHTML = "";
            while(data.content[i]){
                if(ready == true && first_content == 0 && data.content[i]['created_by'] == name){
                    document.getElementById('middlecolcontentdiv').innerHTML = data.content[i]['markup_content'];
                    document.getElementById('middlecolcontenttext').innerHTML = data.content[i]['markup_content'];
                    first_content++;
                    document.getElementById('Mostrecent').innerHTML = 'Last Modified'
                }
                create_acordian(data.content[i], current_team);
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
        else if(data.success == false || cursor_list.length <= 1 && (data.content == null || data.content == '')){
            document.getElementById('rightcolcontentsheading').innerHTML = "<h3>Sorry no feeds to display...</h3><hr>";
            document.getElementById('Mostrecent').innerHTML = 'Nothing to show!'
            document.getElementById('rightcolcontents').innerHTML = "";
            document.getElementById('middlecolcontentdiv').innerHTML = "";
            document.getElementById('middlecolcontenttext').value = "";

            document.getElementById('middlecolcontentdiv').style.display = "block";
            document.getElementById('middlecolcontenttext').style.display = "none";
            document.getElementById('viewbtn').style.display = 'none';
            document.getElementById('pagination').style.display = 'none';
        }
    });
}
function create_acordian(data, current_team){
    var id = data['id'];
    var markup_content = data.markup_content.replace(/\n/g, '@@@');
    markup_content = markup_content.replace(/'/g, '"');

    var $class_card = $("<div>", {id: "classcard"+id, class: 'card'});
    var $class_card_header = $("<div>", {id:"heading"+id, class:"card-header"});
    var $h5 = $("<h5>", {id: "h5"+id, class: "mb-0"});

    var $created_by = $("<span>", {id: "created_by"+id, style: "clear: both; float: left; padding-left: 15px;"});
    var $edit_link = $("<a>", {id: "editlink"+id, href: "/redefine?content_id="+data['id'], target: 'blank', style: "float: right;"});
    var $view_link = $("<a>", {id: "viewlink"+id, href: "/view?content_id="+data['id'], target: 'blank', style: "float: right; padding-right: 15px;"});


    var $dropdowndiv = $("<div>", {id: "settingsdropdown"+id, class: "dropdown", style: "float: right; padding-right: 5px;"});
    var $dropdownspan = $("<span>", {id: "dropdownspan"+id});
    var $dropdownmenu = $("<div>", {class: "dropdown-content"});

    var $visibledropdown = $("<div>", {id: 'visibilitydropdown'+id, class: 'dropdown visibilitydropdown', style: "float: right; padding-right: 15px;"});
    var $visibledropbtn = $("<div>", {id: 'visibilitydropbtn'+id, class: 'dropdown visibilitydropbtn'});
    var $visibledropcontent = $("<div>", {id: 'visibilitydropdown-content'+id, class: 'visibilitydropdown-content'});
    var $visibletoall = $("<button>", {id: 'visibletoall'+id, class: 'btn btn-link visibletoall', onclick: "change_visibility_call('"+id+"', '', 'visibletoall', 'All')", style: "display: block; font-size: 0.9em;"});
    var $visibletosome = $("<button>", {id: "visibletosome"+id, class: "btn btn-link visibletosome", onclick: "select_teams_for_visibility('"+id+"')",
    style: "display: block; font-size: 0.9em;"});
    var $visibletonone =  $("<button>", {id: 'visibletonone'+id, class: 'btn btn-link visibletonone', onclick: "change_visibility_call('"+id+"', '', 'visibletonone', 'None')", style: "display: block; font-size: 0.9em;"});


    var $last_modified = $("<span>", {id: "last_modified"+id, style: "clear: both; float: left; padding-left: 15px;"});
    var $date = $("<span>", {id: "date"+id, style: "float: right; padding-right: 15px;"});


    var $button = $("<button>", {id: "button"+id, class: "btn btn-link collapsed", 'data-toggle': "collapse", 'data-target': "#collapse"+id,
    'aria-expanded': "false", 'aria-controls': "collapse"+id, style: 'float: left; word-break:break-all; overflow-x: scroll;'});
    var $show_public = $("<span>", {id: "show_public"+id, style: "float: right; display: none;"});


    var $class_collapse = $("<div>", {id: "collapse"+id, class: "collapse", 'aria-labelledby': "heading"+id, 'data-parent': "#accordion"});
    var $class_card_body = $("<div>", {id: "classcardbody"+id, class: "card-body", onclick: "show_selected_content('"+markup_content+"')"});

    $('#rightcolcontents').append($class_card);
    $class_card.append($class_card_header);
    $class_card_header.append($h5);

    $h5.append($button);
    $h5.append($show_public);
    $h5.append("<br><br>");
    $h5.append($created_by);
    $h5.append($edit_link);
    $h5.append($view_link);

    $class_card_header.append($visibledropdown);
    $visibledropdown.append($visibledropbtn);
    $visibledropdown.append($visibledropcontent);
    $visibledropcontent.append($visibletoall);
    $visibledropcontent.append($visibletosome);
    $visibledropcontent.append($visibletonone);

    $class_card_header.append($dropdowndiv);
    $dropdowndiv.append($dropdownspan);
    $dropdowndiv.append($dropdownmenu);
    $dropdownmenu.append("<span>No settings currently!</span>");

    $class_card_header.append($last_modified);
    $class_card_header.append($date);
    $class_card.append($class_collapse);

    $class_collapse.append($class_card_body);

    document.getElementById("button"+id).innerHTML = "Desc: "+data.desc;

    document.getElementById("classcardbody"+id).innerHTML = "<pre>"+data.markdown_content+"</pre>";

    document.getElementById("created_by"+id).innerHTML = "Created by: "+ data.created_by;
    document.getElementById("editlink"+id).innerHTML = "<i class='fas fa-pencil-alt'></i>";
    document.getElementById("viewlink"+id).innerHTML = "<i class='fas fa-eye'></i>";

    document.getElementById("last_modified"+id).innerHTML = "<small> Last Modified: "+ data.last_modified;
    document.getElementById("date"+id).innerHTML = "<small>"+data.timestamp+"</small>";
    $show_public.html('<i class="fa fa-user-circle-o" aria-hidden="true" style="color: purple; font-size: 0.8em;"> - Public</i>');


    if(current_team != data.team_id)
        document.getElementById("settingsdropdown"+id).style.display = 'none';

    $dropdownspan.html('<i class="fa fa-cogs" aria-hidden="true" style="color: hotpink;"></i>');

    $visibledropbtn.html('Visible to <i class="fas fa-caret-down">');

    $visibletoall.html("All<br>");
    $visibletosome.html('Some<br>');
    $visibletonone.html('None<br>');

    if(data.visibility_all == true){
        $visibletoall.html("All &nbsp;&nbsp; <i class='fas fa-check'></i><br>");
        document.getElementById("show_public"+id).style.display = "block";
    }
    else if(data.visibility_some == true)
        $visibletosome.html("Some &nbsp;&nbsp; <i class='fas fa-check'></i><br>");
    else if(data.visibility_none == true)
        $visibletonone.html("None &nbsp;&nbsp; <i class='fas fa-check'></i><br>");

}


function show_selected_content(data){
    document.getElementById('Mostrecent').innerHTML = "VIEW CONTENTS";
    data = data.replace(/@@@/g, '\n');
    document.getElementById('middlecolcontentdiv').innerHTML = data;
    document.getElementById('middlecolcontenttext').innerHTML = data;
}

function fetch_prev_content(team_id){
    if(prev_cursor != ''){
        index = cursor_list.indexOf(prev_cursor)-1;
        if(index >= 0){
            next_cursor = cursor_list[index];
            prev_cursor = cursor_list[index];
            fetch_posts(false, '', team_id);
        }
    }
}

function fetch_next_content(team_id){
    if(next_cursor != 'none'){
        fetch_posts(false, '', team_id);
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

                document.getElementById('markdowntxt').value = ""
                document.getElementById('newmarkdowndesc').value = ""
                document.getElementById('middlecolcontentdiv').innerHTML = "";
                document.getElementById('middlecolcontenttext').value = "";
                document.getElementById('middlecolcontenttext').style.display = 'none';
                document.getElementById('viewbtn').style.display = 'none';
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


function change_visibility_call(id, team_list, type, desc){
    $.ajax({
        type: "POST",
        url: "/change_visibility",
        data: JSON.stringify({
           markdown_id: id,
           type: type,
           team_list: team_list
        }),
        success: function(response){
            if(!($('#popups').length))
                popup(response.desc);

            $('#visibletoall'+id).html("All<br>");
            $('#visibletosome'+id).html('Some<br>');
            $('#visibletonone'+id).html('None<br>');
            document.getElementById("show_public"+id).style.display = "none";

            if(response.visibility == true)
                $('#'+type+id).html(desc + " &nbsp;&nbsp; <i class='fas fa-check'></i><br>");
            else
                 $('#visibletonone'+id).html("None &nbsp;&nbsp; <i class='fas fa-check'></i><br>")

            if(desc == 'All')
                document.getElementById("show_public"+id).style.display = "block";

            document.getElementById('teams').innerHTML = "";
            document.getElementById('visibilty-teams').style.display = "none";
        },
        contentType: 'application/json',
        dataType: 'json'
    });
}


function change_visibility(id){
    team_list = {};
    items = document.getElementById('allteamsunorderedlist').getElementsByTagName('input');
    for(let i=1; i<items.length; i++){
        team_list[items[i].id] = items[i].checked;
    }

    if(team_list.length <= 0)
        team_list = null;
    else
        team_list = JSON.stringify(team_list);

    change_visibility_call(id, team_list, 'visibletosome', 'Some');
}


function fetch_teams(id){
    $.get("/fetch_teams?markdown_id="+id, function(data, status){
        if(data.success){
            var i = 0;
            if(data.team_list.length != 0){
                var $ul = $("<ul>", {id: "allteamsunorderedlist"});
                $('#teams').append($ul);
                $ul.html("<input type='checkbox' id='allteamscheckbox'> All");
                document.getElementById('select-teams-header').innerHTML = "<h3>Select Domains to share with</h3>"
                document.getElementById('selectteamsbtn').style.display = 'block';
            }
            else{
                document.getElementById('select-teams-header').innerHTML = "<h3>No Domains to share with</h3>"
                document.getElementById('selectteamsbtn').style.display = 'none';
            }

            while(data.team_list[i]){
                var $team = $("<li>" ,{id: "listitem"+data.team_list[i].team_name});
                $ul.append($team);
                $team.html("<input type='checkbox' id='"+data.team_list[i].team_name+"'> "+ data.team_list[i].team_name);
                if(data.team_list[i].is_checked)
                    document.getElementById(data.team_list[i].team_name).checked = true;
                i++;
            }
            $("#allteamscheckbox").click(function(){
                is_checked = document.getElementById('allteamscheckbox').checked;

                items = document.getElementById('allteamsunorderedlist').getElementsByTagName('input');
                for(let i=0; i<items.length; i++){
                    items[i].checked = is_checked;
                }
            });
        }
    });
}

function select_teams_for_visibility(id){
    // select teams for visibility

    var visibiltyteamsmodal = document.getElementById('visibilty-teams');
    var visibiltyteamsspan = document.getElementsByClassName("visibilty-teams-close")[0];

    visibiltyteamsmodal.style.display = "block";

    fetch_teams(id);

    visibiltyteamsspan.onclick = function() {
        document.getElementById('teams').innerHTML = "";
        visibiltyteamsmodal.style.display = "none";
    }

    document.getElementById('selectteamsbtn').onclick = function(){
        change_visibility(id);
    }

    document.getElementById('addnewdomain').onclick = function(){
        new_domain_name = document.getElementById('new_domain_name').value;
        if(new_domain_name.search(/[a-z0-9]+[.][a-z]+/g) == 0){
            $.ajax({
                type: 'POST',
                url: '/add_new_domain',
                data: JSON.stringify({
                    domain_name: new_domain_name,
                    markdown_id: id
                }),
                success: function(response){
                    if(!($('#popups').length))
                        popup(response.desc);
                    document.getElementById('new_domain_name').value = '';

                    if($('#allteamsunorderedlist').length == 0 ){
                        var $ul = $("<ul>", {id: "allteamsunorderedlist"});
                        $('#teams').append($ul);
                        $ul.html("<input type='checkbox' id='allteamscheckbox'> All");
                        document.getElementById('selectteamsbtn').style.display = 'block';
                    }
                    var $team = $("<li>" ,{id: "listitem"+new_domain_name});
                    $('#allteamsunorderedlist').append($team);
                    $team.html("<input type='checkbox' id='"+new_domain_name+"'> "+ new_domain_name);
                    document.getElementById(new_domain_name).checked = true;

                    $("#allteamscheckbox").click(function(){
                        is_checked = document.getElementById('allteamscheckbox').checked;

                        items = document.getElementById('allteamsunorderedlist').getElementsByTagName('input');
                        for(let i=0; i<items.length; i++){
                            items[i].checked = is_checked;
                        }
                    });

                },
                contentType: 'application/json',
                dataType: 'json'
            });
        }
        else{
            if(!($('#popups').length))
               popup("invalid domain name");
        }
    }

    // select teams for visibility ends here
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

function checklink(url, current_team){
    if(window.location != 'https://syncmarkdown.appspot.com'+url){
          if(current_team == 'None' || current_team == ''){
            document.getElementById('createnewprojectmodal').style.display = "block";
          }
          else
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


// cheat sheet modal

var cheatsheetmodal = document.getElementById('cheatsheetmodal');
var cheatsheetmodalbtn = document.getElementById("cheatsheetlink");
var cheatsheetmodalspan = document.getElementsByClassName("close")[0];

cheatsheetmodalbtn.onclick = function() {
    cheatsheetmodal.style.display = "block";
}
cheatsheetmodalspan.onclick = function() {
    cheatsheetmodal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == cheatsheetmodal) {
        cheatsheetmodal.style.display = "none";
    }
}
// cheat sheet modal ends here


function show_selected_project(response){
    re_initialize_cursors();

    document.getElementById('newmarkdownlink').href = "javascript: checklink('/new_markdown', '"+ response.current_team +"')";
    document.getElementById('addnewmemberlink').href = "javascript: checklink('/add_member', '"+ response.current_team +"')";
    document.getElementById('selectprojectfloat').onclick = function(){ selectprojectsnavopennav(response.user_name, response.current_team); };
    fetch_posts(true, response.user_name, response.current_team);
}


function selectprojectsnavopennav(user_name) {
    document.getElementById("selectprojectsnav").style.width = "40%";
    document.getElementById("selectprojectfloat").style.display = "none";
    fetch_user_projects(user_name, current_team);
}

function selectprojectsnavclosenav() {
    document.getElementById("selectprojectsnav").style.width = "0%";
    document.getElementById("selectprojectfloat").style.display = "block";
}



// create new project ends here

var createnewprojectmodal = document.getElementById('createnewprojectmodal');
var createnewprojectbtn = document.getElementById("newprojectlink");
var createnewprojectspan = document.getElementsByClassName("createnewprojectclose")[0];

createnewprojectbtn.onclick = function() {
    createnewprojectmodal.style.display = "block";
}

createnewprojectspan.onclick = function() {
    createnewprojectmodal.style.display = "none";
}

function create_new_project(){
    if(document.getElementById('newprojectname').value != ""){
        $.ajax({
            type: "POST",
            url: "/create_team",
            data: JSON.stringify({
                project_name: document.getElementById('newprojectname').value
            }),
            success: function(response){
                document.getElementById('createnewprojectmodal').style.display = "none";
                document.getElementById('newprojectname').value = "";
                if(!($('#popups').length)){
                    popup("Created Project Successfully");
                }
                current_team = response.current_team;
                setTimeout(function(){ show_selected_project(response); }, 1000);
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
// create new project ends here

// nav bar script ends here


// select projects


function select_project(user_name, selected_team){
    $.ajax({
        type: 'POST',
        url: '/select_project',
        data: JSON.stringify({
            project_id: selected_team
        }),
        success: function(response){
            if(!($('#popups').length)){
                popup(response.desc);
            }
            setTimeout(function(){ show_selected_project(response); }, 1000);

            $('#project'+current_team).css({
                textShadow: 'none',
                textDecoration: 'none',
                fontSize: "25px"
            });
            $('#project'+selected_team).css({
                textShadow: '2px 2px #ff0000',
                fontSize: "20px"
            });

            current_team = response.current_team;

//          document.getElementById("project"+current_team).style = 'none';
//          document.getElementById("project"+current_team).style.color = 'white';

        },
        contentType: 'application/json',
        dataType: 'json'
    });
}


function create_project_anchor(user_name, data){
    if(! $('#project'+data.team_id).length){
        var $project = $('<a>', {id: 'project'+data.team_id, style: 'color: white;', href: 'javascript: select_project("'+ user_name +'", "'+data.team_id+'")'});
        $('.selectprojectsnavoverlay-content').append($project);
        $project.html(data.team_name);
        if(data.team_id == current_team)
            $project.css({
                textShadow: '2px 2px #ff0000',
                fontSize: "20px"
            });
    }
}


function fetch_user_projects(user_name){
    $.get('/fetch_user_projects', function(data, status){
        if(data.success){
            if(data.projects_list.length > 0){
                var i = 0;
                while(data.projects_list[i]){
                    create_project_anchor(user_name, data.projects_list[i], current_team);
                    i++;
                }
            }
            else{
                $('.selectprojectsnavoverlay-content').append("<h4>You are not a part of any project</h4>");
            }
        }
    });
}

// select projects ends here