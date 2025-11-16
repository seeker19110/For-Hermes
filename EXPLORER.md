# 12-Factor Agents Explorer GUI

A beautiful, interactive web-based GUI for exploring and understanding all 12 factors for building reliable LLM applications.

## 🎯 What is This?

The Explorer is a comprehensive, interactive tool that makes it easy to:

- **Learn** all 12 factors through an intuitive interface
- **Visualize** concepts with integrated diagrams
- **Search** across all content to find specific topics
- **Navigate** between factors with visual cards and sidebar
- **Understand** markdown-rendered content with code examples

## 🚀 Quick Start

### Option 1: Run Directly

```bash
cd explorer
npm install
npm run dev
```

Then open http://localhost:3100 in your browser

### Option 2: Use the Launcher

```bash
./explorer/start.sh
```

## ✨ Features

### 🎨 Beautiful UI
- Modern gradient design with smooth animations
- Responsive layout for desktop and mobile
- Clean, readable typography

### 📚 Complete Content
- All 12 factors with full markdown content
- Brief history of software introduction
- Code examples from real implementations

### 🔍 Search & Navigation
- Real-time search across all factors
- Visual navigation cards with diagrams
- Sidebar navigation for quick access

### 🖼️ Visual Learning
- Integrated factor diagrams
- Visual navigation grid
- Image support in content

### ⚡ Fast & Lightweight
- Vanilla JavaScript - no heavy frameworks
- Server-side markdown rendering
- Minimal dependencies

## 📖 Usage Guide

1. **Start the server** - Follow quick start instructions above
2. **Browse factors** - Click any factor in the sidebar
3. **Visual navigation** - Use diagram cards on the welcome screen
4. **Search** - Type in the search box to filter factors
5. **Read & learn** - Enjoy formatted markdown with code examples

## 🏗️ Architecture

```
explorer/
├── public/
│   └── index.html       # Single-page application
├── src/
│   └── server.ts        # Express API server
└── package.json
```

### Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Marked.js
- **Backend**: Express.js, TypeScript
- **Build**: TSX for TypeScript execution

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main explorer interface |
| `GET /api/factors` | List all 12 factors |
| `GET /api/content/:slug` | Get factor markdown content |
| `GET /api/image/:id` | Get factor diagram image |
| `GET /api/search?q=` | Search all content |
| `GET /api/examples/:factor` | Get code examples |

## 🎓 Educational Value

This explorer helps you understand:

1. **Factor 1** - Natural Language to Tool Calls
2. **Factor 2** - Own Your Prompts
3. **Factor 3** - Own Your Context Window
4. **Factor 4** - Tools are Structured Outputs
5. **Factor 5** - Unify Execution State
6. **Factor 6** - Launch/Pause/Resume
7. **Factor 7** - Contact Humans with Tools
8. **Factor 8** - Own Your Control Flow
9. **Factor 9** - Compact Errors
10. **Factor 10** - Small, Focused Agents
11. **Factor 11** - Trigger from Anywhere
12. **Factor 12** - Stateless Reducer

Each factor includes:
- Core principles and explanations
- Visual diagrams and illustrations
- Code examples from demos
- Practical implementation guidance

## 🔧 Development

### Install Dependencies
```bash
cd explorer
npm install
```

### Development Mode
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm start
```

### Watch Mode
```bash
npm run watch
```

## 🌟 Key Benefits

- **Visual Learning** - Diagrams and visual navigation
- **Interactive** - Click, search, and explore at your own pace
- **Complete** - All 12 factors in one place
- **Accessible** - Clean UI, easy to use
- **Fast** - Lightweight and responsive

## 📱 Screenshots

The explorer features:
- Welcome screen with statistics and visual navigation
- Sidebar with all 12 factors
- Main content area with markdown rendering
- Search functionality for quick discovery
- Visual diagram cards for each factor

## 🤝 Contributing

This explorer is part of the 12-Factor Agents project. To contribute:

1. Make improvements to the UI or functionality
2. Add new features or API endpoints
3. Improve documentation
4. Report bugs or suggest enhancements

## 📄 License

Apache 2.0 - Same as the main 12-Factor Agents project

## 🔗 Related Links

- [Main 12-Factor Agents Repo](https://github.com/humanlayer/12-factor-agents)
- [Video Deep Dive](https://www.youtube.com/watch?v=yxJDyQ8v6P0)
- [AI Engineer Talk](https://www.youtube.com/watch?v=8kMaTybvDUw)
- [12 Factor Apps](https://12factor.net/)

---

**Made with 💜 for the AI agent community**
