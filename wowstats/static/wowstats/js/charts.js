google.charts.load('current', {
    'packages': ['line']
});


function testRequest(characterID) {
    var request = new XMLHttpRequest();

    request.onreadystatechange = function () {
        if (request.readyState != 4) {
            console.log("Loading..")
        } else if (request.readyState === 4) {
            if (request.status === 200) {
                var data = JSON.parse(JSON.parse((request.responseText)))
                drawAllCharts(data)
            }
        }
    }
    var params = "character=" + characterID
    request.open('GET', '/wow/charts-data/' + '?' + params);
    request.overrideMimeType("application/json");
    request.send()
}

function drawAllCharts(data) {
    drawChart(data, '2v2', 'Arena 2v2');
    drawChart(data, '3v3', 'Arena 3v3');
    drawChart(data, 'rbg', 'Arena rbg');
}

function drawChart(resp, key, title) {
    var elementID = 'arena-' + key
    var a = []
    resp.forEach(element => {
        a.push([new Date(element['date']), element[key]])
    });
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Day');
    data.addColumn('number', 'MMR');

    data.addRows(a);

    var options = {
        chart: {
            subtitle: 'Last 30 days'
        },
        width: 700,
        height: 250
    };

    var chart = new google.charts.Line(document.getElementById(elementID));

    chart.draw(data, google.charts.Line.convertOptions(options));
}