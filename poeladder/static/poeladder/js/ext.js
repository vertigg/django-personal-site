window.onload = () => {
  const release = new Date("01/15/2021 20:00:00 UTC");

  if (release > new Date()) {
    $("#timer").countdown({ until: release, padZeroes: true, labels: [] });
  } else {
    $("#timer").html("League released!");
  }
};
