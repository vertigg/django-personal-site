window.onload = function () {
    var now = new Date()
    var release = new Date('6/1/2018 20:00:00 UTC')

    if (release > now) {
        $("#timer").countdown({ until: release, padZeroes: true, labels: [] });
    }
    else {
        $("#timer").html('League released!')
    }
}