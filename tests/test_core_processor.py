"""
Tests for the core DocumentProcessor functionality.
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Import the modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core_processor import DocumentProcessor, CharacterStat, ProcessingResult, TableData


class TestDocumentProcessor:
    """Test suite for DocumentProcessor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = DocumentProcessor()

    def test_process_nonexistent_file(self):
        """Test processing a non-existent file raises appropriate error."""
        nonexistent_file = Path("/path/that/does/not/exist.docx")
        
        with pytest.raises(FileNotFoundError):
            self.processor.process(nonexistent_file)

    def test_process_invalid_column_index(self):
        """Test processing with negative column index raises ValueError."""
        with pytest.raises(ValueError, match="Column index cannot be negative"):
            self.processor.process(Path("dummy.docx"), column_index=-1)

    def test_summarise_empty_characters(self):
        """Test summarising empty character list returns empty list."""
        result = self.processor.summarise([])
        assert result == []

    def test_summarise_single_character(self):
        """Test summarising single character."""
        characters = ["Alice"]
        result = self.processor.summarise(characters)
        
        assert len(result) == 1
        assert result[0] == CharacterStat("Alice", 1)

    def test_summarise_multiple_characters(self):
        """Test summarising multiple characters with frequencies."""
        characters = ["Alice", "Bob", "Alice", "Charlie", "Bob", "Alice"]
        result = self.processor.summarise(characters)
        
        # Should be sorted by count (descending)
        assert len(result) == 3
        assert result[0] == CharacterStat("Alice", 3)  # Most frequent
        assert result[1] == CharacterStat("Bob", 2)
        assert result[2] == CharacterStat("Charlie", 1)

    def test_summarise_ignore_case(self):
        """Test case-insensitive summarising."""
        characters = ["Alice", "alice", "ALICE", "Bob"]
        result = self.processor.summarise(characters, ignore_case=True)
        
        # All Alice variants should be merged
        assert len(result) == 2
        assert result[0] == CharacterStat("Alice", 3)  # All Alice variants
        assert result[1] == CharacterStat("Bob", 1)

    def test_summarise_preserve_case_when_false(self):
        """Test that case is preserved when ignore_case=False."""
        characters = ["Alice", "alice", "ALICE"]
        result = self.processor.summarise(characters, ignore_case=False)
        
        # Should treat as separate names
        assert len(result) == 3
        assert CharacterStat("Alice", 1) in result
        assert CharacterStat("alice", 1) in result
        assert CharacterStat("ALICE", 1) in result

    def test_summarise_empty_names_filtered(self):
        """Test that empty names are filtered out."""
        characters = ["Alice", "", "Bob", "   ", "Charlie"]
        result = self.processor.summarise(characters)
        
        # Should only include non-empty names
        assert len(result) == 3
        names = [stat.name for stat in result]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names

    @patch('app.core_processor.Document')
    def test_process_valid_document(self, mock_document_class):
        """Test processing a valid document with mock."""
        # Mock document structure
        mock_table = Mock()
        mock_row1 = Mock()
        mock_row1.cells = [Mock(text="Row1Col1"), Mock(text="Alice"), Mock(text="Data1")]
        mock_row2 = Mock()
        mock_row2.cells = [Mock(text="Row2Col1"), Mock(text="Bob"), Mock(text="Data2")]
        mock_table.rows = [mock_row1, mock_row2]
        
        mock_doc = Mock()
        mock_doc.tables = [mock_table]
        mock_document_class.return_value = mock_doc
        
        # Test processing
        result = self.processor.process(Path("test.docx"), column_index=1)
        
        assert isinstance(result, ProcessingResult)
        assert result.characters == ["Alice", "Bob"]
        assert len(result.tables) == 1
        assert result.tables[0].rows == [["Row1Col1", "Alice", "Data1"], ["Row2Col1", "Bob", "Data2"]]

    @patch('app.core_processor.Document')
    def test_process_no_characters_found(self, mock_document_class):
        """Test processing document with no characters in specified column."""
        # Mock empty table
        mock_table = Mock()
        mock_row = Mock()
        mock_row.cells = [Mock(text="Only one column")]
        mock_table.rows = [mock_row]
        
        mock_doc = Mock()
        mock_doc.tables = [mock_table]
        mock_document_class.return_value = mock_doc
        
        # Should raise ValueError when no characters found
        with pytest.raises(ValueError, match="No characters found in column"):
            self.processor.process(Path("test.docx"), column_index=1)

    @patch('app.core_processor.Document')
    def test_process_invalid_document(self, mock_document_class):
        """Test processing invalid document raises appropriate error."""
        mock_document_class.side_effect = Exception("Invalid document")
        
        with pytest.raises(ValueError, match="Failed to read document"):
            self.processor.process(Path("invalid.docx"))

    def test_export_report_basic(self):
        """Test basic report export functionality."""
        # Create test data
        characters = ["Alice", "Bob", "Alice"]
        tables = [TableData(rows=[["Header1", "Character", "Data"], ["Row1", "Alice", "Info"]])]
        result = ProcessingResult(characters=characters, tables=tables)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_report.docx"
            
            # Mock Document to avoid actual file creation
            with patch('app.core_processor.Document') as mock_doc_class:
                mock_doc = Mock()
                mock_doc_class.return_value = mock_doc
                
                returned_path = self.processor.export_report(result, output_path)
                
                assert returned_path == output_path
                # Verify Document was created and save was called
                mock_doc_class.assert_called_once()
                mock_doc.save.assert_called_once_with(output_path)

    def test_get_table_preview(self):
        """Test table preview functionality."""
        # Mock document with multiple tables
        mock_table1 = Mock()
        mock_table1.rows = [
            Mock(cells=[Mock(text="A1"), Mock(text="B1"), Mock(text="C1")]),
            Mock(cells=[Mock(text="A2"), Mock(text="B2"), Mock(text="C2")]),
            Mock(cells=[Mock(text="A3"), Mock(text="B3"), Mock(text="C3")]),
        ]
        
        mock_table2 = Mock()
        mock_table2.rows = [
            Mock(cells=[Mock(text="X1"), Mock(text="Y1")]),
            Mock(cells=[Mock(text="X2"), Mock(text="Y2")]),
        ]
        
        with patch('app.core_processor.Document') as mock_doc_class:
            mock_doc = Mock()
            mock_doc.tables = [mock_table1, mock_table2]
            mock_doc_class.return_value = mock_doc
            
            preview = self.processor.get_table_preview(Path("test.docx"), max_rows=2)
            
            # Should return preview of both tables with limited rows
            assert len(preview) == 2
            assert len(preview[0]) == 2  # First 2 rows of first table
            assert len(preview[1]) == 2  # First 2 rows of second table
            assert preview[0][0] == ["A1", "B1", "C1"]
            assert preview[1][0] == ["X1", "Y1"]


