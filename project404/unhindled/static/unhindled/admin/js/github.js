'use strict';

{
    const headers = JSON.parse(document.getElementById('headers').textContent);
    console.log("AJAX headers: " + JSON.stringify(headers));

    var xhr = new XMLHttpRequest();

    xhr.open("GET", headers['uri']);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            try {
                if (xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    console.log(data);
                }
            } 
            catch(e) {
                alert('Error: ' + e.name);
            }
        }
    };

    xhr.setRequestHeader("Accept", "text/json");
    xhr.setRequestHeader("Content-Type", "text/json");
    xhr.send(JSON.stringify(objects));
    
    // fetch request, then
    // make table if status==200, then
    // fill table
}