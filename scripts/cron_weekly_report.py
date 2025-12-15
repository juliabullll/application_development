#!/usr/bin/env python3
import sys
import os
import asyncio
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report_service import ReportService

async def main():
    print("CRON: Еженедельный сводный отчет")
    
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=6)
    
    try:
        result = await ReportService.generate_summary_report(start_date, end_date)
        
        if result["status"] == "success":
            print(f"УСПЕХ: Сводный отчет с {start_date} по {end_date}")
            print(f"Охвачено дней: {result['days_count']}")
            
            if result["summary"]:
                total_orders = sum(day["total_orders"] for day in result["summary"])
                total_products = sum(day["total_products"] for day in result["summary"])
                print(f"Всего заказов: {total_orders}")
                print(f"Всего продукции: {total_products}")
            
            with open("/var/log/cron_weekly_report.log", "a") as f:
                f.write(f"{date.today().isoformat()} | WEEKLY | {result}\n")
            
            sys.exit(0)
        else:
            print(f"ОШИБКА: {result.get('message', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())