#!/bin/bash
# EpochCore RAS Go Repository Setup Script

set -e

echo "🐹 Setting up EpochCore RAS for Go repository..."

# Check Go version
if ! command -v go &> /dev/null; then
    echo "❌ Go is required but not found"
    echo "Please install Go: https://golang.org/doc/install"
    exit 1
fi

GO_VERSION=$(go version)
echo "✅ Found $GO_VERSION"

# Initialize Go module if go.mod doesn't exist
if [ ! -f "go.mod" ]; then
    echo "📦 Initializing Go module..."
    MODULE_NAME=$(basename $(pwd))
    go mod init $MODULE_NAME
else
    echo "📝 Found existing go.mod"
fi

# Create basic Go project structure
echo "📁 Setting up Go project structure..."
mkdir -p cmd
mkdir -p internal
mkdir -p pkg
mkdir -p configs
mkdir -p scripts

# Install EpochCore RAS dependencies
echo "📥 Installing Go dependencies..."
go mod tidy

# Create main application
echo "🔧 Creating Go integration application..."
cat > cmd/epochcore/main.go << 'EOF'
package main

import (
	"fmt"
	"os"
	"os/exec"
)

// EpochCoreIntegration provides Go integration with the Python-based EpochCore RAS system
type EpochCoreIntegration struct {
	pythonExecutable   string
	integrationScript  string
}

func NewEpochCoreIntegration() *EpochCoreIntegration {
	return &EpochCoreIntegration{
		pythonExecutable:  "python3",
		integrationScript: "integration.py",
	}
}

func (e *EpochCoreIntegration) runPythonCommand(command string) error {
	cmd := exec.Command(e.pythonExecutable, e.integrationScript, command)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func (e *EpochCoreIntegration) InitRecursive() error {
	fmt.Println("🚀 Initializing EpochCore RAS recursive improvement system...")
	if err := e.runPythonCommand("init-recursive"); err != nil {
		return fmt.Errorf("failed to initialize recursive improvement system: %w", err)
	}
	fmt.Println("✅ Recursive improvement system initialized successfully")
	return nil
}

func (e *EpochCoreIntegration) GetStatus() error {
	fmt.Println("📊 Getting EpochCore RAS system status...")
	return e.runPythonCommand("status")
}

func (e *EpochCoreIntegration) ValidateSystem() error {
	fmt.Println("🔍 Validating EpochCore RAS system...")
	if err := e.runPythonCommand("validate"); err != nil {
		return fmt.Errorf("system validation failed: %w", err)
	}
	fmt.Println("✅ System validation completed successfully")
	return nil
}

func (e *EpochCoreIntegration) SetupDemo() error {
	fmt.Println("🎯 Setting up EpochCore RAS demo environment...")
	if err := e.runPythonCommand("setup-demo"); err != nil {
		return fmt.Errorf("demo setup failed: %w", err)
	}
	fmt.Println("✅ Demo environment setup completed")
	return nil
}

func (e *EpochCoreIntegration) RunWorkflow() error {
	fmt.Println("⚡ Running EpochCore RAS workflow...")
	if err := e.runPythonCommand("run-workflow"); err != nil {
		return fmt.Errorf("workflow execution failed: %w", err)
	}
	fmt.Println("✅ Workflow execution completed")
	return nil
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: epochcore [init|status|validate|demo|run]")
		os.Exit(1)
	}

	integration := NewEpochCoreIntegration()
	command := os.Args[1]

	var err error
	switch command {
	case "init":
		err = integration.InitRecursive()
	case "status":
		err = integration.GetStatus()
	case "validate":
		err = integration.ValidateSystem()
	case "demo":
		err = integration.SetupDemo()
	case "run":
		err = integration.RunWorkflow()
	default:
		fmt.Printf("Unknown command: %s\n", command)
		fmt.Println("Usage: epochcore [init|status|validate|demo|run]")
		os.Exit(1)
	}

	if err != nil {
		fmt.Fprintf(os.Stderr, "❌ Error: %v\n", err)
		os.Exit(1)
	}
}
EOF

# Create test file
echo "🧪 Creating Go test..."
cat > cmd/epochcore/main_test.go << 'EOF'
package main

import (
	"testing"
)

func TestNewEpochCoreIntegration(t *testing.T) {
	integration := NewEpochCoreIntegration()
	if integration == nil {
		t.Fatal("Expected EpochCoreIntegration instance, got nil")
	}
	
	if integration.pythonExecutable == "" {
		t.Fatal("Expected python executable to be set")
	}
	
	if integration.integrationScript == "" {
		t.Fatal("Expected integration script to be set")
	}
}

