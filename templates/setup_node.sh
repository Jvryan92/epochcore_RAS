#!/bin/bash
# EpochCore RAS Node.js Repository Setup Script

set -e

echo "🟢 Setting up EpochCore RAS for Node.js repository..."

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not found"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Found Node.js $NODE_VERSION"

# Check npm version
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not found"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✅ Found npm $NPM_VERSION"

# Install/update package.json
echo "📦 Setting up package.json..."
if [ -f "package.json" ]; then
    echo "📝 Found existing package.json, backing up..."
    cp package.json package.json.backup
    
    # Add EpochCore RAS scripts
    npm pkg set scripts.epochcore:init="node -e \"require('./integration.js').initRecursive()\""
    npm pkg set scripts.epochcore:status="node -e \"require('./integration.js').getStatus()\""
    npm pkg set scripts.epochcore:validate="node -e \"require('./integration.js').validateSystem()\""
    npm pkg set scripts.test:epochcore="npm run epochcore:validate"
else
    # Create new package.json
    npm init -y
    
    # Add EpochCore RAS specific configuration
    npm pkg set scripts.epochcore:init="node -e \"require('./integration.js').initRecursive()\""
    npm pkg set scripts.epochcore:status="node -e \"require('./integration.js').getStatus()\""
    npm pkg set scripts.epochcore:validate="node -e \"require('./integration.js').validateSystem()\""
    npm pkg set scripts.test:epochcore="npm run epochcore:validate"
fi

# Install EpochCore RAS dependencies
echo "📥 Installing EpochCore RAS dependencies..."
npm install --save-dev \
    jest \
    eslint \
    prettier \
    yaml \
    @octokit/rest \
    axios

# Install runtime dependencies
npm install --save \
    js-yaml \
    node-cron \
    fs-extra \
    chalk

# Create Jest configuration
echo "🧪 Setting up Jest testing..."
if [ ! -f "jest.config.js" ]; then
    cat > jest.config.js << EOF
module.exports = {
  testEnvironment: 'node',
  collectCoverage: true,
  coverageDirectory: 'coverage',
  testMatch: [
    '**/__tests__/**/*.js',
    '**/?(*.)+(spec|test).js'
  ],
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
};
EOF
fi

# Create Jest setup file
if [ ! -f "jest.setup.js" ]; then
    cat > jest.setup.js << EOF
// Jest setup for EpochCore RAS
const { performance } = require('perf_hooks');

global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: console.warn,
  error: console.error,
};

// EpochCore RAS test utilities
global.EpochCore = {
  testStartTime: performance.now(),
  getTestDuration: () => performance.now() - global.EpochCore.testStartTime
};
EOF
fi

# Create ESLint configuration
echo "🔍 Setting up ESLint..."
if [ ! -f ".eslintrc.js" ]; then
    cat > .eslintrc.js << EOF
module.exports = {
  env: {
    node: true,
    es2021: true,
    jest: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'module',
  },
  rules: {
    'no-console': 'warn',
    'no-unused-vars': 'error',
    'no-undef': 'error',
  },
  ignorePatterns: [
    'node_modules/',
    'dist/',
    'coverage/',
    'recursive_improvement/',
  ],
};
EOF
fi

# Create Prettier configuration
if [ ! -f ".prettierrc" ]; then
    cat > .prettierrc << EOF
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
EOF
fi

# Create basic Node.js project structure
echo "📁 Setting up Node.js project structure..."
mkdir -p tests
mkdir -p src
mkdir -p lib
mkdir -p config
mkdir -p __tests__

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test

# EpochCore RAS
logs/
backups/
.epochcore/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
fi

# Create JavaScript integration wrapper
echo "🔧 Creating JavaScript integration wrapper..."
cat > integration.js << EOF
/**
 * EpochCore RAS JavaScript Integration Wrapper
 * This file provides Node.js integration with the Python-based EpochCore RAS system
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class EpochCoreIntegration {
  constructor() {
    this.pythonExecutable = 'python3';
    this.integrationScript = path.join(__dirname, 'integration.py');
  }

  async runPythonCommand(command) {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn(this.pythonExecutable, [this.integrationScript, command], {
        cwd: __dirname,
        stdio: 'inherit'
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true, code });
        } else {
          reject({ success: false, code, error: \`Process exited with code \${code}\` });
        }
      });

      pythonProcess.on('error', (error) => {
        reject({ success: false, error: error.message });
      });
    });
  }

  async initRecursive() {
    console.log('🚀 Initializing EpochCore RAS recursive improvement system...');
    try {
      await this.runPythonCommand('init-recursive');
      console.log('✅ Recursive improvement system initialized successfully');
      return { success: true };
    } catch (error) {
      console.error('❌ Failed to initialize recursive improvement system:', error);
      return { success: false, error };
    }
  }

  async getStatus() {
    console.log('📊 Getting EpochCore RAS system status...');
    try {
      await this.runPythonCommand('status');
      return { success: true };
    } catch (error) {
      console.error('❌ Failed to get system status:', error);
      return { success: false, error };
    }
  }

  async validateSystem() {
    console.log('🔍 Validating EpochCore RAS system...');
    try {
      await this.runPythonCommand('validate');
      console.log('✅ System validation completed successfully');
      return { success: true };
    } catch (error) {
      console.error('❌ System validation failed:', error);
      return { success: false, error };
    }
  }

  async setupDemo() {
    console.log('🎯 Setting up EpochCore RAS demo environment...');
    try {
      await this.runPythonCommand('setup-demo');
      console.log('✅ Demo environment setup completed');
      return { success: true };
    } catch (error) {
      console.error('❌ Demo setup failed:', error);
      return { success: false, error };
    }
  }

  async runWorkflow() {
    console.log('⚡ Running EpochCore RAS workflow...');
    try {
      await this.runPythonCommand('run-workflow');
      console.log('✅ Workflow execution completed');
      return { success: true };
    } catch (error) {
      console.error('❌ Workflow execution failed:', error);
      return { success: false, error };
    }
  }
}

// Export for use in other modules
module.exports = new EpochCoreIntegration();

// CLI usage
if (require.main === module) {
  const command = process.argv[2];
  const integration = new EpochCoreIntegration();

  switch (command) {
    case 'init':
      integration.initRecursive();
      break;
    case 'status':
      integration.getStatus();
      break;
    case 'validate':
      integration.validateSystem();
      break;
    case 'demo':
      integration.setupDemo();
      break;
    case 'run':
      integration.runWorkflow();
      break;
    default:
      console.log('Usage: node integration.js [init|status|validate|demo|run]');
  }
}
EOF

# Test Node.js EpochCore RAS integration
echo "🧪 Testing EpochCore RAS Node.js integration..."
if node integration.js validate; then
    echo "✅ EpochCore RAS Node.js integration successful!"
else
    echo "⚠️  EpochCore RAS validation warnings - check the output above"
fi

echo "🎉 Node.js repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Run tests: npm test"
echo "2. Initialize recursive improvements: npm run epochcore:init"
echo "3. Check system status: npm run epochcore:status"
echo "4. Run EpochCore validation: npm run test:epochcore"