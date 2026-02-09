"""Import parsing engine for CSV, XLSX, and JSON files."""

import csv
import io
import json
import logging
from typing import Any, BinaryIO

import chardet


logger = logging.getLogger(__name__)


class FileParser:
    """Base file parser with charset detection."""
    
    @staticmethod
    def detect_encoding(content: bytes) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            content: File content as bytes
            
        Returns:
            Detected encoding (e.g., 'utf-8', 'iso-8859-1')
        """
        result = chardet.detect(content)
        encoding = result.get("encoding", "utf-8")
        confidence = result.get("confidence", 0)
        
        logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2%})")
        
        # Fallback to UTF-8 if confidence is low
        if confidence < 0.7:
            logger.warning(f"Low confidence in encoding detection, using UTF-8")
            return "utf-8"
            
        return encoding


class CSVParser(FileParser):
    """CSV file parser with encoding detection and dialect detection."""
    
    def parse(self, file: BinaryIO, encoding: str | None = None) -> tuple[list[str], list[dict[str, Any]]]:
        """
        Parse CSV file.
        
        Args:
            file: File object
            encoding: Optional encoding (auto-detected if not provided)
            
        Returns:
            Tuple of (column_names, rows)
        """
        # Read file content
        content = file.read()
        
        # Detect encoding if not provided
        if encoding is None:
            encoding = self.detect_encoding(content)
        
        # Decode content
        try:
            text = content.decode(encoding)
        except UnicodeDecodeError:
            logger.warning(f"Failed to decode with {encoding}, falling back to UTF-8 with errors='replace'")
            text = content.decode("utf-8", errors="replace")
        
        # Detect CSV dialect
        sample = text[:10000]  # Use first 10KB for dialect detection
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            # Fallback to excel dialect
            dialect = csv.excel
            
        # Parse CSV
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        
        columns = reader.fieldnames or []
        rows = list(reader)
        
        logger.info(f"Parsed CSV: {len(columns)} columns, {len(rows)} rows")
        
        return columns, rows


class XLSXParser(FileParser):
    """Excel XLSX file parser."""
    
    def parse(self, file: BinaryIO) -> tuple[list[str], list[dict[str, Any]]]:
        """
        Parse XLSX file.
        
        Args:
            file: File object
            
        Returns:
            Tuple of (column_names, rows)
        """
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl is required for XLSX parsing. Install with: pip install openpyxl")
        
        # Load workbook
        workbook = openpyxl.load_workbook(file, read_only=True, data_only=True)
        
        # Get first sheet
        sheet = workbook.active
        
        # Read rows
        rows_iter = sheet.iter_rows(values_only=True)
        
        # First row is header
        columns = [str(cell) if cell is not None else f"Column{i}" for i, cell in enumerate(next(rows_iter))]
        
        # Read data rows
        rows = []
        for row in rows_iter:
            # Skip empty rows
            if all(cell is None or cell == "" for cell in row):
                continue
                
            row_dict = {
                col: cell for col, cell in zip(columns, row)
            }
            rows.append(row_dict)
        
        logger.info(f"Parsed XLSX: {len(columns)} columns, {len(rows)} rows")
        
        return columns, rows


class JSONParser(FileParser):
    """JSON file parser."""
    
    def parse(self, file: BinaryIO, encoding: str | None = None) -> tuple[list[str], list[dict[str, Any]]]:
        """
        Parse JSON file.
        
        Args:
            file: File object
            encoding: Optional encoding (auto-detected if not provided)
            
        Returns:
            Tuple of (column_names, rows)
        """
        # Read file content
        content = file.read()
        
        # Detect encoding if not provided
        if encoding is None:
            encoding = self.detect_encoding(content)
        
        # Decode content
        try:
            text = content.decode(encoding)
        except UnicodeDecodeError:
            logger.warning(f"Failed to decode with {encoding}, falling back to UTF-8 with errors='replace'")
            text = content.decode("utf-8", errors="replace")
        
        # Parse JSON
        data = json.loads(text)
        
        # Handle different JSON structures
        if isinstance(data, list):
            rows = data
        elif isinstance(data, dict):
            # If it's a dict, check if it has a data key
            if "data" in data and isinstance(data["data"], list):
                rows = data["data"]
            elif "items" in data and isinstance(data["items"], list):
                rows = data["items"]
            elif "rows" in data and isinstance(data["rows"], list):
                rows = data["rows"]
            else:
                # Treat the dict as a single row
                rows = [data]
        else:
            raise ValueError("JSON must be an array of objects or an object with a data/items/rows array")
        
        # Extract column names from first row
        if rows:
            columns = list(rows[0].keys())
        else:
            columns = []
        
        logger.info(f"Parsed JSON: {len(columns)} columns, {len(rows)} rows")
        
        return columns, rows


def create_parser(file_format: str):
    """
    Factory to create appropriate parser based on file format.
    
    Args:
        file_format: File format ("csv", "xlsx", "json")
        
    Returns:
        Parser instance
    """
    if file_format == "csv":
        return CSVParser()
    elif file_format == "xlsx":
        return XLSXParser()
    elif file_format == "json":
        return JSONParser()
    else:
        raise ValueError(f"Unsupported file format: {file_format}")


def suggest_column_mapping(
    file_columns: list[str],
    schema_fields: list[str],
    threshold: float = 0.6
) -> dict[str, str]:
    """
    Suggest column mapping based on similarity.
    
    Uses simple string similarity (case-insensitive, normalized).
    
    Args:
        file_columns: Column names from file
        schema_fields: Field names from schema
        threshold: Minimum similarity threshold (0.0-1.0)
        
    Returns:
        Mapping dict {file_column: schema_field}
    """
    from difflib import SequenceMatcher
    
    mapping = {}
    
    for file_col in file_columns:
        best_match = None
        best_score = 0.0
        
        file_col_norm = file_col.lower().replace("_", "").replace(" ", "")
        
        for schema_field in schema_fields:
            schema_field_norm = schema_field.lower().replace("_", "")
            
            # Calculate similarity
            score = SequenceMatcher(None, file_col_norm, schema_field_norm).ratio()
            
            if score > best_score:
                best_score = score
                best_match = schema_field
        
        # Only include if similarity is above threshold
        if best_match and best_score >= threshold:
            mapping[file_col] = best_match
            logger.debug(f"Mapped '{file_col}' -> '{best_match}' (score: {best_score:.2f})")
    
    return mapping
