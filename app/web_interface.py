"""
Modern web interface for Word Character Analyzer using Flask.
Provides a responsive, modern web interface with JavaScript animations.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import List, Optional
import json
import uuid
from datetime import datetime

try:
    from flask import Flask, render_template_string, request, jsonify, send_file, session, redirect, url_for
    from werkzeug.utils import secure_filename
    from werkzeug.exceptions import RequestEntityTooLarge
except ImportError:
    raise ImportError("Flask is required for web interface. Install with: pip install flask")

from .core_processor import DocumentProcessor, CharacterStat


app = Flask(__name__)
app.secret_key = "word-analyzer-secret-key-2024"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global processor instance
processor = DocumentProcessor()

# Session storage for analysis results
analysis_sessions = {}

# HTML Templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Word Character Analyzer Pro</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            animation: fadeInDown 1s ease-out;
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .main-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            margin-bottom: 30px;
            animation: fadeInUp 1s ease-out 0.3s both;
        }

        .upload-section {
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 60px 20px;
            text-align: center;
            margin-bottom: 30px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .upload-section:hover {
            border-color: #667eea;
            background-color: #f8f9ff;
        }

        .upload-section.dragover {
            border-color: #667eea;
            background-color: #f0f4ff;
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 4rem;
            color: #667eea;
            margin-bottom: 20px;
        }

        .upload-text {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 10px;
        }

        .upload-subtext {
            font-size: 0.9rem;
            color: #999;
        }

        .settings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .setting-group {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }

        .setting-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #495057;
        }

        .setting-group input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
        }

        .setting-group input[type="checkbox"] {
            margin-right: 8px;
            transform: scale(1.2);
        }

        .analyze-btn {
            width: 100%;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 20px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .progress-container {
            display: none;
            margin: 20px 0;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }

        .progress-text {
            text-align: center;
            margin-top: 10px;
            font-size: 0.9rem;
            color: #666;
        }

        .results-section {
            display: none;
            margin-top: 30px;
        }

        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .results-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
        }

        .export-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .export-btn:hover {
            background: #218838;
            transform: translateY(-1px);
        }

        .results-table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .results-table th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }

        .results-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }

        .results-table tr:nth-child(even) {
            background: #f8f9fa;
        }

        .results-table tr:hover {
            background: #e3f2fd;
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #f5c6cb;
            margin: 20px 0;
            display: none;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .file-input {
            display: none;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-magic"></i> Word Character Analyzer Pro</h1>
            <p>Advanced AI-powered document analysis with modern web interface</p>
        </div>

        <div class="main-card">
            <div class="upload-section" id="uploadSection">
                <div class="upload-icon">
                    <i class="fas fa-cloud-upload-alt"></i>
                </div>
                <div class="upload-text">Drop your Word document here or click to browse</div>
                <div class="upload-subtext">Supports .docx files up to 16MB</div>
                <input type="file" id="fileInput" class="file-input" accept=".docx">
            </div>

            <div class="error-message" id="errorMessage"></div>

            <div class="settings-grid">
                <div class="setting-group">
                    <label for="minMentions">Minimum Mentions</label>
                    <input type="number" id="minMentions" value="1" min="1" max="99">
                </div>
                <div class="setting-group">
                    <label for="columnIndex">Character Column (1-based)</label>
                    <input type="number" id="columnIndex" value="2" min="1" max="20">
                </div>
                <div class="setting-group">
                    <label>
                        <input type="checkbox" id="ignoreCase" checked>
                        Ignore Case Sensitivity
                    </label>
                </div>
            </div>

            <button class="analyze-btn" id="analyzeBtn" disabled>
                <i class="fas fa-search"></i> Analyze Document
            </button>

            <div class="progress-container" id="progressContainer">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-text" id="progressText">Preparing analysis...</div>
            </div>

            <div class="results-section" id="resultsSection">
                <div class="results-header">
                    <h2 class="results-title">
                        <i class="fas fa-chart-bar"></i> Analysis Results
                    </h2>
                    <button class="export-btn" id="exportBtn">
                        <i class="fas fa-download"></i> Export Report
                    </button>
                </div>

                <div class="stats-grid" id="statsGrid"></div>

                <table class="results-table">
                    <thead>
                        <tr>
                            <th><i class="fas fa-user"></i> Character Name</th>
                            <th><i class="fas fa-hashtag"></i> Mentions</th>
                            <th><i class="fas fa-percentage"></i> Frequency</th>
                        </tr>
                    </thead>
                    <tbody id="resultsTableBody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        class WordAnalyzer {
            constructor() {
                this.currentFile = null;
                this.currentSessionId = null;
                this.setupEventListeners();
            }

            setupEventListeners() {
                const uploadSection = document.getElementById('uploadSection');
                const fileInput = document.getElementById('fileInput');
                const analyzeBtn = document.getElementById('analyzeBtn');

                // File upload events
                uploadSection.addEventListener('click', () => fileInput.click());
                uploadSection.addEventListener('dragover', this.handleDragOver.bind(this));
                uploadSection.addEventListener('drop', this.handleDrop.bind(this));
                uploadSection.addEventListener('dragleave', this.handleDragLeave.bind(this));

                fileInput.addEventListener('change', this.handleFileSelect.bind(this));
                analyzeBtn.addEventListener('click', this.analyzeDocument.bind(this));
                
                document.getElementById('exportBtn').addEventListener('click', this.exportResults.bind(this));
            }

            handleDragOver(e) {
                e.preventDefault();
                e.currentTarget.classList.add('dragover');
            }

            handleDragLeave(e) {
                e.preventDefault();
                e.currentTarget.classList.remove('dragover');
            }

            handleDrop(e) {
                e.preventDefault();
                e.currentTarget.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.setCurrentFile(files[0]);
                }
            }

            handleFileSelect(e) {
                const file = e.target.files[0];
                if (file) {
                    this.setCurrentFile(file);
                }
            }

            setCurrentFile(file) {
                if (file.type !== 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
                    this.showError('Please select a valid Word document (.docx)');
                    return;
                }

                this.currentFile = file;
                document.getElementById('analyzeBtn').disabled = false;
                
                const uploadSection = document.getElementById('uploadSection');
                uploadSection.innerHTML = `
                    <div class="upload-icon" style="color: #28a745;">
                        <i class="fas fa-file-word"></i>
                    </div>
                    <div class="upload-text" style="color: #28a745;">${file.name}</div>
                    <div class="upload-subtext">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                `;

                this.hideError();
            }

            async analyzeDocument() {
                if (!this.currentFile) {
                    this.showError('Please select a document first');
                    return;
                }

                const formData = new FormData();
                formData.append('document', this.currentFile);
                formData.append('min_mentions', document.getElementById('minMentions').value);
                formData.append('column_index', document.getElementById('columnIndex').value - 1);
                formData.append('ignore_case', document.getElementById('ignoreCase').checked);

                this.showProgress();
                this.updateProgress(0, 'Uploading document...');

                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || 'Analysis failed');
                    }

                    this.currentSessionId = data.session_id;
                    this.displayResults(data);
                    this.hideProgress();

                } catch (error) {
                    this.showError(error.message);
                    this.hideProgress();
                }
            }

            showProgress() {
                document.getElementById('progressContainer').style.display = 'block';
                document.getElementById('analyzeBtn').disabled = true;
            }

            hideProgress() {
                document.getElementById('progressContainer').style.display = 'none';
                document.getElementById('analyzeBtn').disabled = false;
            }

            updateProgress(percentage, text) {
                document.getElementById('progressFill').style.width = percentage + '%';
                document.getElementById('progressText').textContent = text;
            }

            displayResults(data) {
                const resultsSection = document.getElementById('resultsSection');
                resultsSection.style.display = 'block';

                // Display stats
                const statsGrid = document.getElementById('statsGrid');
                statsGrid.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${data.total_characters}</div>
                        <div class="stat-label">Total Characters</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.unique_characters}</div>
                        <div class="stat-label">Unique Characters</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.filtered_characters}</div>
                        <div class="stat-label">With ${data.min_mentions}+ Mentions</div>
                    </div>
                `;

                // Display results table
                const tableBody = document.getElementById('resultsTableBody');
                tableBody.innerHTML = '';

                data.results.forEach((result, index) => {
                    const row = tableBody.insertRow();
                    row.innerHTML = `
                        <td><i class="fas fa-user"></i> ${result.name}</td>
                        <td><span class="badge">${result.count}</span></td>
                        <td>${result.frequency}%</td>
                    `;
                    
                    // Add animation delay
                    row.style.animationDelay = (index * 0.1) + 's';
                    row.style.animation = 'fadeInUp 0.5s ease-out forwards';
                });

                // Scroll to results
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }

            async exportResults() {
                if (!this.currentSessionId) {
                    this.showError('No results to export');
                    return;
                }

                try {
                    const response = await fetch(`/export/${this.currentSessionId}`);
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'character_analysis.docx';
                        a.click();
                        window.URL.revokeObjectURL(url);
                    } else {
                        throw new Error('Export failed');
                    }
                } catch (error) {
                    this.showError('Export failed: ' + error.message);
                }
            }

            showError(message) {
                const errorElement = document.getElementById('errorMessage');
                errorElement.textContent = message;
                errorElement.style.display = 'block';
            }

            hideError() {
                document.getElementById('errorMessage').style.display = 'none';
            }
        }

        // Initialize the analyzer
        const analyzer = new WordAnalyzer();

        // Add some interactive animations
        document.addEventListener('DOMContentLoaded', function() {
            // Animate elements on load
            const cards = document.querySelectorAll('.setting-group, .stat-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = (index * 0.1) + 's';
                card.style.animation = 'fadeInUp 0.6s ease-out forwards';
            });
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main page with file upload and analysis interface."""
    return render_template_string(HOME_TEMPLATE)


