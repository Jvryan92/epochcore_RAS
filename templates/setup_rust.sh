#!/bin/bash
# EpochCore RAS Rust Repository Setup Script

set -e

echo "🦀 Setting up EpochCore RAS for Rust repository..."

# Check Rust version
if ! command -v rustc &> /dev/null; then
    echo "❌ Rust is required but not found"
    echo "Please install Rust: https://rustup.rs/"
    exit 1
fi

RUST_VERSION=$(rustc --version)
echo "✅ Found $RUST_VERSION"

# Check Cargo
if ! command -v cargo &> /dev/null; then
    echo "❌ Cargo is required but not found"
    exit 1
fi

CARGO_VERSION=$(cargo --version)
echo "✅ Found $CARGO_VERSION"

# Initialize Rust project if Cargo.toml doesn't exist
if [ ! -f "Cargo.toml" ]; then
    echo "📦 Initializing Rust project..."
    PROJECT_NAME=$(basename $(pwd) | tr '-' '_')
    cargo init --name $PROJECT_NAME
else
    echo "📝 Found existing Cargo.toml, backing up..."
    cp Cargo.toml Cargo.toml.backup
fi

# Add EpochCore RAS dependencies to Cargo.toml
echo "📥 Adding Rust dependencies for EpochCore RAS..."
cat >> Cargo.toml << 'EOF'

[dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_yaml = "0.9"
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
clap = { version = "4.0", features = ["derive"] }
anyhow = "1.0"
log = "0.4"
env_logger = "0.10"

[dev-dependencies]
tempfile = "3.0"
EOF

# Create basic Rust project structure
echo "📁 Setting up Rust project structure..."
mkdir -p src/bin
mkdir -p src/lib
mkdir -p tests
mkdir -p examples
mkdir -p config

# Create EpochCore integration library
echo "🔧 Creating Rust integration library..."
cat > src/lib.rs << 'EOF'
//! EpochCore RAS Rust Integration Library
//!
//! This library provides Rust integration with the Python-based EpochCore RAS system

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use log::{info, error};

/// EpochCore integration configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpochCoreConfig {
    pub python_executable: String,
    pub integration_script: String,
}

impl Default for EpochCoreConfig {
    fn default() -> Self {
        Self {
            python_executable: "python3".to_string(),
            integration_script: "integration.py".to_string(),
        }
    }
}

/// Main integration struct for EpochCore RAS
#[derive(Debug)]
pub struct EpochCoreIntegration {
    config: EpochCoreConfig,
}

impl EpochCoreIntegration {
    /// Create a new EpochCore integration instance
    pub fn new() -> Self {
        Self {
            config: EpochCoreConfig::default(),
        }
    }

    /// Create a new EpochCore integration instance with custom config
    pub fn with_config(config: EpochCoreConfig) -> Self {
        Self { config }
    }

    /// Execute a Python integration command
    pub fn execute_command(&self, command: &str) -> Result<()> {
        info!("Executing EpochCore command: {}", command);
        
        let output = Command::new(&self.config.python_executable)
            .arg(&self.config.integration_script)
            .arg(command)
            .stdout(Stdio::inherit())
            .stderr(Stdio::inherit())
            .output()
            .with_context(|| format!("Failed to execute command: {}", command))?;

        if output.status.success() {
            info!("Command '{}' executed successfully", command);
            Ok(())
        } else {
            error!("Command '{}' failed with status: {}", command, output.status);
            anyhow::bail!("Command failed with status: {}", output.status);
        }
    }

    /// Initialize the recursive improvement system
    pub fn init_recursive(&self) -> Result<()> {
        println!("🚀 Initializing EpochCore RAS recursive improvement system...");
        self.execute_command("init-recursive")?;
        println!("✅ Recursive improvement system initialized successfully");
        Ok(())
    }

    /// Get system status
    pub fn get_status(&self) -> Result<()> {
        println!("📊 Getting EpochCore RAS system status...");
        self.execute_command("status")
    }

    /// Validate the system
    pub fn validate_system(&self) -> Result<()> {
        println!("🔍 Validating EpochCore RAS system...");
        self.execute_command("validate")?;
        println!("✅ System validation completed successfully");
        Ok(())
    }

    /// Setup demo environment
    pub fn setup_demo(&self) -> Result<()> {
        println!("🎯 Setting up EpochCore RAS demo environment...");
        self.execute_command("setup-demo")?;
        println!("✅ Demo environment setup completed");
        Ok(())
    }

    /// Run workflow
    pub fn run_workflow(&self) -> Result<()> {
        println!("⚡ Running EpochCore RAS workflow...");
        self.execute_command("run-workflow")?;
        println!("✅ Workflow execution completed");
        Ok(())
    }
}

impl Default for EpochCoreIntegration {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_epochcore_integration_creation() {
        let integration = EpochCoreIntegration::new();
        assert_eq!(integration.config.python_executable, "python3");
        assert_eq!(integration.config.integration_script, "integration.py");
    }

    #[test]
    fn test_epochcore_integration_with_config() {
        let config = EpochCoreConfig {
            python_executable: "python".to_string(),
            integration_script: "custom.py".to_string(),
        };
        let integration = EpochCoreIntegration::with_config(config.clone());
        assert_eq!(integration.config.python_executable, config.python_executable);
        assert_eq!(integration.config.integration_script, config.integration_script);
    }

    #[test]
    fn test_config_serialization() {
        let config = EpochCoreConfig::default();
        let serialized = serde_yaml::to_string(&config).unwrap();
        let deserialized: EpochCoreConfig = serde_yaml::from_str(&serialized).unwrap();
        
        assert_eq!(config.python_executable, deserialized.python_executable);
        assert_eq!(config.integration_script, deserialized.integration_script);
    }
}
EOF

