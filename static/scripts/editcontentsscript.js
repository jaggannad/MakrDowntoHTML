function editmarkdown(url, type){
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify ({
            markdowntxt: document.getElementById('markdowntext').value,
            type: type
        }),
        success: function(response){
            document.getElementById('markupdiv').innerHTML = response.content;
        },
        contentType: "application/json",
        dataType: 'json'
    });
}

