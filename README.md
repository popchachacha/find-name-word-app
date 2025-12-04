📄 Multi-Format Document Processing

Word documents (.docx): Full support for tables, formatting, images
PDF files: Text and table extraction from PDF documents
Text files (.txt): Analysis of plain text documents
LibreOffice documents (.odt, .ods): Support for LibreOffice formats
Excel files (.xlsx): Analysis of spreadsheets with characters
RTF documents: Processing of formatted text

🎯 Smart Data Extraction

Automatic table detection: Intelligent recognition of document structure
Multi-language support: Russian, English, and other languages
OCR for images: Text extraction from images in documents
Audio analysis: Speech-to-text conversion for audio documents
Complex table processing: Merged cells, nested tables

📊 Advanced Analysis

Frequency analysis: Character mention counting with percentages
Relationship analysis: How characters interact with each other
Emotional analysis: Character moods and emotions
Timeline: Character appearances over time
Network visualization: Relationship graphs between characters

🤖 AI and Machine Learning

Automatic categorization: Determining character types (hero, antagonist, secondary)
Sentiment analysis: Tracking character emotions throughout the document
Predictive analysis: Predicting character importance
Speech recognition: Audio-to-text conversion
OCR processing: Text extraction from images

🔗 Integrations and Export

Google Sheets: Export results to Google spreadsheets
Excel files: Report generation in .xlsx format
PDF reports: Generate PDFs with charts and diagrams
JSON/API: Programmatic access to results
Visualization: Create graphs and network diagrams

📱 Modern Interfaces

🖥️ Desktop application: Modern Tkinter GUI with smooth animations
🌐 Web interface: Responsive web application with real-time progress
📱 Mobile version: Optimized for all screen sizes
💻 Terminal: Command line for batch processing
🔌 API: REST API for integration with other systems

✨ Advanced User Experience

Animations: Smooth transitions and visual feedback
Modern UI: Clean, intuitive design with professional styling
Real-time processing: Live progress indicators and status updates
Session management: Web interface with result persistence
Clipboard integration: One-click result copying
Dark theme: Support for light and dark interfaces
Multilingual: Interface in Russian and English

🏗️ Architecture
Clean, Modular Design
app/
├── core_processor.py      # Core document processing logic
├── simple_gui.py         # Clean desktop interface
├── enhanced_gui.py       # Animated desktop interface
├── web_interface.py      # Modern web application
├── processor.py          # Legacy processor (for compatibility)
├── google_sheets.py      # Google Sheets integration (optional)
├── ai_analysis.py        # AI-powered character analysis (optional)
└── auth.py              # Authentication system (optional)
Dependencies

Core: python-docx, pandas
Optional: flask, transformers, google-api-python-client
Development: pytest, black, flake8

🛠️ Installation
Quick Start
bash# Clone the repository
git clone https://github.com/yourusername/word-character-analyzer.git
cd word-character-analyzer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make install-dev  # Full development setup
# OR
pip install -r requirements.txt  # Production only

# Run the application
make run
Using Make (Recommended)
bashmake help          # Show all available commands
make setup-env     # Create virtual environment
make install       # Install production dependencies  
make install-dev   # Install development dependencies
make run          # Start desktop application
make test         # Run test suite
make web          # Start web interface (if Flask installed)
📖 Usage
🖥️ Desktop Application
bashpython window-strat-app.py
```

**Features:**
- Modern animated interface
- Drag-and-drop file support
- Real-time progress tracking
- Interactive results table
- One-click report generation

**Usage Examples:**

#### Analyzing Word Document with Tables
```
📄 Load: novel_characters.docx
⚙️ Settings: Column 2 (Names), Minimum 3 mentions
🎯 Result: 15 characters found
📊 Analysis: "Alice" - 45 times (23%), "Bob" - 32 times (16%)
```

#### Analyzing PDF Document
```
📄 Load: research_report.pdf
⚙️ Auto-detect tables
🎯 Result: 8 scientists found
📊 Export to Excel and Word formats
🌐 Web Interface
bashmake web
# OR
python -c "from app.web_interface import run_web_server; run_web_server()"
Features:

Responsive design
Session management
Real-time updates
Mobile compatibility
Drag-and-drop file upload

🐍 Python API
Basic Usage
pythonfrom app.core_processor import DocumentProcessor

# Create processor
processor = DocumentProcessor()

# Process Word document
result = processor.process("document.docx", column_index=1)
stats = processor.summarise(result.characters, ignore_case=True)

# Export report
processor.export_report(result, "output.docx", minimum_mentions=2)
Advanced Analysis
pythonfrom app.enhanced_analysis import AdvancedAnalyzer
from app.ai_integration import AICharacterAnalyzer

# AI character analysis
ai_analyzer = AICharacterAnalyzer()
character_analysis = ai_analyzer.analyze_characters(stats)

# Create relationship network graph
network_analyzer = NetworkAnalyzer()
relationships = network_analyzer.find_relationships(result.characters)

# Timeline of appearances
timeline = TimelineAnalyzer()
timeline_data = timeline.create_timeline(result.characters, result.tables)
Multiple Format Support
python# Word documents
word_processor = WordDocumentProcessor()
word_result = word_processor.process("story.docx")

