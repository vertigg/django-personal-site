function checkNotificationPermissions() {
    if (!Notification) {
        console.error('Desktop notifications are not available in your browser.');
        return;
    }

    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
}


function showNotification(text) {
    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    } else {
        new Notification('Notification', {
            body: text,
            dir: 'ltr',
        });
    }
}

const storeFactory = (key, defaultValue) => {
    return {
        fetch: () => {
            let savedData = localStorage.getItem(key);
            if (!savedData) {return defaultValue};
            return JSON.parse(savedData);
        },
        clear: () => localStorage.removeItem(key),
        save: (data) => localStorage.setItem(key, JSON.stringify(data)),
    }
}

const filterStore = storeFactory('savedFilters', defaultValue = []);
const optionsStore = storeFactory('settings', defaultValue = {pollingRate: 10, blacklistedUsers: []});


app = PetiteVue.createApp({
    $delimiters: ["[[", "]]"],
    personChatPattern: /(?<guild><.*?>?)\s(?<name>[^<]\w*)(?:\:\s)(?<text>.*)/gm,
    chatMatches: [],
    filterWords: filterStore.fetch(),
    options: optionsStore.fetch(),
    isMonitoring: false,
    selected: null,
    monitoringInterval: null,
    get pollingRate() {
        return this.options.pollingRate;
    },
    set pollingRate(value) {
        this.options.pollingRate = value;
        optionsStore.save(this.options);
    },
    async selectClientFile() {
        this.stopWatching();
        let [fileHandle] = await window.showOpenFilePicker();
        if (fileHandle) {
            let f = await fileHandle.getFile();
            if (!f) { console.log('failed accessing file'); return; }
            this.selected = { handle: fileHandle, file: f };
            console.log('selected', f.name);
        }
    },
    stopWatching() {
        clearInterval(this.monitoringInterval);
        this.monitoringInterval = null;
        this.isMonitoring = false;
    },
    startWatching() {
        if (this.monitoringInterval) { this.stopWatching(); }
        if (!this.selected) { return; }

        checkNotificationPermissions();

        this.monitoringInterval = setInterval(async ts => {
            if (!this.selected) { return; }
            this.checkFile();
        }, this.settings.pollingRate * 1000);
        this.isMonitoring = true;
    },
    async checkFile() {
        if (!this.selectClientFile) { return; }
        let f = await this.selected.handle.getFile();
        if (f.lastModified > this.selected.file.lastModified && f.size > this.selected.file.size) {
            let offset = f.size - this.selected.file.size
            console.log(this.selected.file.name, 'was updated');
            this.selected.file = f;
            this.readFile(f, offset);
        } else {
            console.log(this.selected.file.name, 'had no changes');
        }
    },
    async readFile(f, offset) {
        let reader = new FileReader(); // FIXME: Maybe it's better to create one reader?
        reader.addEventListener('load', event => {
            let lines = event.target.result.split(/\r?\n/);
            for (const line of lines) {
                for (const match of line.matchAll(this.personChatPattern)) {
                    this.filterWords.forEach(word => {
                        // FIXME: Can be multiple matches in one string
                        interestWord = match.groups.text.match(new RegExp(word, 'i'));
                        if (interestWord) {
                            this.chatMatches.push(match.groups)
                            showNotification(`Match for ${word} found in PoE Chat`);
                        }
                    })
                }
            }
            console.log(event.target.result);
        });

        let blob = f.slice(-offset);
        reader.readAsText(blob);
    },
    addFilter(submitEvent) {
        let value = submitEvent.target.elements.word.value.trim();
        if (!value) { return };
        let currentFilterSet = new Set(this.filterWords);
        if (!currentFilterSet.has(value)) {
            currentFilterSet.add(value);
            this.filterWords = Array.from(currentFilterSet);
            filterStore.save(this.filterWords);
        }
    },
    removeWord(idx) {
        this.filterWords.splice(idx, 1);
        filterStore.save(this.filterWords)
    },
    clearWords() {
        this.filterWords = [];
        filterStore.clear();
    },
}).mount()
