from datetime import date, timedelta
from typing import Optional, Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.db.session import get_async_session
from app.repositories.report_repository import ReportRepository
from app.models.database_models import DailyOrderReport

logger = logging.getLogger(__name__)

class ReportService:
    
    @staticmethod
    async def generate_daily_order_report(
        report_date: Optional[date] = None
    ) -> Dict[str, Any]:
        if report_date is None:
            report_date = date.today() - timedelta(days=1)
            
        logger.info(f"Генерация ежедневного отчета за {report_date}")
        
        async for session in get_async_session():
            try:
                orders = await ReportRepository.get_orders_by_date(session, report_date)
                
                reports_generated = 0
                for order in orders:
                    count_product = await ReportRepository.get_order_product_count(
                        session, order.id
                    )
                    
                    await ReportRepository.create_daily_report(
                        session=session,
                        report_at=report_date,
                        order_id=order.id,
                        count_product=count_product
                    )
                    
                    reports_generated += 1
                
                logger.info(f"Сгенерировано {reports_generated} отчетов за {report_date}")
                return {
                    "status": "success",
                    "reports_generated": reports_generated,
                    "date": report_date.isoformat()
                }
                
            except Exception as e:
                logger.error(f"Ошибка генерации отчета: {e}")
                await session.rollback()
                return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def get_daily_report(report_date: date) -> Dict[str, Any]:
        async for session in get_async_session():
            try:
                reports = await ReportRepository.get_daily_reports(session, report_date)
                
                return {
                    "status": "success",
                    "date": report_date.isoformat(),
                    "reports": [
                        {
                            "id": str(r.id),
                            "order_id": str(r.order_id),
                            "count_product": r.count_product,
                            "created_at": r.created_at.isoformat()
                        }
                        for r in reports
                    ],
                    "total_reports": len(reports),
                    "total_products": sum(r.count_product for r in reports)
                }
            except Exception as e:
                logger.error(f"Ошибка получения отчета: {e}")
                return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def generate_summary_report(
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        async for session in get_async_session():
            try:
                result = await session.execute(
                    select(
                        DailyOrderReport.report_at,
                        func.count(DailyOrderReport.id).label("total_orders"),
                        func.sum(DailyOrderReport.count_product).label("total_products"),
                        func.avg(DailyOrderReport.count_product).label("avg_products_per_order")
                    )
                    .where(DailyOrderReport.report_at.between(start_date, end_date))
                    .group_by(DailyOrderReport.report_at)
                    .order_by(DailyOrderReport.report_at)
                )
                
                summary = result.all()
                report_data = []
                for row in summary:
                    report_data.append({
                        "date": row.report_at,
                        "total_orders": row.total_orders,
                        "total_products": row.total_products,
                        "avg_products_per_order": float(row.avg_products_per_order or 0)
                    })
                
                return {
                    "status": "success",
                    "period": {"start": start_date, "end": end_date},
                    "summary": report_data,
                    "days_count": len(report_data)
                }
                
            except Exception as e:
                logger.error(f"Ошибка генерации сводного отчета: {e}")
                return {"status": "error", "message": str(e)}