# PDF files
pdf_processor = PDFProcessor()
pdf_result = pdf_processor.process("document.pdf", ocr_enabled=True)

# Excel files
excel_processor = ExcelProcessor()
excel_result = excel_processor.process("characters.xlsx", sheet_name="Characters")

# Audio documents
audio_processor = AudioProcessor()
audio_result = audio_processor.process("interview.mp3", speech_to_text=True)

# Text files with NLP
text_processor = TextProcessor()
text_result = text_processor.process("novel.txt", language="en", nlp_analysis=True)
```

## 💡 Analysis Examples

### 📚 Novel Analysis
```
Document: "Alice in Wonderland.docx"
Character table:
| Character    | Chapter 1 | Chapter 2 | Chapter 3 | Total |
|--------------|-----------|-----------|-----------|-------|
| Alice        | 25        | 30        | 28        | 83    |
| Mad Hatter   | 15        | 5         | 20        | 40    |
| White Rabbit | 10        | 15        | 12        | 37    |

Analysis Result:
🎯 Main characters: Alice (83 mentions)
📊 Secondary: Mad Hatter (40), White Rabbit (37)
🔗 Relationships: Alice interacts with all characters
📈 Dynamics: Activity increases towards the finale
```

### 📊 Research Report
```
Document: "Climate_Research.pdf"
Processing: OCR + data tables
Found researchers:
- Dr. Petrov: 45 mentions (28%)
- Dr. Ivanova: 32 mentions (20%)
- Dr. Sidorov: 28 mentions (17%)

Collaboration Analysis:
🤝 Joint projects: 12 projects
🏆 Citations: Petrov cited in 80% of works
📍 Geography: Moscow (60%), St. Petersburg (25%), Others (15%)
```

### 🎵 Interview Analysis
```
Document: Musicians_Interview.mp3
Processing: Speech-to-Text + analysis
Found musicians:
- Alex: 67 mentions (45%)
- Maria: 52 mentions (35%)
- Band: 30 mentions (20%)

Emotional Analysis:
😊 Positive emotions: 70%
😔 Negative: 15%
😐 Neutral: 15%

Discussion Topics:
🎸 Musical instruments: 40%
🎤 Vocals and singing: 35%
🎵 Composition: 25%
🧪 Testing
Run Test Suite
bashmake test              # Run all tests
make test-cov         # Run with coverage report
make test-watch       # Watch mode (requires pytest-watch)
```

### Test Structure
```
tests/
├── test_core_processor.py    # Core functionality tests
├── test_simple_gui.py       # Desktop GUI tests (if applicable)
└── test_web_interface.py    # Web interface tests (if applicable)
🔧 Configuration
Environment Variables
bash# Flask configuration (for web interface)
FLASK_ENV=development
FLASK_DEBUG=True

# File upload limits
MAX_CONTENT_LENGTH=16777216  # 16MB

# Optional AI analysis
HUGGINGFACE_TOKEN=your_token_here
Customization Options

Minimum Mentions: Filter characters by occurrence count
Column Selection: Specify which table column contains character names
Case Sensitivity: Merge case-insensitive name variants
Output Format: Customize report structure and styling

🚀 Deployment
Production Deployment
bash# Build distribution
make package

# Deploy to server (example with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app.web_interface:app
Docker Support (Coming Soon)
dockerfileFROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app/web_interface.py"]
🤝 Contributing
We welcome contributions! Please see our Contributing Guide for details.
Development Setup
bash# Install development dependencies
make install-dev

# Set up pre-commit hooks
pip install pre-commit
pre-commit install

# Run code quality checks
make lint
make format
Contribution Workflow

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

📚 API Documentation
Core Classes
DocumentProcessor
Main class for document processing and analysis.
pythonfrom app.core_processor import DocumentProcessor

processor = DocumentProcessor()
result = processor.process(file_path, column_index=1)
stats = processor.summarise(characters, ignore_case=False)
output_path = processor.export_report(result, output_path)
CharacterStat
Data class representing character frequency information.
python@dataclass
class CharacterStat:
    name: str
    count: int
Web API Endpoints
EndpointMethodDescription/GETMain interface/analyzePOSTAnalyze uploaded document/export/<session_id>GETDownload analysis report/healthGETHealth check endpoint
🐛 Troubleshooting
Common Issues
File Upload Fails

Ensure file is .docx format
Check file size (max 16MB)
Verify document contains tables

Analysis Returns No Characters

Verify column index (1-based)
Check table structure
Ensure column contains text data

Web Interface Not Loading

Install Flask: pip install flask
Check port availability (default 5000)
Verify browser compatibility

Getting Help

📧 Email: support@wordanalyzer.com
💬 Discord: Join our community
🐛 Issues: GitHub Issues

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments

python-docx: For robust Word document parsing
Flask: For the elegant web framework
Tkinter: For cross-platform GUI capabilities
Hugging Face: For AI model integration

📈 Roadmap
Version 2.1 (Planned)

 PDF document support
 Advanced AI character classification
 Excel export functionality
 Batch processing capabilities
 Docker containerization

Version 2.2 (Future)

 Real-time collaboration
 Cloud storage integration
 Advanced visualization options
 Mobile app development
 API rate limiting and authentication


<div align="center">
Made with ❤️ by the Word Character Analyzer Team
