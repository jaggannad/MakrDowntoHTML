function edit_markdown(url, type){
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify ({
            markdown_txt: document.getElementById('markdowntext').value,
            type: type
        }),
        success: function(response){
            document.getElementById('markupdiv').innerHTML = response.content;
            if(type == 'post'){
                if(!($('#popups').length))
                    popup("Posted content successfully");
            }

        },
        contentType: "application/json",
        dataType: 'json'
    });
}

function popup(content){
    var $popups = $("<div>", {id: 'popups',
    style: 'width: 30%; height: 100px; position: absolute; top: 15%; left: 35%; background: white; border-radius: 10px;'
     +'color: black; text-align: center;' });

    $('body').append($popups);
    document.getElementById('popups').innerHTML = "<hr><p style='padding: auto;'><code>"+content+"!</code></p><hr>";
    $('#popups').fadeOut(3000, function(){
        $('#popups').remove();
    });
}