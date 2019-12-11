window.onload = () => {
  const release = new Date("12/13/2019 20:00:00 UTC");

  if (release > new Date()) {
    $("#timer").countdown({ until: release, padZeroes: true, labels: [] });
  } else {
    $("#timer").html("League released!");
  }
};
