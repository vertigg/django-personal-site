window.onload = () => {
  if (releaseDate > new Date()) {
    $("#timer").countdown({ until: releaseDate, padZeroes: true, labels: [] });
  } else {
    $("#timer").html("League released!");
  }
};
