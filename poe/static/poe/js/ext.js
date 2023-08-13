window.onload = () => {
  let value = JSON.parse(document.getElementById('announcement-date').textContent);
  if (value) {
    value = new Date(value)
  }
  if (value > new Date()) {
    $("#timer").countdown({ until: value, padZeroes: true, labels: [] });
  } else {
    $("#timer").html("League released!");
  }
};
