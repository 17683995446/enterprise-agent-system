"""
LLM Analysis API Routes
FastAPI routes for LLM-powered code analysis
Infrastructure Layer - API层
"""

import asyncio
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from enterprise_agent_system.application.llm_analysis_system import (
    EnhancedCodeAnalyzer,
    EnhancedProjectAnalyzer,
)
from enterprise_agent_system.application.enhanced_analysis_system import EnhancedAnalyzer
from enterprise_agent_system.infrastructure.llm_integration import AnalysisOptions, AnalysisDepth
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)
router = APIRouter(prefix="/api/v1/llm", tags=["LLM Analysis"])


class CodeAnalysisRequest(BaseModel):
    """代码分析请求"""
    code: str = Field(..., description="要分析的代码")
    language: str = Field(default="python", description="编程语言")
    analysis_type: str = Field(default="comprehensive", description="分析类型: comprehensive, security, performance, architecture")
    depth: str = Field(default="deep", description="分析深度: quick, standard, deep, comprehensive")


class FileAnalysisRequest(BaseModel):
    """文件分析请求"""
    file_path: str = Field(..., description="文件路径")
    analysis_type: str = Field(default="comprehensive", description="分析类型")


class ProjectAnalysisRequest(BaseModel):
    """项目分析请求"""
    project_path: str = Field(..., description="项目路径")
    max_files: int = Field(default=30, description="最大分析文件数")


class TestGenerationRequest(BaseModel):
    """测试生成请求"""
    code: str = Field(..., description="要生成测试的代码")
    language: str = Field(default="python", description="编程语言")
    test_framework: str = Field(default="pytest", description="测试框架")


class RefactoringRequest(BaseModel):
    """重构建议请求"""
    code: str = Field(..., description="要重构的代码")
    language: str = Field(default="python", description="编程语言")
    target_style: Optional[str] = Field(default=None, description="目标风格")


class DocumentationRequest(BaseModel):
    """文档生成请求"""
    code: str = Field(..., description="要生成文档的代码")
    language: str = Field(default="python", description="编程语言")
    doc_format: str = Field(default="docstring", description="文档格式")


class ComparisonRequest(BaseModel):
    """代码比较请求"""
    code: str = Field(..., description="原始代码")
    alternatives: List[str] = Field(..., description="替代方案列表")
    language: str = Field(default="python", description="编程语言")


class ErrorAnalysisRequest(BaseModel):
    """错误分析请求"""
    error_message: str = Field(..., description="错误信息")
    code_context: Optional[str] = Field(default=None, description="代码上下文")
    stack_trace: Optional[str] = Field(default=None, description="堆栈跟踪")


@router.post("/analyze/code")
async def analyze_code(request: CodeAnalysisRequest) -> Dict[str, Any]:
    """分析代码"""
    logger.info(f"Analyzing {request.language} code")
    
    analyzer = EnhancedCodeAnalyzer()
    
    options = AnalysisOptions(
        depth=AnalysisDepth[request.depth.upper()],
        include_security=True,
        include_performance=True,
        include_best_practices=True,
    )
    
    try:
        if request.analysis_type == "security":
            report = await analyzer.analyze_security(request.code, request.language)
        elif request.analysis_type == "performance":
            report = await analyzer.analyze_performance(request.code, request.language)
        elif request.analysis_type == "architecture":
            report = await analyzer.analyze_architecture(request.code, request.language)
        else:
            result = await analyzer.llm.analyze_code(
                code=request.code,
                language=request.language,
                options=options,
            )
            report = type('Report', (), {
                'title': f"{request.language}代码分析",
                'content': result.content,
                'findings': analyzer._extract_findings(result.content),
                'recommendations': analyzer._extract_recommendations(result.content),
                'quality_score': 8.0,
                'confidence': 0.85,
                'processing_time': result.latency,
            })()
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "content": report.content,
                "findings": report.findings,
                "recommendations": report.recommendations,
                "quality_score": report.quality_score,
                "confidence": report.confidence,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/file")
