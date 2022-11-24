async function postData(dateRange) {
  const response = await fetch(
    "/poe/api/stash", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf
    },
    body: JSON.stringify({ 'from_date': dateRange[0], 'end_date': dateRange[1] })
  });
  return response;
}

app = PetiteVue.createApp({
  $delimiters: ["[[", "]]"],
  isLoading: false,
  pickerInstance: flatpickr("#picker input", { mode: 'range' }),
  entries: [],
  reset() {
    this.entries = [];
    this.pickerInstance.clear();
  },
  async checkDateRange() {
    if (!this.pickerInstance || !this.pickerInstance.selectedDates.length) {
      return;
    }
    this.isLoading = true;
    let unixDates = [];
    this.pickerInstance.selectedDates.forEach(date => unixDates.push(date.getTime() / 1000))
    unixDates.sort((a, b) => b - a);
    postData(unixDates)
      .then(async (response) => {
        if (response.ok) {
          this.entries = await response.json()
        }
        else {
          console.error(response.statusText, response.status);
        };
      })
      .catch(err => console.log(err))
      .finally(() => this.isLoading = false)
  },
}).mount()