@app.route('/analyze', methods=['POST'])
def analyze_document():
    """Handle document analysis request."""
    try:
        # Validate file upload
        if 'document' not in request.files:
            return jsonify({'error': 'No document provided'}), 400
        
        file = request.files['document']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not file.filename.lower().endswith('.docx'):
            return jsonify({'error': 'Please upload a Word document (.docx)'}), 400
        
        # Get parameters
        min_mentions = int(request.form.get('min_mentions', 1))
        column_index = int(request.form.get('column_index', 1))
        ignore_case = request.form.get('ignore_case', 'true').lower() == 'true'
        
        # Validate parameters
        if min_mentions < 1:
            return jsonify({'error': 'Minimum mentions must be at least 1'}), 400
        if column_index < 0:
            return jsonify({'error': 'Column index cannot be negative'}), 400
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(temp_file_path)
        
        try:
            # Process document
            result = processor.process(Path(temp_file_path), column_index=column_index)
            stats = processor.summarise(result.characters, ignore_case=ignore_case)
            
            # Filter by minimum mentions
            filtered_stats = [stat for stat in stats if stat.count >= min_mentions]
            
            # Calculate total and frequencies
            total_mentions = sum(stat.count for stat in stats)
            results_data = []
            
            for stat in filtered_stats:
                frequency = round((stat.count / total_mentions) * 100, 2) if total_mentions > 0 else 0
                results_data.append({
                    'name': stat.name,
                    'count': stat.count,
                    'frequency': frequency
                })
            
            # Create session for results
            session_id = str(uuid.uuid4())
            analysis_sessions[session_id] = {
                'results': filtered_stats,
                'original_result': result,
                'parameters': {
                    'min_mentions': min_mentions,
                    'column_index': column_index,
                    'ignore_case': ignore_case
                },
                'created_at': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'total_characters': len(result.characters),
                'unique_characters': len(stats),
                'filtered_characters': len(filtered_stats),
                'min_mentions': min_mentions,
                'results': results_data
            })
            
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
                os.rmdir(temp_dir)
            except:
                pass
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/export/<session_id>')
def export_results(session_id):
    """Export analysis results as Word document."""
    if session_id not in analysis_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    try:
        session_data = analysis_sessions[session_id]
        params = session_data['parameters']
        
        # Create temporary output file
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, f"analysis_{session_id[:8]}.docx")
        
        # Export report
        processor.export_report(
            session_data['original_result'],
            Path(output_path),
            minimum_mentions=params['min_mentions'],
            ignore_case=params['ignore_case']
        )
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name='character_analysis_report.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Word Character Analyzer Web Interface',
        'version': '2.0.0'
    })


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    """Handle file size limit exceeded."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


@app.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def handle_server_error(error):
    """Handle server errors."""
    return jsonify({'error': 'Internal server error'}), 500


def run_web_server(host='127.0.0.1', port=5000, debug=False):
    """Run the web interface server."""
    print(f"🚀 Starting Word Character Analyzer Web Interface...")
    print(f"📡 Server running at: http://{host}:{port}")
    print(f"🌐 Open your browser to: http://{host}:{port}")
    print(f"💡 Press Ctrl+C to stop the server")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_web_server(debug=True)