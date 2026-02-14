class Store {
    constructor(storageKey = 'vanilla_app_data') {
        this.storageKey = storageKey;
        this.data = this.load();
    }

    load() {
        if (typeof localStorage !== 'undefined') {
            const raw = localStorage.getItem(this.storageKey);
            return raw ? JSON.parse(raw) : { items: [] };
        }
        return { items: [] };
    }

    save() {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem(this.storageKey, JSON.stringify(this.data));
        }
    }

    getItems() {
        return this.data.items;
    }

    addItem(text) {
        const item = {
            id: Date.now().toString(),
            text,
            completed: false,
            createdAt: new Date().toISOString()
        };
        this.data.items.unshift(item);
        this.save();
        return item;
    }

    deleteItem(id) {
        this.data.items = this.data.items.filter(i => i.id !== id);
        this.save();
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = Store;
} else {
    window.Store = Store;
}