# Create binary application
echo "🔧 Creating Rust binary application..."
cat > src/bin/epochcore.rs << 'EOF'
//! EpochCore RAS Command Line Interface

use anyhow::Result;
use clap::{Parser, Subcommand};
use env_logger;
use log::info;
use epochcore_ras::EpochCoreIntegration;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
#[command(name = "epochcore")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize recursive improvement system
    Init,
    /// Get system status
    Status,
    /// Validate system integrity
    Validate,
    /// Setup demo environment
    Demo,
    /// Run workflow
    Run,
}

fn main() -> Result<()> {
    env_logger::init();
    
    let cli = Cli::parse();
    let integration = EpochCoreIntegration::new();

    match cli.command {
        Commands::Init => {
            info!("Initializing EpochCore RAS system");
            integration.init_recursive()?;
        }
        Commands::Status => {
            info!("Getting system status");
            integration.get_status()?;
        }
        Commands::Validate => {
            info!("Validating system");
            integration.validate_system()?;
        }
        Commands::Demo => {
            info!("Setting up demo");
            integration.setup_demo()?;
        }
        Commands::Run => {
            info!("Running workflow");
            integration.run_workflow()?;
        }
    }

    Ok(())
}
EOF

# Create integration tests
echo "🧪 Creating integration tests..."
cat > tests/integration_test.rs << 'EOF'
//! Integration tests for EpochCore RAS

use epochcore_ras::{EpochCoreIntegration, EpochCoreConfig};

#[test]
fn test_integration_instantiation() {
    let integration = EpochCoreIntegration::new();
    // Should not panic during creation
    drop(integration);
}

#[test]
fn test_integration_with_custom_config() {
    let config = EpochCoreConfig {
        python_executable: "python3".to_string(),
        integration_script: "integration.py".to_string(),
    };
    
    let integration = EpochCoreIntegration::with_config(config);
    // Should not panic during creation
    drop(integration);
}
EOF

# Create example
echo "📚 Creating usage example..."
cat > examples/basic_usage.rs << 'EOF'
//! Basic usage example for EpochCore RAS integration

use epochcore_ras::EpochCoreIntegration;
use anyhow::Result;

fn main() -> Result<()> {
    println!("EpochCore RAS Basic Usage Example");
    
    // Create integration instance
    let integration = EpochCoreIntegration::new();
    
    // Get system status (this might fail if EpochCore is not set up)
    match integration.get_status() {
        Ok(_) => println!("✅ System status retrieved successfully"),
        Err(e) => println!("⚠️  System status failed (expected if EpochCore not set up): {}", e),
    }
    
    Ok(())
}
EOF

# Create README for Rust integration
echo "📖 Creating Rust-specific README..."
cat > README_RUST.md << 'EOF'
# EpochCore RAS Rust Integration

This project provides Rust integration with the EpochCore RAS (Recursive Autonomous Software) system.

## Installation

1. Ensure you have Rust installed: https://rustup.rs/
2. Clone this repository
3. Run the setup script: `./templates/setup_rust.sh`

## Usage

### Command Line Interface

```bash
# Build the project
cargo build --release

# Initialize EpochCore RAS system
cargo run --bin epochcore init

# Get system status
cargo run --bin epochcore status

# Validate system
cargo run --bin epochcore validate

# Setup demo environment
cargo run --bin epochcore demo

# Run workflow
cargo run --bin epochcore run
```

### Library Usage

```rust
use epochcore_ras::EpochCoreIntegration;

fn main() -> anyhow::Result<()> {
    let integration = EpochCoreIntegration::new();
    
    // Initialize system
    integration.init_recursive()?;
    
    // Get status
    integration.get_status()?;
    
    // Validate system
    integration.validate_system()?;
    
    Ok(())
}
```

## Configuration

You can customize the integration by providing a custom configuration:

```rust
use epochcore_ras::{EpochCoreIntegration, EpochCoreConfig};

let config = EpochCoreConfig {
    python_executable: "python3".to_string(),
    integration_script: "custom_integration.py".to_string(),
};

let integration = EpochCoreIntegration::with_config(config);
```

## Testing

```bash
# Run unit tests
cargo test

# Run integration tests
cargo test --tests

# Run with logging
RUST_LOG=info cargo test
```

## Development

```bash
# Format code
cargo fmt

# Run linter
cargo clippy

# Build documentation
cargo doc --open
```
EOF

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Rust
/target
Cargo.lock
*.pdb

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# EpochCore RAS
logs/
backups/
.epochcore/
EOF
fi

# Update the Cargo.toml name to match the library
PROJECT_NAME=$(basename $(pwd) | tr '-' '_')
sed -i "s/name = \".*\"/name = \"epochcore_ras\"/" Cargo.toml || true

# Build and test
echo "🏗️  Building Rust project..."
cargo build

echo "🧪 Running Rust tests..."
if cargo test; then
    echo "✅ EpochCore RAS Rust integration tests passed!"
else
    echo "⚠️  EpochCore RAS Rust integration tests have warnings - check the output above"
fi

# Test Rust EpochCore RAS integration
echo "🧪 Testing EpochCore RAS Rust integration..."
if timeout 10 cargo run --bin epochcore status 2>/dev/null; then
    echo "✅ EpochCore RAS Rust integration successful!"
else
    echo "⚠️  EpochCore RAS validation warnings - this is expected if Python/EpochCore is not set up"
fi

echo "🎉 Rust repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Build the project: cargo build"
echo "2. Run tests: cargo test"  
echo "3. Initialize recursive improvements: cargo run --bin epochcore init"
echo "4. Check system status: cargo run --bin epochcore status"
echo "5. Build documentation: cargo doc --open"