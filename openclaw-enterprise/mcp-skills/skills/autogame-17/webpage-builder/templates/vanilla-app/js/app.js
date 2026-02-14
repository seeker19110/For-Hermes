// Basic Router
const Router = {
    routes: {},
    navigate(path) {
        window.location.hash = path;
    },
    register(path, handler) {
        this.routes[path] = handler;
    },
    handle(url) {
        let route = url.split('#')[1] || 'home';
        const handler = this.routes[route] || this.routes['home'];
        if (handler) handler();
    }
};

const store = new Store();

const App = {
    init() {
        Router.register('home', this.renderHome);
        Router.register('about', this.renderAbout);

        window.addEventListener('hashchange', () => {
            Router.handle(window.location.hash);
        });

        Router.handle(window.location.hash);
    },

    renderHome() {
        const view = document.getElementById('view');
        const items = store.getItems();
        
        view.innerHTML = `
            <h2>Home</h2>
            <p>Welcome to your vanilla app!</p>
            <ul>
                ${items.map(i => `<li>${i.text} <button onclick="store.deleteItem('${i.id}'); App.renderHome()">Delete</button></li>`).join('')}
            </ul>
            <input type="text" id="new-item" placeholder="Add new item">
            <button class="primary" onclick="App.addItem()">Add</button>
        `;
    },

    addItem() {
        const input = document.getElementById('new-item');
        if (input.value.trim()) {
            store.addItem(input.value);
            input.value = '';
            this.renderHome();
        }
    },

    renderAbout() {
        document.getElementById('view').innerHTML = `
            <h2>About</h2>
            <p>This is a simple vanilla JS app template.</p>
            <a href="#home">Back to Home</a>
        `;
    }
};

window.App = App;
window.router = Router;

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
