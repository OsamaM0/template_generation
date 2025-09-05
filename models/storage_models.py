"""
Data models for storing generated templates in MongoDB.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class DocumentInfo(BaseModel):
    """Document information model."""
    uuid: str
    idx: str
    custom_id: str
    filename: str
    content: str

class GenerationMetadata(BaseModel):
    """Metadata for generated content."""
    generation_source: str = "template_generator"
    goals_source: str  # "database" or "default"
    content_length: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class QuestionRecord(BaseModel):
    """Model for storing question records in MongoDB."""
    document_uuid: str
    document_idx: str
    custom_id: str
    filename: str
    goals: List[str]
    questions: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: GenerationMetadata

class WorksheetRecord(BaseModel):
    """Model for storing worksheet records in MongoDB."""
    document_uuid: str
    document_idx: str
    custom_id: str
    filename: str
    goals: List[str]
    worksheet: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: GenerationMetadata

class SummaryRecord(BaseModel):
    """Model for storing summary records in MongoDB."""
    document_uuid: str
    document_idx: str
    custom_id: str
    filename: str
    summary: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: GenerationMetadata

class MindMapRecord(BaseModel):
    """Model for storing mind map records in MongoDB."""
    document_uuid: str
    document_idx: str
    custom_id: str
    filename: str
    mindmap: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: GenerationMetadata

class ProcessingStats(BaseModel):
    """Statistics for processing session."""
    total_documents: int = 0
    processed_documents: int = 0
    successful_questions: int = 0
    successful_worksheets: int = 0
    successful_summaries: int = 0
    successful_mindmaps: int = 0
    failed_documents: int = 0
    skipped_documents: int = 0
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    
    def add_success(self, template_type: str):
        """Add a successful generation."""
        if template_type == "questions":
            self.successful_questions += 1
        elif template_type == "worksheets":
            self.successful_worksheets += 1
        elif template_type == "summaries":
            self.successful_summaries += 1
        elif template_type == "mindmaps":
            self.successful_mindmaps += 1
        self.processed_documents += 1
    
    def add_failure(self):
        """Add a failed generation."""
        self.failed_documents += 1
    
    def add_skip(self):
        """Add a skipped document."""
        self.skipped_documents += 1
    
    def finish(self):
        """Mark processing as finished."""
        self.end_time = datetime.utcnow()
    
    def get_duration(self) -> float:
        """Get processing duration in seconds."""
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary."""
        return {
            "total_documents": self.total_documents,
            "processed_documents": self.processed_documents,
            "successful_generations": {
                "questions": self.successful_questions,
                "worksheets": self.successful_worksheets,
                "summaries": self.successful_summaries,
                "mindmaps": self.successful_mindmaps
            },
            "failed_documents": self.failed_documents,
            "skipped_documents": self.skipped_documents,
            "duration_seconds": self.get_duration(),
            "success_rate": (self.processed_documents / max(self.total_documents, 1)) * 100
        }
