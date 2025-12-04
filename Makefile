# Makefile for Word Character Analyzer

.PHONY: help install install-dev test run clean docs setup-env

# Default target
help:
	@echo "Word Character Analyzer - Development Commands"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  setup-env      - Create Python virtual environment"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run            - Run the application"
	@echo "  test           - Run tests"
	@echo "  test-watch     - Run tests in watch mode"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code"
	@echo ""
	@echo "Build and Deploy:"
	@echo "  build          - Build documentation"
	@echo "  clean          - Clean build artifacts"
	@echo "  package        - Create distribution package"
	@echo ""
	@echo "Web Interface:"
	@echo "  web            - Start web interface (if Flask is installed)"

# Environment setup
setup-env:
	@echo "Setting up Python virtual environment..."
	python3 -m venv .venv
	@echo "Activating virtual environment..."
	@. .venv/bin/activate && pip install --upgrade pip

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy
	pip install -e .

# Run the application
run:
	@echo "Starting Word Character Analyzer..."
	python3 window-strat-app.py

# Run with virtual environment
run-venv:
	@. .venv/bin/activate && python window-strat-app.py

# Run tests
test:
	@echo "Running tests..."
	python3 -m pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	python3 -m pytest tests/ --cov=app --cov-report=html --cov-report=term

# Watch tests (requires pytest-watch)
test-watch:
	@echo "Running tests in watch mode..."
	python3 -m pytest tests/ --tb=short -f

# Code formatting
format:
	@echo "Formatting code..."
	black app/ tests/ *.py
	isort app/ tests/ *.py

# Linting
lint:
	@echo "Running linting..."
	flake8 app/ tests/ *.py
	mypy app/ --ignore-missing-imports

# Build documentation
docs:
	@echo "Building documentation..."
	mkdir -p docs
	@echo "# Word Character Analyzer Documentation" > docs/README.md
	@echo "" >> docs/README.md
	@echo "## API Documentation" >> docs/README.md
	@echo "Run 'python -m pydoc -w app.core_processor' to generate docs" >> docs/README.md

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf docs/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Package for distribution
package:
	@echo "Creating distribution package..."
	python3 setup.py sdist bdist_wheel

# Web interface (if Flask is available)
web:
	@echo "Checking for Flask..."
	@python3 -c "import flask" 2>/dev/null || (echo "Flask not installed. Run 'pip install flask' first." && exit 1)
	@echo "Starting web interface..."
	@python3 -c "from app.auth import create_auth_api, create_auth_system; from app.google_sheets import GoogleSheetsProcessor; api = create_auth_api(create_auth_system()); api.run(debug=True)"

# Development server with auto-reload
dev:
	@echo "Starting development server with auto-reload..."
	@. .venv/bin/activate && python window-strat-app.py

# Install web dependencies (optional)
install-web:
	@echo "Installing web interface dependencies..."
	pip install flask flask-socketio eventlet

# Create test Word document for testing
create-test-doc:
	@echo "Creating test document..."
	python3 -c "
from docx import Document
doc = Document()
doc.add_heading('Test Document for Character Analysis', 0)
table = doc.add_table(rows=4, cols=3)
table.style = 'Table Grid'
headers = ['ID', 'Character', 'Description']
for i, header in enumerate(headers):
    table.cell(0, i).text = header
data = [['1', 'Alice', 'Main protagonist'], ['2', 'Bob', 'Supporting character'], ['3', 'Charlie', 'Minor character']]
for i, row_data in enumerate(data, 1):
    for j, cell_data in enumerate(row_data):
        table.cell(i, j).text = cell_data
doc.save('test_document.docx')
print('Created test_document.docx')
"

# Security check
security:
	@echo "Running security checks..."
	@python3 -c "import safety; safety.check()" || echo "Safety not installed. Install with: pip install safety"

# Performance profiling
profile:
	@echo "Running performance analysis..."
	python3 -m cProfile -o profile.stats window-strat-app.py
	@echo "Profile saved to profile.stats"
	@echo "View with: python3 -m pstats profile.stats"

# Update todo progress
todo:
	@echo "Current task progress:"
	@echo "1. ✅ Analyze project architecture - COMPLETED"
	@echo "2. ✅ Clean up dependencies - COMPLETED"
	@echo "3. ⏳ Create documentation - IN PROGRESS"
	@echo "4. ⏳ Add testing suite - IN PROGRESS"
	@echo "5. ⏳ Set up git repository - PENDING"
	@echo "6. ⏳ Fix import issues - PENDING"