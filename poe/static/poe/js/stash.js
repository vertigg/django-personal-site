async function postData(dateRange) {
  const response = await fetch(
    "/poe/api/stash", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf
    },
    body: JSON.stringify({ 'dates': dateRange })
  });
  return response;
}

function arraysEqual(a1, a2) {
  return a1.length === a2.length && a1.every((v, i) => { return v === a2[i] })
}

app = PetiteVue.createApp({
  $delimiters: ["[[", "]]"],
  datePicker: flatpickr("#picker input", { mode: 'range' }),
  isLoading: false,
  isReceivedEmptyResponse: false,
  errorMessage: '',
  previousDates: [],
  entries: [],
  reset() {
    this.entries = [];
    this.datePicker.clear();
    this.errorMessage = '';
    this.isReceivedEmptyResponse = false;
  },
  async checkDateRange() {
    if (!this.datePicker || !this.datePicker.selectedDates.length || arraysEqual(this.previousDates, this.datePicker.selectedDates)) {
      return;
    }
    this.previousDates = this.datePicker.selectedDates;
    this.isLoading = true;
    postData(this.datePicker.selectedDates)
      .then(async (response) => {
        if (response.ok) {
          this.entries = await response.json()
          this.isReceivedEmptyResponse = this.entries.length ? false : true;
          this.errorMessage = ''
        }
        else {
          this.errorMessage = `${response.statusText} ${response.status}`
          console.error(response.statusText, response.status);
          this.previousDates = [];
        };
      })
      .catch(err => {
        this.errorMessage = err.message;
        this.previousDates = [];
        console.error(err);
      })
      .finally(() => this.isLoading = false)
  },
}).mount()