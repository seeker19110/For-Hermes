#!/bin/bash

echo "🚀 Starting 12-Factor Agents Explorer..."
echo ""
echo "This will start the interactive GUI for exploring all 12 factors"
echo "of building reliable LLM applications."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
npm run dev
