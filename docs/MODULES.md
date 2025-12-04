# Module Documentation

## Core Modules

### 1. Core Processor Module (`app/core_processor.py`)

#### Overview
The central processing engine for document analysis, handling Word document parsing, character extraction, and statistical calculations.

#### Classes

##### `DocumentProcessor`
**Purpose**: Main document processing class

**Methods**:
- `process(source: Path, column_index: int = 1) -> ProcessingResult`
  - Process Word document and extract character data
  - Parameters: 
    - `source`: Path to Word document
    - `column_index`: Zero-based column index containing characters
  - Returns: ProcessingResult with characters and table data
  - Raises: FileNotFoundError, ValueError

- `summarise(characters: Iterable[str], ignore_case: bool = False) -> List[CharacterStat]`
  - Convert character list to frequency statistics
  - Parameters:
    - `characters`: Iterable of character names
    - `ignore_case`: Whether to merge case-insensitive names
  - Returns: Sorted list of CharacterStat objects

- `export_report(result: ProcessingResult, output_path: Path, minimum_mentions: int = 1, ignore_case: bool = False) -> Path`
  - Generate Word document report with analysis results
  - Parameters:
    - `result`: ProcessingResult to export
    - `output_path`: Path where to save the report
    - `minimum_mentions`: Filter characters below this count
    - `ignore_case`: Case-insensitive processing
  - Returns: Path to created report file

- `get_table_preview(source: Path, max_rows: int = 5) -> List[List[str]]`
  - Get preview of document table structure
  - Useful for UI display and user guidance

##### `CharacterStat`
**Purpose**: Data class for character frequency information
**Fields**:
- `name: str` - Character name
- `count: int` - Number of mentions

##### `TableData`
**Purpose**: Representation of Word table structure
**Fields**:
- `rows: List[List[str]]` - Table cell contents

##### `ProcessingResult`
**Purpose**: Complete processing output container
**Fields**:
- `characters: List[str]` - Extracted character names
- `tables: List[TableData]` - Original table structures

#### Usage Examples

```python
from app.core_processor import DocumentProcessor

# Initialize processor
processor = DocumentProcessor()

# Process document
result = processor.process("document.docx", column_index=1)

# Get statistics
stats = processor.summarise(result.characters, ignore_case=True)

# Filter and export
filtered_stats = [stat for stat in stats if stat.count >= 2]
processor.export_report(result, "report.docx", minimum_mentions=2)
```

### 2. Desktop GUI Modules

#### Simple GUI (`app/simple_gui.py`)

##### `CharacterAnalysisGUI`
**Purpose**: Clean, minimal desktop interface

**Key Features**:
- Standard Tkinter widgets
- Basic file selection
- Simple configuration options
- Results table display
- Clipboard integration

**Main Methods**:
- `select_file()` - File dialog for document selection
- `analyze_document()` - Trigger document processing
- `copy_results()` - Copy results to clipboard
- `_display_results()` - Update results table

#### Enhanced GUI (`app/enhanced_gui.py`)

##### `ModernCharacterAnalysisGUI`
**Purpose**: Modern, animated desktop interface

**Advanced Features**:
- Custom animated buttons
- Real-time progress bars
- Modern card-based layout
- Smooth animations
- Professional styling

**Custom Components**:
- `AnimatedButton` - Custom button with hover effects
- `AnimatedProgressBar` - Smooth progress indication
- Modern color schemes and typography

### 3. Web Interface Module (`app/web_interface.py`)

#### Flask Application Structure

##### Main Application (`app`)
**Purpose**: Flask web application instance

**Routes**:
- `GET /` - Main interface
- `POST /analyze` - Document analysis
- `GET /export/<session_id>` - Report download
- `GET /health` - Health check

##### Key Functions

###### `analyze_document()`
**Purpose**: Handle document analysis via web interface
**Process**:
1. Validate file upload
2. Save temporary file
3. Process with DocumentProcessor
4. Create session
5. Return JSON results

###### `export_results(session_id)`
**Purpose**: Generate and serve report file
**Process**:
1. Validate session
2. Generate report
3. Stream file to client

##### Frontend JavaScript (`WordAnalyzer` class)
**Purpose**: Client-side interface management
**Features**:
- File drag & drop
- Progress tracking
- Results display
- Export functionality

### 4. Legacy Modules

#### Original Processor (`app/processor.py`)
**Purpose**: Legacy processing logic (maintained for compatibility)
**Status**: Replaced by `core_processor.py`

