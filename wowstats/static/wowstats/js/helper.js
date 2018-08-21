function track(id, token) {
    data = 'id=' + id + '&csrfmiddlewaretoken=' + token;
    if (document.getElementById('track-' + id).checked) {
        data += "&track=true"
    } else {
        data += "&track=false"
    }
    var request = new XMLHttpRequest();
    request.open('POST', '/wow/track/', true);
    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
    request.send(data);
}