async def analyze_file(request: FileAnalysisRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """分析文件"""
    logger.info(f"Analyzing file: {request.file_path}")
    
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        report = await analyzer.analyze_file(request.file_path)
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "content": report.content,
                "findings": report.findings,
                "recommendations": report.recommendations,
                "quality_score": report.quality_score,
                "confidence": report.confidence,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/project")
async def analyze_project(request: ProjectAnalysisRequest) -> Dict[str, Any]:
    """分析项目"""
    logger.info(f"Analyzing project: {request.project_path}")
    
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        result = await analyzer.analyze_project(request.project_path)
        
        summary = result.get("summary")
        
        return {
            "status": "success",
            "data": {
                "files_analyzed": len(result.get("files", {})),
                "summary": {
                    "title": summary.title,
                    "content": summary.content,
                    "findings": summary.findings,
                    "recommendations": summary.recommendations,
                    "quality_score": summary.quality_score,
                },
                "file_reports": [
                    {
                        "file": file,
                        "title": report.title,
                        "quality_score": report.quality_score,
                        "findings_count": len(report.findings),
                    }
                    for file, report in result.get("files", {}).items()
                ]
            }
        }
    except Exception as e:
        logger.error(f"Project analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/tests")
async def generate_tests(request: TestGenerationRequest) -> Dict[str, Any]:
    """生成测试用例"""
    logger.info(f"Generating tests for {request.language} code")
    
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        report = await analyzer.generate_tests(
            code=request.code,
            language=request.language,
            test_framework=request.test_framework,
        )
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "content": report.content,
                "recommendations": report.recommendations,
                "quality_score": report.quality_score,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refactor")
async def suggest_refactoring(request: RefactoringRequest) -> Dict[str, Any]:
    """重构建议"""
    logger.info(f"Generating refactoring suggestions for {request.language}")
    
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        report = await analyzer.suggest_refactoring(
            code=request.code,
            language=request.language,
        )
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "content": report.content,
                "findings": report.findings,
                "recommendations": report.recommendations,
                "quality_score": report.quality_score,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Refactoring suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/document")
async def document_code(request: DocumentationRequest) -> Dict[str, Any]:
    """生成文档"""
    logger.info(f"Generating documentation for {request.language} code")
    
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        report = await analyzer.document_code(
            code=request.code,
            language=request.language,
            doc_format=request.doc_format,
        )
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "content": report.content,
                "recommendations": report.recommendations,
                "quality_score": report.quality_score,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def explain_code(request: CodeAnalysisRequest) -> Dict[str, Any]:
    """解释代码"""
    logger.info(f"Explaining {request.language} code")
    
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        report = await analyzer.explain_code(
            code=request.code,
            language=request.language,
        )
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "content": report.content,
                "quality_score": report.quality_score,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Code explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_alternatives(request: ComparisonRequest) -> Dict[str, Any]:
    """比较替代方案"""
    logger.info(f"Comparing {len(request.alternatives)} alternatives")
    
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        report = await analyzer.compare_alternatives(
            code=request.code,
            alternatives=request.alternatives,
            language=request.language,
        )
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "content": report.content,
                "findings": report.findings,
                "recommendations": report.recommendations,
                "quality_score": report.quality_score,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain-error")
async def explain_error(request: ErrorAnalysisRequest) -> Dict[str, Any]:
    """解释错误"""
    logger.info("Analyzing error")
    
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        result = await analyzer.llm.explain_error(
            error_message=request.error_message,
            code_context=request.code_context,
            stack_trace=request.stack_trace,
        )
        
        return {
            "status": "success",
            "data": {
                "content": result.content,
                "processing_time": result.latency,
            }
        }
    except Exception as e:
        logger.error(f"Error analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """获取LLM统计信息"""
    analyzer = EnhancedCodeAnalyzer()
    
    try:
        stats = analyzer.get_llm_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/comprehensive")
async def analyze_comprehensive(request: CodeAnalysisRequest) -> Dict[str, Any]:
    """综合分析 - 静态分析 + LLM分析"""
    logger.info(f"Comprehensive analysis for {request.language} code")
    
    analyzer = EnhancedAnalyzer()
    
    options = AnalysisOptions(
        depth=AnalysisDepth[request.depth.upper()],
        include_security=True,
        include_performance=True,
        include_best_practices=True,
    )
    
    try:
        report = await analyzer.analyze_code(
            code=request.code,
            language=request.language,
            options=options,
        )
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "summary": report.summary,
                "content": report.llm_insights,
                "findings": [
                    {
                        "severity": f.severity,
                        "category": f.category,
                        "title": f.title,
                        "description": f.description,
                        "location": f.location,
                        "line_number": f.line_number,
                        "code_snippet": f.code_snippet,
                        "suggestion": f.suggestion,
                    }
                    for f in report.findings
                ],
                "recommendations": report.recommendations,
                "metrics": report.metrics,
                "quality_score": report.quality_score,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/security-deep")
async def analyze_security_deep(request: CodeAnalysisRequest) -> Dict[str, Any]:
    """深度安全分析"""
    logger.info(f"Deep security analysis for {request.language} code")
    
    analyzer = EnhancedAnalyzer()
    
    try:
        report = await analyzer.analyze_security_deep(
            code=request.code,
            language=request.language,
        )
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "summary": report.summary,
                "content": report.llm_insights,
                "findings": [
                    {
                        "severity": f.severity,
                        "category": f.category,
                        "title": f.title,
                        "description": f.description,
                        "location": f.location,
                        "line_number": f.line_number,
                        "code_snippet": f.code_snippet,
                        "cwe_id": f.cwe_id,
                    }
                    for f in report.findings
                ],
                "recommendations": report.recommendations,
                "quality_score": report.quality_score,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Deep security analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/performance-deep")
async def analyze_performance_deep(request: CodeAnalysisRequest) -> Dict[str, Any]:
    """深度性能分析"""
    logger.info(f"Deep performance analysis for {request.language} code")
    
    analyzer = EnhancedAnalyzer()
    
    try:
        report = await analyzer.analyze_performance_deep(
            code=request.code,
            language=request.language,
        )
        
        return {
            "status": "success",
            "data": {
                "title": report.title,
                "summary": report.summary,
                "content": report.llm_insights,
                "recommendations": report.recommendations,
                "quality_score": report.quality_score,
                "processing_time": report.processing_time,
            }
        }
    except Exception as e:
        logger.error(f"Deep performance analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-analyze")
async def batch_analyze(codes: List[CodeAnalysisRequest]) -> Dict[str, Any]:
    """批量分析"""
    logger.info(f"Batch analyzing {len(codes)} code snippets")
    
    analyzer = EnhancedCodeAnalyzer()
    
    async def analyze_one(req: CodeAnalysisRequest):
        options = AnalysisOptions(
            depth=AnalysisDepth[req.depth.upper()],
            include_security=True,
            include_performance=True,
        )
        result = await analyzer.llm.analyze_code(
            code=req.code,
            language=req.language,
            options=options,
        )
        return {
            "language": req.language,
            "content": result.content,
            "processing_time": result.latency,
        }
    
    try:
        results = await asyncio.gather(*[analyze_one(req) for req in codes])
        
        return {
            "status": "success",
            "data": {
                "total": len(results),
                "results": results,
            }
        }
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
