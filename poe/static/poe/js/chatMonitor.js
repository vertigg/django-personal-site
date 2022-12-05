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
            if (!savedData) { return defaultValue };
            return JSON.parse(savedData);
        },
        clear: () => localStorage.removeItem(key),
        save: (data) => localStorage.setItem(key, JSON.stringify(data)),
    }
}

const filterStore = storeFactory('savedFilters', defaultValue = []);
const optionsStore = storeFactory('settings', defaultValue = { pollingRate: 10, blacklistedUsers: [] });


app = PetiteVue.createApp({
    $delimiters: ["[[", "]]"],
    $reader: null,
    messagePattern: /(?<guild><.*?>?)\s(?<name>[^<]\w*)(?:\:\s)(?<text>.*)/gm,
    truncateString: str => str.length <= 20 ? str : `${str.substring(0, Math.min(15, str.length))}...`,
    matchedChatMessages: [],
    textFilters: filterStore.fetch(),
    options: optionsStore.fetch(),
    isMonitoring: false,
    selected: null,
    monitoringInterval: null,
    get reader() {
        if (!this.$reader) {
            this.$reader = new FileReader();
            this.$reader.addEventListener('load', (event) => this.detectMessages(this, event))
        }
        return this.$reader;
    },
    detectMessages(app, event) {
        let lines = event.target.result.split(/\r?\n/);
        for (const line of lines) {
            for (const match of line.matchAll(app.messagePattern)) {
                app.textFilters.forEach(word => {
                    // FIXME: Can be multiple matches in one string
                    interestWord = match.groups.text.match(new RegExp(word, 'i'));
                    if (interestWord) {
                        app.matchedChatMessages.push(match.groups)
                        showNotification(`Match for ${word} found in PoE Chat`);
                        app.autoscrollChat();
                    }
                })
            }
        }
    },
    get pollingRate() { return this.options.pollingRate; },
    set pollingRate(value) {
        this.options.pollingRate = value;
        optionsStore.save({ ...this.options, pollingRate: value });
    },
    get chatMessages() {
        // Apply blacklist filters here
        return this.matchedChatMessages
    },
    async selectClientFile() {
        this.stopWatching();
        let [fileHandle] = await window.showOpenFilePicker();
        if (fileHandle) {
            let f = await fileHandle.getFile();
            if (!f) { console.error('failed accessing file'); return; }
            this.selected = { handle: fileHandle, file: f };
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
        }, this.pollingRate * 1000);
        this.isMonitoring = true;
    },
    async checkFile() {
        if (!this.selectClientFile) { return; }
        let f = await this.selected.handle.getFile();
        if (f.lastModified > this.selected.file.lastModified && f.size > this.selected.file.size) {
            console.debug(this.selected.file.name, 'was updated');
            const offset = f.size - this.selected.file.size
            this.selected.file = f;
            this.$reader.readAsText(f.slice(-offset));
        } else {
            console.debug(this.selected.file.name, 'had no changes');
        }
    },
    addTextFilter(submitEvent) {
        let value = submitEvent.target.elements.word.value.trim();
        submitEvent.target.elements.word.value = '';
        if (!value) { return };
        let currentFilterSet = new Set(this.textFilters);
        if (!currentFilterSet.has(value)) {
            currentFilterSet.add(value);
            this.textFilters = Array.from(currentFilterSet);
            filterStore.save(this.textFilters);
        }
    },
    removeTextFilter(index) {
        this.textFilters.splice(index, 1);
        filterStore.save(this.textFilters)
    },
    clearTextFilters() {
        this.textFilters = [];
        filterStore.clear();
    },
    copyUsernameToClipboard(name) {
        navigator.clipboard.writeText(`@${name}`);
        //FIXME: Show drawer 
    },
    autoscrollChat() {
        lastMessageIndex = this.chatMessages.length - 1;
        const el = document.getElementsByClassName(`chat-entry-${lastMessageIndex}`)[0];
        if (el) { el.scrollIntoView({ behavior: 'smooth' }) };
    },
}).mount()
