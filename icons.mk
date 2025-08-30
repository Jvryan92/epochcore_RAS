# StrategyDECK Icon Generation System Makefile

# Directories
SCRIPT_DIR = scripts
ASSETS_DIR = assets
OUTPUT_DIR = $(ASSETS_DIR)/icons
MASTERS_DIR = $(ASSETS_DIR)/masters
CONFIG_DIR = config
DOCS_DIR = docs

# Python path
PYTHON = python3

# Scripts
GENERATE_SCRIPT = $(SCRIPT_DIR)/generate_icons.py
ENHANCED_SCRIPT = $(SCRIPT_DIR)/enhanced_icon_generator.py
PALETTE_SCRIPT = $(SCRIPT_DIR)/palette_manager.py
EXPORTER_SCRIPT = $(SCRIPT_DIR)/icon_framework_exporter.py
CLI_SCRIPT = $(SCRIPT_DIR)/strategydeck_cli.py
DEBUG_SCRIPT = debug_bake_svg.py

# Default target
.PHONY: all
all: clean generate

# Clean output directory
.PHONY: clean
clean:
	@echo "Cleaning output directory..."
	@rm -rf $(OUTPUT_DIR)/*
	@mkdir -p $(OUTPUT_DIR)

# Generate icons (basic)
.PHONY: generate
generate:
	@echo "Generating icons..."
	@$(PYTHON) $(GENERATE_SCRIPT)

# Generate icons with enhanced generator
.PHONY: generate-enhanced
generate-enhanced:
	@echo "Generating icons with enhanced generator..."
	@$(PYTHON) $(ENHANCED_SCRIPT) --csv

# Generate specific variants
.PHONY: generate-variant
generate-variant:
	@echo "Generating custom variant..."
	@$(PYTHON) $(ENHANCED_SCRIPT) --create-variant $(VARIANT)

# Optimize existing icons
.PHONY: optimize
optimize:
	@echo "Optimizing existing icons..."
	@$(PYTHON) $(ENHANCED_SCRIPT) --optimize-existing

# List color palettes
.PHONY: list-palettes
list-palettes:
	@echo "Listing color palettes..."
	@$(PYTHON) $(PALETTE_SCRIPT) --list

# Create a new color palette
.PHONY: create-palette
create-palette:
	@echo "Creating palette $(NAME)..."
	@$(PYTHON) $(PALETTE_SCRIPT) --create $(NAME) $(if $(COLOR),--base-color $(COLOR),)

# Edit a color palette
.PHONY: edit-palette
edit-palette:
	@echo "Editing palette $(NAME)..."
	@$(PYTHON) $(PALETTE_SCRIPT) --edit $(NAME)

# Preview a color palette
.PHONY: preview-palette
preview-palette:
	@echo "Previewing palette $(NAME)..."
	@$(PYTHON) $(PALETTE_SCRIPT) --preview $(NAME)

# Export icons for React
.PHONY: export-react
export-react:
	@echo "Exporting icons for React..."
	@$(PYTHON) $(EXPORTER_SCRIPT) --framework react --output ./dist/react-icons $(if $(OPTIMIZE),--optimize,)

# Export icons for Vue
.PHONY: export-vue
export-vue:
	@echo "Exporting icons for Vue..."
	@$(PYTHON) $(EXPORTER_SCRIPT) --framework vue --output ./dist/vue-icons $(if $(OPTIMIZE),--optimize,)

# Export icons for Svelte
.PHONY: export-svelte
export-svelte:
	@echo "Exporting icons for Svelte..."
	@$(PYTHON) $(EXPORTER_SCRIPT) --framework svelte --output ./dist/svelte-icons $(if $(OPTIMIZE),--optimize,)

# Export icons for all frameworks
.PHONY: export-all
export-all: export-react export-vue export-svelte
	@echo "Exported icons for all frameworks"

# Launch debug tool with GUI
.PHONY: debug-gui
debug-gui:
	@echo "Launching debugger GUI..."
	@$(PYTHON) $(DEBUG_SCRIPT) --gui

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	@pytest tests/ -v

# Run linting
.PHONY: lint
lint:
	@echo "Running linters..."
	@flake8 $(SCRIPT_DIR)/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@flake8 $(SCRIPT_DIR)/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Format code with black
.PHONY: format
format:
	@echo "Formatting code..."
	@black $(SCRIPT_DIR)/ tests/

# Check formatting with black
.PHONY: format-check
format-check:
	@echo "Checking code formatting..."
	@black --check $(SCRIPT_DIR)/ tests/

# Full validation sequence
.PHONY: validate
validate: clean generate test lint format-check
	@echo "Validation complete"

# Show system information
.PHONY: info
info:
	@echo "StrategyDECK Icon System Information"
	@$(PYTHON) $(CLI_SCRIPT) info

# Check dependencies
.PHONY: check-deps
check-deps:
	@echo "Checking dependencies..."
	@$(PYTHON) $(CLI_SCRIPT) info --dependencies

# Show icon statistics
.PHONY: stats
stats:
	@echo "Icon statistics..."
	@$(PYTHON) $(CLI_SCRIPT) info --stats

# Install required dependencies
.PHONY: install-deps
install-deps:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

# Help text
.PHONY: help
help:
	@echo "StrategyDECK Icon Generation System"
	@echo ""
	@echo "Available targets:"
	@echo "  all              - Clean and generate icons (default target)"
	@echo "  clean            - Clean output directory"
	@echo "  generate         - Generate icons using basic generator"
	@echo "  generate-enhanced - Generate icons using enhanced generator"
	@echo "  generate-variant - Generate custom variant (specify VARIANT=mode,finish,size,context)"
	@echo "  optimize         - Optimize existing icons"
	@echo ""
	@echo "  list-palettes    - List available color palettes"
	@echo "  create-palette   - Create a new color palette (specify NAME and optional COLOR)"
	@echo "  edit-palette     - Edit a color palette (specify NAME)"
	@echo "  preview-palette  - Preview a color palette (specify NAME)"
	@echo ""
	@echo "  export-react     - Export icons for React (optional OPTIMIZE=1)"
	@echo "  export-vue       - Export icons for Vue (optional OPTIMIZE=1)"
	@echo "  export-svelte    - Export icons for Svelte (optional OPTIMIZE=1)"
	@echo "  export-all       - Export icons for all frameworks"
	@echo ""
	@echo "  debug-gui        - Launch debug tool with GUI"
	@echo "  test             - Run tests"
	@echo "  lint             - Run linters"
	@echo "  format           - Format code with black"
	@echo "  format-check     - Check code formatting with black"
	@echo "  validate         - Run full validation sequence"
	@echo ""
	@echo "  info             - Show system information"
	@echo "  check-deps       - Check dependencies"
	@echo "  stats            - Show icon statistics"
	@echo "  install-deps     - Install required dependencies"
	@echo "  help             - Show this help message"