class TestCharacterStat:
    """Test suite for CharacterStat dataclass."""

    def test_character_stat_creation(self):
        """Test CharacterStat creation and properties."""
        stat = CharacterStat("Alice", 5)
        assert stat.name == "Alice"
        assert stat.count == 5

    def test_character_stat_equality(self):
        """Test CharacterStat equality comparison."""
        stat1 = CharacterStat("Alice", 5)
        stat2 = CharacterStat("Alice", 5)
        stat3 = CharacterStat("Bob", 5)
        
        assert stat1 == stat2
        assert stat1 != stat3


class TestTableData:
    """Test suite for TableData dataclass."""

    def test_table_data_creation(self):
        """Test TableData creation and properties."""
        rows = [["A1", "B1"], ["A2", "B2"]]
        table = TableData(rows=rows)
        assert table.rows == rows

    def test_table_data_empty(self):
        """Test TableData with empty rows."""
        table = TableData(rows=[])
        assert table.rows == []


class TestProcessingResult:
    """Test suite for ProcessingResult dataclass."""

    def test_processing_result_creation(self):
        """Test ProcessingResult creation and properties."""
        characters = ["Alice", "Bob"]
        tables = [TableData(rows=[["Header", "Name"]])]
        result = ProcessingResult(characters=characters, tables=tables)
        
        assert result.characters == characters
        assert result.tables == tables

    def test_processing_result_empty(self):
        """Test ProcessingResult with empty data."""
        result = ProcessingResult(characters=[], tables=[])
        assert result.characters == []
        assert result.tables == []


if __name__ == "__main__":
    pytest.main([__file__])