#### Original GUI (`app/gui.py`)
**Purpose**: Original desktop interface (maintained for compatibility)
**Status**: Replaced by `simple_gui.py` and `enhanced_gui.py`

### 5. Optional Modules

#### Google Sheets Integration (`app/google_sheets.py`)
**Purpose**: Export results to Google Sheets
**Requirements**: Google API credentials

**Main Class**: `GoogleSheetsProcessor`
- `authenticate()` - Google API authentication
- `export_characters()` - Export to Sheets
- `import_from_sheets()` - Import from Sheets

#### AI Analysis (`app/ai_analysis.py`)
**Purpose**: AI-powered character analysis
**Requirements**: Transformers library

**Main Classes**:
- `SimpleTextAnalyzer` - Rule-based analysis
- `AdvancedAIAnalyzer` - ML-based analysis
- `AIAnalysisManager` - Analysis coordination

#### Authentication (`app/auth.py`)
**Purpose**: User authentication system
**Requirements**: Flask, SQLAlchemy

**Main Classes**:
- `SimpleAuthManager` - User management
- `FlaskAuthAPI` - Web authentication
- `APILimiter` - Rate limiting

## Module Dependencies

### Dependency Graph
```
app/
├── core_processor.py (Core)
├── simple_gui.py → core_processor.py
├── enhanced_gui.py → simple_gui.py, core_processor.py
├── web_interface.py → core_processor.py
├── google_sheets.py → core_processor.py (optional)
├── ai_analysis.py → core_processor.py (optional)
└── auth.py (optional)
```

### Core Dependencies
- **Required**: `python-docx`, `tkinter` (built-in)
- **Optional**: `flask`, `transformers`, `google-api-python-client`

## Error Handling

### Exception Hierarchy
```
ProcessingError (base)
├── FileNotFoundError
├── ValueError (invalid parameters)
├── DocumentError (parsing failures)
└── ExportError (output failures)
```

### Error Patterns
1. **Input Validation**: Check file existence, format
2. **Graceful Degradation**: Fallback to basic functionality
3. **User Feedback**: Clear error messages
4. **Recovery**: Retry mechanisms where appropriate

## Configuration

### Module-Specific Settings

#### Core Processor
```python
# Default column index
DEFAULT_COLUMN_INDEX = 1

# Case sensitivity default
DEFAULT_IGNORE_CASE = True

# Minimum mentions default
DEFAULT_MIN_MENTIONS = 1
```

#### Web Interface
```python
# File upload limits
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'.docx'}

# Session settings
SESSION_TIMEOUT = 3600  # 1 hour
```

#### GUI Applications
```python
# Window dimensions
DEFAULT_WINDOW_SIZE = "1000x700"

# Update intervals
PROGRESS_UPDATE_INTERVAL = 100  # milliseconds
```

## Performance Considerations

### Memory Usage
- **Document Processing**: Load tables sequentially
- **GUI Applications**: Minimize memory footprint
- **Web Interface**: Session cleanup after timeout

### Processing Speed
- **Optimized Parsing**: Direct table access
- **Background Processing**: Non-blocking UI
- **Caching**: Session data in web interface

## Testing Guidelines

### Unit Testing
Each module should have comprehensive unit tests:
- Input validation
- Edge cases
- Error conditions
- Core functionality

### Integration Testing
Test module interactions:
- GUI → Processor communication
- Web interface → Backend processing
- Data flow verification

### Performance Testing
Monitor resource usage:
- Memory consumption
- Processing time
- UI responsiveness

## Extension Points

### Adding New Document Types
1. Extend `DocumentProcessor`
2. Add format detection
3. Implement parsing logic
4. Update validation

### Adding New Analysis Features
1. Extend processing pipeline
2. Add result data structures
3. Update export functionality
4. Enhance UI components

### Adding New Interfaces
1. Implement `DocumentProcessor` interface
2. Add input handling
3. Implement result display
4. Add error handling

## API Reference

### Core Processor API
See individual class documentation above for complete method signatures and examples.

### GUI API
- Window management methods
- Event handling patterns
- Data binding conventions
- Animation control methods

### Web API
- RESTful endpoint specifications
- Request/response formats
- Error response codes
- Authentication requirements

## Best Practices

### Code Organization
- Single responsibility principle
- Clear module boundaries
- Consistent naming conventions
- Comprehensive documentation

### Error Handling
- Specific exception types
- Clear error messages
- Graceful degradation
- User-friendly feedback

### Performance
- Lazy loading where appropriate
- Memory management
- Background processing
- Efficient algorithms

### Security
- Input validation
- File type checking
- Path sanitization
- Session management