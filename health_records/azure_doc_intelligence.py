"""
Azure Document Intelligence service for extracting structured data from therapist notes.
"""
import os
import logging
from typing import Dict, List, Optional
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from django.conf import settings

logger = logging.getLogger(__name__)


class AzureDocumentIntelligenceService:
    """Service for processing documents using Azure Document Intelligence"""
    
    def __init__(self):
        """Initialize the Azure Document Intelligence client"""
        self.endpoint = getattr(settings, 'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', None)
        self.api_key = getattr(settings, 'AZURE_DOCUMENT_INTELLIGENCE_KEY', None)
        
        if not self.endpoint or not self.api_key:
            logger.warning("Azure Document Intelligence credentials not configured")
            self.client = None
        else:
            try:
                credential = AzureKeyCredential(self.api_key)
                self.client = DocumentIntelligenceClient(
                    endpoint=self.endpoint,
                    credential=credential
                )
            except Exception as e:
                logger.error(f"Failed to initialize Azure Document Intelligence client: {e}")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if Azure Document Intelligence is properly configured"""
        return self.client is not None
    
    def analyze_document(self, file_path: str) -> Optional[Dict]:
        """
        Analyze a document and extract structured data.
        
        Args:
            file_path: Path to the document image file
            
        Returns:
            Dictionary containing extracted data, or None if analysis fails
        """
        if not self.is_configured():
            logger.error("Azure Document Intelligence is not configured")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Use the general document model to extract text and structure
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-layout",
                analyze_request=file_content,
                content_type="application/octet-stream"
            )
            
            result = poller.result()
            
            # Extract structured information
            extracted_data = {
                'raw_text': result.content if hasattr(result, 'content') else '',
                'pages': [],
                'tables': [],
                'key_value_pairs': [],
                'findings': []
            }
            
            # Extract pages
            if hasattr(result, 'pages') and result.pages:
                for page in result.pages:
                    extracted_data['pages'].append({
                        'page_number': page.page_number if hasattr(page, 'page_number') else None,
                        'width': page.width if hasattr(page, 'width') else None,
                        'height': page.height if hasattr(page, 'height') else None,
                    })
            
            # Extract tables
            if hasattr(result, 'tables') and result.tables:
                for table in result.tables:
                    table_data = {
                        'row_count': table.row_count if hasattr(table, 'row_count') else 0,
                        'column_count': table.column_count if hasattr(table, 'column_count') else 0,
                        'cells': []
                    }
                    
                    if hasattr(table, 'cells') and table.cells:
                        for cell in table.cells:
                            cell_data = {
                                'row_index': cell.row_index if hasattr(cell, 'row_index') else None,
                                'column_index': cell.column_index if hasattr(cell, 'column_index') else None,
                                'content': cell.content if hasattr(cell, 'content') else '',
                                'kind': cell.kind if hasattr(cell, 'kind') else None,
                            }
                            table_data['cells'].append(cell_data)
                    
                    extracted_data['tables'].append(table_data)
            
            # Extract key-value pairs (for structured forms)
            if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
                for kv_pair in result.key_value_pairs:
                    key = kv_pair.key.content if hasattr(kv_pair, 'key') and hasattr(kv_pair.key, 'content') else ''
                    value = kv_pair.value.content if hasattr(kv_pair, 'value') and hasattr(kv_pair.value, 'content') else ''
                    if key and value:
                        extracted_data['key_value_pairs'].append({
                            'key': key,
                            'value': value
                        })
            
            # Parse findings from the text (look for common medical note patterns)
            extracted_data['findings'] = self._parse_findings(extracted_data['raw_text'])
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return None
    
    def _parse_findings(self, text: str) -> List[Dict]:
        """
        Parse findings from extracted text.
        Looks for common patterns in medical/therapy notes.
        
        Args:
            text: Extracted text from the document
            
        Returns:
            List of findings dictionaries
        """
        findings = []
        
        if not text:
            return findings
        
        # Common patterns to look for in therapy notes
        lines = text.split('\n')
        current_category = None
        
        # Keywords that might indicate categories
        category_keywords = {
            'assessment': ['assessment', 'findings', 'evaluation', 'examination'],
            'diagnosis': ['diagnosis', 'diagnoses', 'condition', 'pathology'],
            'treatment': ['treatment', 'plan', 'intervention', 'therapy', 'exercise'],
            'prognosis': ['prognosis', 'outcome', 'expectation', 'progress'],
            'recommendations': ['recommendation', 'advice', 'suggest', 'should'],
            'measurements': ['rom', 'range of motion', 'strength', 'power', 'degrees'],
            'symptoms': ['symptom', 'pain', 'discomfort', 'complaint'],
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains a category keyword
            line_lower = line.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_category = category
                    break
            
            # If line looks like a finding (contains common medical terms or measurements)
            if self._is_finding_line(line):
                finding = {
                    'category': current_category or 'general',
                    'text': line,
                    'type': self._classify_finding_type(line)
                }
                findings.append(finding)
        
        return findings
    
    def _is_finding_line(self, line: str) -> bool:
        """Check if a line looks like a medical finding"""
        # Common medical/therapy terms
        medical_terms = [
            'pain', 'stiffness', 'weakness', 'swelling', 'tenderness',
            'rom', 'range', 'motion', 'flexion', 'extension', 'abduction', 'adduction',
            'strength', 'power', 'grade', 'degrees', 'cm', 'mm',
            'improved', 'worsened', 'stable', 'normal', 'abnormal',
            'limited', 'restricted', 'full', 'partial'
        ]
        
        line_lower = line.lower()
        return any(term in line_lower for term in medical_terms) and len(line) > 10
    
    def _classify_finding_type(self, text: str) -> str:
        """Classify the type of finding"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['rom', 'range of motion', 'flexion', 'extension', 'degrees']):
            return 'measurement'
        elif any(term in text_lower for term in ['strength', 'power', 'grade']):
            return 'strength'
        elif any(term in text_lower for term in ['pain', 'discomfort', 'tenderness']):
            return 'symptom'
        elif any(term in text_lower for term in ['exercise', 'treatment', 'therapy']):
            return 'treatment'
        else:
            return 'observation'

