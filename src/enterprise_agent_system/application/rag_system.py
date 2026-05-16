"""
RAG (Retrieval-Augmented Generation) System
提供知识库构建、文档分块、向量存储和语义检索功能
"""

import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)


@dataclass
class DocumentChunk:
    """文档分块"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """搜索结果"""
    chunk: DocumentChunk
    relevance_score: float


class SimpleVectorStore:
    """简单的内存向量存储"""
    
    def __init__(self):
        self.chunks: Dict[str, DocumentChunk] = {}
        self.index = defaultdict(list)
    
    def add_chunk(self, chunk: DocumentChunk):
        """添加文档块"""
        self.chunks[chunk.id] = chunk
        
        # 简单的关键字索引
        words = set(chunk.content.lower().split())
        for word in words:
            self.index[word].append(chunk.id)
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """简单的关键字搜索"""
        query_words = set(query.lower().split())
        chunk_scores = defaultdict(float)
        
        # 基于关键词匹配的简单得分
        for word in query_words:
            if word in self.index:
                for chunk_id in self.index[word]:
                    chunk_scores[chunk_id] += 1
        
        # 排序并返回
        sorted_chunks = sorted(
            chunk_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        results = []
        for chunk_id, score in sorted_chunks:
            if chunk_id in self.chunks:
                results.append(SearchResult(
                    chunk=self.chunks[chunk_id],
                    relevance_score=score
                ))
        
        return results
    
    def get_all_chunks(self) -> List[DocumentChunk]:
        """获取所有文档块"""
        return list(self.chunks.values())


class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """将文本分割成块"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # 尝试在标点或换行处分割
            if end < len(text):
                # 向后查找最近的分割点
                split_pos = self._find_split_position(text, start, end)
                if split_pos > start:
                    end = split_pos
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 移动到下一个块，带重叠
            start = end - self.chunk_overlap
        
        return chunks
    
    def _find_split_position(self, text: str, start: int, end: int) -> int:
        """查找最佳分割位置"""
        split_chars = ['\n\n', '\n', '. ', '! ', '? ', '; ', ', ']
        for char in split_chars:
            pos = text.rfind(char, start, end)
            if pos != -1:
                return pos + len(char)
        return end
    
    def process_document(self, content: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """处理文档并返回分块"""
        chunks = self.split_text(content)
        result = []
        
        for i, chunk_content in enumerate(chunks):
            chunk_id = hashlib.md5(
                f"{metadata.get('source', '')}-{i}".encode()
            ).hexdigest()
            
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            
            result.append(DocumentChunk(
                id=chunk_id,
                content=chunk_content,
                metadata=chunk_metadata
            ))
        
        return result


class RAGSystem:
    """RAG系统核心"""
    
    def __init__(self):
        self.vector_store = SimpleVectorStore()
        self.document_processor = DocumentProcessor()
        self.knowledge_base: Dict[str, List[DocumentChunk]] = {}
        logger.info("RAG System initialized")
    
    def add_document(self, content: str, source: str, metadata: Optional[Dict[str, Any]] = None):
        """添加文档到知识库"""
        full_metadata = {
            "source": source,
            **(metadata or {})
        }
        
        chunks = self.document_processor.process_document(
            content=content,
            metadata=full_metadata
        )
        
        for chunk in chunks:
            self.vector_store.add_chunk(chunk)
        
        self.knowledge_base[source] = chunks
        logger.info(f"Added document: {source}, {len(chunks)} chunks")
    
    def add_file(self, file_path: str):
        """从文件添加文档"""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.add_document(
            content=content,
            source=file_path,
            metadata={
                "file_path": file_path,
                "file_name": path.name
            }
        )
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """搜索相关文档"""
        results = self.vector_store.search(query, top_k)
        logger.info(f"Search: '{query}' found {len(results)} results")
        return results
    
    def build_context(self, query: str, top_k: int = 3) -> str:
        """构建检索上下文"""
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results):
            context_parts.append(
                f"[Document {i+1}]\n"
                f"Source: {result.chunk.metadata.get('source', 'unknown')}\n"
                f"Content: {result.chunk.content}\n"
            )
        
        return "\n".join(context_parts)
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """获取知识库统计"""
        total_chunks = len(self.vector_store.get_all_chunks())
        total_documents = len(self.knowledge_base)
        
        return {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "documents": list(self.knowledge_base.keys())
        }


# 全局RAG实例
_rag_system: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """获取RAG系统实例"""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system
