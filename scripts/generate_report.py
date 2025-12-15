import sys
import os
import asyncio
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report_service import ReportService

async def main():
    report_date = date.today() - timedelta(days=1)
    
    if len(sys.argv) > 1:
        try:
            report_date = date.fromisoformat(sys.argv[1])
        except ValueError:
            print(f"Неверный формат даты. Используйте: YYYY-MM-DD")
            sys.exit(1)
    
    print(f"Запуск генерации отчета за {report_date}...")
    
    result = await ReportService.generate_daily_order_report(report_date)
    
    if result["status"] == "success":
        print(f"Отчет успешно сгенерирован!")
        print(f"Дата: {report_date}")
        print(f"Сгенерировано отчетов: {result['reports_generated']}")
    else:
        print(f"Ошибка генерации отчета: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())