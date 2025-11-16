# 12-Factor Agents Explorer

An interactive web-based GUI for exploring and understanding the 12-Factor Agents principles for building reliable LLM applications.

## Features

- 🎨 **Beautiful Interactive UI** - Modern, gradient-based design with smooth animations
- 📚 **All 12 Factors** - Complete content from all 12 factors with markdown rendering
- 🔍 **Search Functionality** - Quickly find topics across all factors
- 🖼️ **Visual Navigation** - Browse factors using visual diagram cards
- 📖 **Markdown Rendering** - Full support for code blocks, images, and formatting
- 🎯 **Responsive Design** - Works on desktop and mobile devices
- ⚡ **Fast & Lightweight** - Built with vanilla JavaScript and Express

## Quick Start

### Installation

```bash
cd explorer
npm install
```

### Run Development Server

```bash
npm run dev
```

The explorer will be available at http://localhost:3100

### Build for Production

```bash
npm run build
npm start
```

## Usage

1. **Navigate Factors** - Click on any factor in the left sidebar
2. **Visual Browse** - Click on diagram cards in the welcome screen
3. **Search** - Use the search box to find specific topics
4. **Read Content** - All factor content is rendered as formatted markdown

## API Endpoints

The explorer server provides several API endpoints:

- `GET /api/factors` - List all 12 factors
- `GET /api/content/:slug` - Get markdown content for a factor
- `GET /api/image/:factorId` - Get diagram image for a factor
- `GET /api/search?q=query` - Search across all factor content
- `GET /api/examples/:factor` - Get code examples for a specific factor

## Project Structure

```
explorer/
├── public/
│   └── index.html          # Main HTML interface
├── src/
│   └── server.ts           # Express server with API endpoints
├── package.json
├── tsconfig.json
└── README.md
```

## Technologies Used

- **Frontend**: Vanilla JavaScript, HTML5, CSS3, Marked.js
- **Backend**: Express.js, TypeScript
- **Build Tools**: TSX, TypeScript Compiler

## Contributing

This explorer is part of the 12-Factor Agents project. Contributions are welcome!

## License

Apache 2.0 - See LICENSE file for details

## Links

- [12-Factor Agents Main Repository](https://github.com/humanlayer/12-factor-agents)
- [Documentation](https://github.com/humanlayer/12-factor-agents#readme)
- [Video Deep Dive](https://www.youtube.com/watch?v=yxJDyQ8v6P0)
