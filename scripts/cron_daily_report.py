#!/usr/bin/env python3
import sys
import os
import asyncio
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report_service import ReportService

async def main():
    report_date = date.today() - timedelta(days=1)
    
    print("CRON: Запуск ежедневной генерации отчетов")
    print(f"Дата отчета: {report_date}")
    
    try:
        result = await ReportService.generate_daily_order_report(report_date)
        
        if result["status"] == "success":
            print(f"УСПЕХ: Отчет за {report_date} сгенерирован")
            print(f"Создано отчетов: {result['reports_generated']}")
            
            with open("/var/log/cron_daily_report.log", "a") as f:
                f.write(f"{date.today().isoformat()} | SUCCESS | {result}\n")
            
            sys.exit(0)
        else:
            print(f"ОШИБКА: {result.get('message', 'Unknown error')}")
            
            with open("/var/log/cron_daily_report.log", "a") as f:
                f.write(f"{date.today().isoformat()} | ERROR | {result}\n")
            
            sys.exit(1)
            
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        
        with open("/var/log/cron_daily_report.log", "a") as f:
            f.write(f"{date.today().isoformat()} | CRITICAL | {str(e)}\n")
        
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())