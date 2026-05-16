"""
Data Pipeline and Batch Processing
批量文件处理、项目扫描、数据管道
"""

import os
import time
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from enterprise_agent_system.infrastructure.config_manager import get_config
from enterprise_agent_system.infrastructure.advanced_logging import get_logger

logger = get_logger("pipeline")


@dataclass
class FileAnalysisTask:
    """文件分析任务"""
    file_path: str
    file_type: str
    language: str
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class PipelineProgress:
    """管道进度"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    current_task: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class DataPipeline:
    """数据管道处理器"""
    
    def __init__(self, max_workers: int = 10):
        self.config = get_config()
        self.max_workers = max_workers
        self.progress = PipelineProgress()
    
    def scan_project(
        self,
        project_path: str,
        extensions: Optional[List[str]] = None
    ) -> List[FileAnalysisTask]:
        """扫描项目"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs']
        
        tasks: List[FileAnalysisTask] = []
        project_dir = Path(project_path)
        
        if not project_dir.exists():
            logger.error(f"Project path does not exist: {project_path}")
            return tasks
        
        logger.info(f"Scanning project: {project_path}")
        
        for ext in extensions:
            for file_path in project_dir.rglob(f"*{ext}"):
                # 跳过隐藏目录和常见排除目录
                if any(part.startswith('.') or part in (
                    'node_modules', '__pycache__', 'venv', '.venv',
                    'build', 'dist', 'target'
                ) for part in file_path.parts):
                    continue
                
                task = FileAnalysisTask(
                    file_path=str(file_path),
                    file_type=ext[1:],
                    language=self._guess_language(file_path)
                )
                tasks.append(task)
        
        logger.info(f"Found {len(tasks)} files to analyze")
        self.progress.total_tasks = len(tasks)
        return tasks
    
    def execute_pipeline(
        self,
        tasks: List[FileAnalysisTask],
        processor_func: Callable[[FileAnalysisTask], Any]
    ) -> List[FileAnalysisTask]:
        """执行数据管道"""
        self.progress.start_time = time.time()
        logger.info(f"Starting pipeline with {len(tasks)} tasks")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self._process_task, task, processor_func): task
                for task in tasks
            }
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                self.progress.current_task = task.file_path
                
                try:
                    result = future.result()
                    task.status = "completed"
                    task.result = result
                    self.progress.completed_tasks += 1
                except Exception as e:
                    task.status = "failed"
                    task.error = str(e)
                    self.progress.failed_tasks += 1
                    logger.error(f"Task failed: {task.file_path} - {e}")
        
        self.progress.end_time = time.time()
        
        logger.info(f"Pipeline completed: {self.progress.completed_tasks} succeeded, "
                   f"{self.progress.failed_tasks} failed")
        
        return tasks
    
    def _process_task(
        self,
        task: FileAnalysisTask,
        processor_func: Callable[[FileAnalysisTask], Any]
    ) -> Any:
        """处理单个任务"""
        task.start_time = time.time()
        task.status = "in_progress"
        
        try:
            result = processor_func(task)
            task.end_time = time.time()
            return result
        except Exception:
            task.end_time = time.time()
            raise
    
    def get_progress(self) -> Dict[str, Any]:
        """获取进度信息"""
        elapsed = 0.0
        if self.progress.start_time:
            if self.progress.end_time:
                elapsed = self.progress.end_time - self.progress.start_time
            else:
                elapsed = time.time() - self.progress.start_time
        
        return {
            "total_tasks": self.progress.total_tasks,
            "completed_tasks": self.progress.completed_tasks,
            "failed_tasks": self.progress.failed_tasks,
            "current_task": self.progress.current_task,
            "progress_percent": (
                (self.progress.completed_tasks + self.progress.failed_tasks) /
                self.progress.total_tasks * 100
                if self.progress.total_tasks > 0 else 0
            ),
            "elapsed_seconds": elapsed,
        }
    
    def _guess_language(self, file_path: Path) -> str:
        """根据文件类型猜测语言"""
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
        }
        return language_map.get(ext, 'unknown')


class PipelineResultExporter:
    """管道结果导出器"""
    
    @staticmethod
    def export_json(tasks: List[FileAnalysisTask], output_path: str):
        """导出 JSON"""
        import json
        
        data = [
            {
                "file_path": task.file_path,
                "file_type": task.file_type,
                "language": task.language,
                "status": task.status,
                "result": task.result,
                "error": task.error,
                "processing_time": (
                    task.end_time - task.start_time
                    if task.end_time and task.start_time else None
                )
            }
            for task in tasks
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results exported to {output_path}")
    
    @staticmethod
    def export_html(tasks: List[FileAnalysisTask], output_path: str):
        """导出 HTML 报告"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ margin-bottom: 20px; }}
        .task {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
        .success {{ background-color: #d4edda; border-color: #c3e6cb; }}
        .failed {{ background-color: #f8d7da; border-color: #f5c6cb; }}
        h1, h2, h3 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>Code Analysis Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total tasks: {len(tasks)}</p>
        <p>Completed: {sum(1 for t in tasks if t.status == 'completed')}</p>
        <p>Failed: {sum(1 for t in tasks if t.status == 'failed')}</p>
    </div>
    <h2>Tasks</h2>
    {''.join([f'''
    <div class="task {'success' if task.status == 'completed' else 'failed'}">
        <h3>{Path(task.file_path).name}</h3>
        <p>File: {task.file_path}</p>
        <p>Language: {task.language}</p>
        <p>Status: {task.status}</p>
        {f'<p>Error: {task.error}</p>' if task.error else ''}
    </div>
    ''' for task in tasks])}
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report exported to {output_path}")


# 示例使用
def create_sample_pipeline():
    """创建示例管道"""
    def sample_processor(task: FileAnalysisTask) -> Dict:
        with open(task.file_path, 'r') as f:
            content = f.read()
        return {
            "file_path": task.file_path,
            "lines_of_code": len(content.splitlines()),
            "chars": len(content)
        }
    
    return DataPipeline(), sample_processor
