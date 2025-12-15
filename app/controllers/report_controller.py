from datetime import date, timedelta
from typing import Optional
from litestar import Controller, get, post
from litestar.params import Parameter
from litestar.status_codes import HTTP_200_OK
from pydantic import BaseModel
from app.services.report_service import ReportService

class ReportRequest(BaseModel):
    report_date: Optional[date] = None

class CronTaskRequest(BaseModel):
    task: str = "daily"

class ReportController(Controller):
    path = "/api/v1/reports"
    
    @post("/generate-daily", status_code=HTTP_200_OK)
    async def generate_daily_report(self, data: ReportRequest) -> dict:
        result = await ReportService.generate_daily_order_report(data.report_date)
        return result
    
    @get("/daily/{report_date:date}", status_code=HTTP_200_OK)
    async def get_daily_report(self, report_date: date) -> dict:
        result = await ReportService.get_daily_report(report_date)
        return result
    
    @get("/summary", status_code=HTTP_200_OK)
    async def get_summary_report(
        self,
        start_date: date = Parameter(default_factory=lambda: date.today() - timedelta(days=7)),
        end_date: date = Parameter(default_factory=date.today)
    ) -> dict:
        result = await ReportService.generate_summary_report(start_date, end_date)
        return result
    
    @get("/cron-test", status_code=HTTP_200_OK)
    async def test_cron_endpoint(self) -> dict:
        return {
            "status": "success",
            "message": "Cron endpoint is working",
            "timestamp": date.today().isoformat()
        }
    
    @post("/run-cron-manual", status_code=HTTP_200_OK)
    async def run_cron_manual(self, data: CronTaskRequest) -> dict:
        import subprocess
        import asyncio
        
        scripts = {
            "daily": "/app/scripts/cron_daily_report.py",
            "weekly": "/app/scripts/cron_weekly_report.py",
            "clean": "/app/scripts/clean_old_reports.py",
            "test": "/app/scripts/test_cron.py"
        }
        
        if data.task not in scripts:
            return {"status": "error", "message": f"Unknown task: {data.task}"}
        
        script_path = scripts[data.task]
        
        try:
            process = await asyncio.create_subprocess_exec(
                "python", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "task": data.task,
                "return_code": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else ""
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}