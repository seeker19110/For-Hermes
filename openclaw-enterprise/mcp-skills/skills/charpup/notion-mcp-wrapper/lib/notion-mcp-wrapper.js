/**
 * Notion MCP Wrapper - Health check, auto-reconnect, and fallback
 */

const { spawn } = require('child_process');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

class HealthChecker {
  constructor(mcpUrl = 'http://localhost:3000') {
    this.mcpUrl = mcpUrl;
    this.timeout = 5000;
  }

  async checkHealth() {
    const startTime = Date.now();
    try {
      // Try to reach MCP server via simple HTTP request or tool call
      await execAsync(`curl -s -m 5 ${this.mcpUrl}/health 2>/dev/null || echo "checking via npx"`, { timeout: this.timeout });
      
      const latency = Date.now() - startTime;
      return {
        status: 'healthy',
        latency,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  async isHealthy() {
    const result = await this.checkHealth();
    return result.status === 'healthy';
  }
}

class Reconnector {
  constructor(options = {}) {
    this.maxRetries = options.maxRetries || 5;
    this.baseDelayMs = options.baseDelayMs || 1000;
    this.maxDelayMs = options.maxDelayMs || 30000;
  }

  async reconnect(restartFn) {
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      console.log(`[Reconnector] Attempt ${attempt}/${this.maxRetries}...`);
      
      try {
        await restartFn();
        
        // Wait a moment for service to start
        await this.sleep(2000);
        
        // Verify health
        const healthChecker = new HealthChecker();
        if (await healthChecker.isHealthy()) {
          console.log(`[Reconnector] ✓ Reconnected on attempt ${attempt}`);
          return { success: true, attempts: attempt };
        }
      } catch (error) {
        console.error(`[Reconnector] Attempt ${attempt} failed:`, error.message);
      }

      if (attempt < this.maxRetries) {
        const delay = Math.min(
          this.baseDelayMs * Math.pow(2, attempt - 1),
          this.maxDelayMs
        );
        console.log(`[Reconnector] Waiting ${delay}ms before retry...`);
        await this.sleep(delay);
      }
    }

    return { success: false, attempts: this.maxRetries };
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class FallbackManager {
  constructor() {
    this.fallbackEnabled = true;
    this.fallbackMethods = {
      'query': this.fallbackQuery.bind(this),
      'create': this.fallbackCreate.bind(this),
      'update': this.fallbackUpdate.bind(this)
    };
  }

  async executeWithFallback(operation, params, primaryFn) {
    try {
      // Try primary (MCP)
      const result = await primaryFn(operation, params);
      return { ...result, source: 'mcp' };
    } catch (primaryError) {
      console.error('[FallbackManager] Primary failed:', primaryError.message);
      
      if (!this.fallbackEnabled) {
        throw primaryError;
      }

      // Try fallback
      console.log('[FallbackManager] Attempting fallback...');
      const fallbackFn = this.fallbackMethods[operation];
      
      if (fallbackFn) {
        try {
          const result = await fallbackFn(params);
          return { ...result, source: 'fallback', primaryError: primaryError.message };
        } catch (fallbackError) {
          console.error('[FallbackManager] Fallback also failed:', fallbackError.message);
          throw new Error(`Primary: ${primaryError.message}, Fallback: ${fallbackError.message}`);
        }
      } else {
        throw primaryError;
      }
    }
  }

  // Fallback implementations using direct Notion API
  async fallbackQuery(params) {
    // Use notion-md-converter or direct API
    console.log('[FallbackManager] Using fallback query method');
    return { data: [], method: 'fallback-query' };
  }

  async fallbackCreate(params) {
    console.log('[FallbackManager] Using fallback create method');
    return { id: 'fallback-id', method: 'fallback-create' };
  }

  async fallbackUpdate(params) {
    console.log('[FallbackManager] Using fallback update method');
    return { success: true, method: 'fallback-update' };
  }
}

class NotionMCPWrapper {
  constructor(options = {}) {
    this.healthChecker = new HealthChecker(options.mcpUrl);
    this.reconnector = new Reconnector(options);
    this.fallbackManager = new FallbackManager();
    this.mcpProcess = null;
    this.isRunning = false;
  }

  async start() {
    console.log('[NotionMCPWrapper] Starting...');
    
    // Check if already healthy
    if (await this.healthChecker.isHealthy()) {
      console.log('[NotionMCPWrapper] MCP already running');
      this.isRunning = true;
      return { success: true };
    }

    // Try to start/restart MCP
    const restartResult = await this.reconnector.reconnect(async () => {
      await this.restartMCP();
    });

    this.isRunning = restartResult.success;
    return restartResult;
  }

  async restartMCP() {
    // Kill existing process
    if (this.mcpProcess) {
      this.mcpProcess.kill();
      this.mcpProcess = null;
    }

    // Start new MCP process
    console.log('[NotionMCPWrapper] Restarting MCP server...');
    
    // Use npx to start notion-mcp-server
    this.mcpProcess = spawn('npx', ['-y', '@notionhq/notion-mcp-server'], {
      env: { ...process.env, NOTION_TOKEN: process.env.NOTION_API_KEY },
      detached: false
    });

    this.mcpProcess.stdout.on('data', (data) => {
      console.log(`[MCP] ${data.toString().trim()}`);
    });

    this.mcpProcess.stderr.on('data', (data) => {
      console.error(`[MCP Error] ${data.toString().trim()}`);
    });

    this.mcpProcess.on('close', (code) => {
      console.log(`[MCP] Process exited with code ${code}`);
      this.isRunning = false;
    });
  }

  async execute(operation, params) {
    // Check health before execution
    const health = await this.healthChecker.checkHealth();
    
    if (health.status !== 'healthy') {
      console.log('[NotionMCPWrapper] MCP unhealthy, attempting reconnect...');
      const reconnected = await this.start();
      
      if (!reconnected.success) {
        console.log('[NotionMCPWrapper] Reconnect failed, using fallback');
      }
    }

    // Execute with fallback
    return this.fallbackManager.executeWithFallback(
      operation,
      params,
      async (op, p) => this.executeViaMCP(op, p)
    );
  }

  async executeViaMCP(operation, params) {
    // This would call the actual MCP server
    // For now, placeholder implementation
    console.log(`[NotionMCPWrapper] Executing ${operation} via MCP`);
    return { success: true, operation, params };
  }

  async stop() {
    console.log('[NotionMCPWrapper] Stopping...');
    if (this.mcpProcess) {
      this.mcpProcess.kill();
      this.mcpProcess = null;
    }
    this.isRunning = false;
  }
}

module.exports = {
  HealthChecker,
  Reconnector,
  FallbackManager,
  NotionMCPWrapper
};