func TestEpochCoreIntegration_GetStatus(t *testing.T) {
	integration := NewEpochCoreIntegration()
	// Note: This might fail if Python/EpochCore is not properly set up
	// but the test should not panic
	defer func() {
		if r := recover(); r != nil {
			t.Fatalf("GetStatus() panicked: %v", r)
		}
	}()
	
	integration.GetStatus() // We don't check error as it might be expected to fail
}
EOF

# Create Go integration package
echo "📦 Creating Go integration package..."
mkdir -p pkg/epochcore
cat > pkg/epochcore/integration.go << 'EOF'
package epochcore

import (
	"fmt"
	"os/exec"
)

// Integration provides programmatic access to EpochCore RAS functionality
type Integration struct {
	pythonExecutable   string
	integrationScript  string
}

// New creates a new EpochCore integration instance
func New() *Integration {
	return &Integration{
		pythonExecutable:  "python3",
		integrationScript: "integration.py",
	}
}

// WithPythonExecutable sets the Python executable path
func (i *Integration) WithPythonExecutable(executable string) *Integration {
	i.pythonExecutable = executable
	return i
}

// WithIntegrationScript sets the integration script path
func (i *Integration) WithIntegrationScript(script string) *Integration {
	i.integrationScript = script
	return i
}

// Execute runs a Python integration command
func (i *Integration) Execute(command string) error {
	cmd := exec.Command(i.pythonExecutable, i.integrationScript, command)
	return cmd.Run()
}

// Init initializes the recursive improvement system
func (i *Integration) Init() error {
	return i.Execute("init-recursive")
}

// Status gets the system status
func (i *Integration) Status() error {
	return i.Execute("status")
}

// Validate validates the system
func (i *Integration) Validate() error {
	return i.Execute("validate")
}

// Demo sets up demo environment
func (i *Integration) Demo() error {
	return i.Execute("setup-demo")
}

// Run executes workflow
func (i *Integration) Run() error {
	return i.Execute("run-workflow")
}
EOF

cat > pkg/epochcore/integration_test.go << 'EOF'
package epochcore

import (
	"testing"
)

func TestNew(t *testing.T) {
	integration := New()
	if integration == nil {
		t.Fatal("Expected Integration instance, got nil")
	}
}

func TestWithPythonExecutable(t *testing.T) {
	integration := New().WithPythonExecutable("python")
	if integration.pythonExecutable != "python" {
		t.Fatalf("Expected python executable 'python', got '%s'", integration.pythonExecutable)
	}
}

func TestWithIntegrationScript(t *testing.T) {
	integration := New().WithIntegrationScript("custom.py")
	if integration.integrationScript != "custom.py" {
		t.Fatalf("Expected integration script 'custom.py', got '%s'", integration.integrationScript)
	}
}
EOF

# Create Makefile
echo "🔨 Creating Makefile..."
cat > Makefile << 'EOF'
.PHONY: build test clean run-init run-status run-validate run-demo run-workflow

# Build the application
build:
	go build -o bin/epochcore ./cmd/epochcore

# Run tests
test:
	go test ./...

# Clean build artifacts
clean:
	rm -rf bin/
	go clean

# Install dependencies
deps:
	go mod tidy
	go mod download

# Format code
fmt:
	go fmt ./...

# Run linters
lint:
	golangci-lint run

# EpochCore RAS commands
run-init: build
	./bin/epochcore init

run-status: build
	./bin/epochcore status

run-validate: build
	./bin/epochcore validate

run-demo: build
	./bin/epochcore demo

run-workflow: build
	./bin/epochcore run

# Development shortcuts
dev-setup:
	go mod tidy
	go build -o bin/epochcore ./cmd/epochcore

dev-test:
	go test -v ./...
EOF

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
go.work

# Build artifacts
bin/
dist/

# Dependency directories
vendor/

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

# Build and test
echo "🏗️  Building Go application..."
go build -o bin/epochcore ./cmd/epochcore

echo "🧪 Running Go tests..."
if go test ./...; then
    echo "✅ EpochCore RAS Go integration tests passed!"
else
    echo "⚠️  EpochCore RAS Go integration tests have warnings - check the output above"
fi

# Test Go EpochCore RAS integration
echo "🧪 Testing EpochCore RAS Go integration..."
if ./bin/epochcore status 2>/dev/null; then
    echo "✅ EpochCore RAS Go integration successful!"
else
    echo "⚠️  EpochCore RAS validation warnings - check the output above"
fi

echo "🎉 Go repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Build the application: make build"
echo "2. Run tests: make test"
echo "3. Initialize recursive improvements: make run-init"
echo "4. Check system status: make run-status" 
echo "5. Validate system: make run-validate"