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

const DIVISIONS = [
  { amount: 60, name: 'seconds' },
  { amount: 60, name: 'minutes' },
  { amount: 24, name: 'hours' },
  { amount: 7, name: 'days' },
  { amount: 4.34524, name: 'weeks' },
  { amount: 12, name: 'months' },
  { amount: Number.POSITIVE_INFINITY, name: 'years' }
]

app = PetiteVue.createApp({
  $delimiters: ["[[", "]]"],
  datePicker: flatpickr("#picker input", { mode: 'range' }),
  timeFormatter: new Intl.RelativeTimeFormat("en", { localeMatcher: "lookup" }),
  isLoading: false,
  isReceivedEmptyResponse: false,
  errorMessage: '',
  previousDates: [],
  entries: [],
  getActionClass(action) {
    switch (action) {
      case 'added':
        return 'stash-action-added'
      case 'removed':
        return 'stash-action-removed'
      case 'modified':
        return 'stash-action-modified'
      default:
        break;
    }
  },
  getRelativeDate(date) {
    let duration = (new Date(date * 1000) - new Date()) / 1000

    for (let i = 0; i <= DIVISIONS.length; i++) {
      const division = DIVISIONS[i]
      if (Math.abs(duration) < division.amount) {
        return this.timeFormatter.format(Math.round(duration), division.name)
      }
      duration /= division.amount
    }
  },
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