"""
Project Analyzer Routes - API endpoints for project analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


router = APIRouter()


class AnalyzeProjectRequest(BaseModel):
    project_path: str = Field(..., description="项目路径")
    analysis_type: str = Field(default="auto", description="分析类型: auto, python, typescript")


class AnalysisResponse(BaseModel):
    project_name: str
    project_path: str
    project_type: str
    analysis_time: str
    statistics: Dict[str, Any]
    packages: Optional[list] = None
    quality_score: Optional[float] = None


@router.post("/analyze")
async def analyze_project(request: AnalyzeProjectRequest):
    """分析本地项目"""
    from enterprise_agent_system.infrastructure.typescript_vue_project_analyzer import (
        TypeScriptVueProjectAnalyzer
    )
    
    try:
        analyzer = TypeScriptVueProjectAnalyzer(request.project_path)
        result = analyzer.analyze_project()
        
        return {
            "project_name": result.project_name,
            "project_path": result.project_path,
            "project_type": result.project_type,
            "analysis_time": result.analysis_time,
            "statistics": {
                "total_files": result.statistics.total_files,
                "code_lines": result.statistics.code_lines,
                "packages": result.statistics.package_count,
            },
            "packages": [pkg.dict() for pkg in result.packages] if result.packages else [],
            "quality_score": 8.0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-github")
async def analyze_github_repo(owner: str, repo: str):
    """分析GitHub仓库"""
    from enterprise_agent_system.infrastructure.github_repository_analyzer import (
        GitHubRepositoryAnalyzer
    )
    
    try:
        analyzer = GitHubRepositoryAnalyzer(owner, repo)
        result = analyzer.analyze_repository()
        
        return {
            "owner": owner,
            "repo": repo,
            "result": str(result) if result else "Analysis complete",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-types")
async def get_supported_project_types():
    """获取支持的项目类型"""
    return {
        "types": [
            {
                "id": "python",
                "name": "Python",
                "extensions": [".py"],
            },
            {
                "id": "typescript",
                "name": "TypeScript/JavaScript",
                "extensions": [".ts", ".tsx", ".js", ".jsx"],
            },
            {
                "id": "vue",
                "name": "Vue.js",
                "extensions": [".vue", ".ts", ".tsx"],
            },
        ],
    }
