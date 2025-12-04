"""
Setup script for Word Character Analyzer Pro.

This package provides tools for analyzing character frequencies in Word documents
with modern desktop and web interfaces.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

# Development requirements
dev_requirements = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
    "pre-commit>=2.20.0",
]

# Optional dependencies
optional_requirements = {
    "web": [
        "flask>=2.3.0",
        "werkzeug>=2.3.0",
    ],
    "ai": [
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "numpy>=1.21.0",
    ],
    "sheets": [
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=1.0.0",
        "google-auth-httplib2>=0.1.0",
        "google-api-python-client>=2.0.0",
    ],
    "all": [
        "flask>=2.3.0",
        "werkzeug>=2.3.0",
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "numpy>=1.21.0",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=1.0.0",
        "google-auth-httplib2>=0.1.0",
        "google-api-python-client>=2.0.0",
    ],
}

setup(
    name="word-character-analyzer",
    version="2.0.0",
    author="Word Character Analyzer Team",
    author_email="support@wordanalyzer.com",
    description="Advanced AI-powered document analysis tool for extracting character frequencies from Word documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/word-character-analyzer",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/word-character-analyzer/issues",
        "Documentation": "https://github.com/yourusername/word-character-analyzer/docs",
        "Source Code": "https://github.com/yourusername/word-character-analyzer",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require=optional_requirements,
    entry_points={
        "console_scripts": [
            "word-analyzer=app.simple_gui:run_app",
            "word-analyzer-pro=app.enhanced_gui:run_enhanced_app",
            "word-analyzer-web=app.web_interface:run_web_server",
        ],
    },
    include_package_data=True,
    package_data={
        "app": [
            "*.txt",
            "*.md",
            "*.yml",
            "*.yaml",
            "*.json",
        ],
    },
    zip_safe=False,
    keywords=[
        "word",
        "document",
        "analysis",
        "character",
        "frequency",
        "table",
        "docx",
        "python",
        "tkinter",
        "flask",
        "ai",
        "nlp",
    ],
)