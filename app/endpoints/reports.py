from litestar import Controller, get, post
from litestar.params import Parameter
from litestar.status_codes import HTTP_404_NOT_FOUND
from litestar.exceptions import HTTPException
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import AsyncSessionLocal
from app.models.database_models import DailyOrderReport, Order

class ReportController(Controller):
    path = "/reports"
    
    @get("/daily")
    async def get_daily_report(
        self,
        report_date: str = Parameter(title="Дата отчета", description="Формат YYYY-MM-DD"),
        db: AsyncSession = AsyncSessionLocal()
    ) -> dict:
        try:
            date_obj = date.fromisoformat(report_date)
        except ValueError:
            raise HTTPException(
                detail="Неверный формат даты. Используйте YYYY-MM-DD",
                status_code=400
            )
        
        async with db:
            result = await db.execute(
                select(DailyOrderReport)
                .where(DailyOrderReport.report_at == date_obj)
                .order_by(DailyOrderReport.created_at.desc())
            )
            reports = result.scalars().all()
            
            if not reports:
                raise HTTPException(
                    detail=f"Отчеты за дату {report_date} не найдены",
                    status_code=HTTP_404_NOT_FOUND
                )
            
            return {
                "date": report_date,
                "reports": [
                    {
                        "id": str(report.id),
                        "order_id": str(report.order_id),
                        "count_product": report.count_product,
                        "created_at": report.created_at.isoformat()
                    }
                    for report in reports
                ]
            }
    
    @get("/daily/summary")
    async def get_daily_summary(
        self,
        report_date: str = Parameter(title="Дата отчета", description="Формат YYYY-MM-DD"),
        db: AsyncSession = AsyncSessionLocal()
    ) -> dict:
        try:
            date_obj = date.fromisoformat(report_date)
        except ValueError:
            raise HTTPException(
                detail="Неверный формат даты. Используйте YYYY-MM-DD",
                status_code=400
            )
        
        async with db:
            count_result = await db.execute(
                select(func.count(DailyOrderReport.id))
                .where(DailyOrderReport.report_at == date_obj)
            )
            total_reports = count_result.scalar()
            
            if total_reports == 0:
                raise HTTPException(
                    detail=f"Отчеты за дату {report_date} не найдены",
                    status_code=HTTP_404_NOT_FOUND
                )
            
            sum_result = await db.execute(
                select(func.sum(DailyOrderReport.count_product))
                .where(DailyOrderReport.report_at == date_obj)
            )
            total_products = sum_result.scalar() or 0
            
            return {
                "date": report_date,
                "total_reports": total_reports,
                "total_products": total_products,
                "average_products_per_order": round(total_products / total_reports, 2)
            }
    
    @post("/daily/generate")
    async def generate_report(
        self,
        report_date: str = Parameter(title="Дата для генерации", description="Формат YYYY-MM-DD"),
        db: AsyncSession = AsyncSessionLocal()
    ) -> dict:
        try:
            date_obj = date.fromisoformat(report_date)
        except ValueError:
            raise HTTPException(
                detail="Неверный формат даты. Используйте YYYY-MM-DD",
                status_code=400
            )
        
        async with db:
            existing_result = await db.execute(
                select(func.count(DailyOrderReport.id))
                .where(DailyOrderReport.report_at == date_obj)
            )
            existing_count = existing_result.scalar()
            
            if existing_count > 0:
                return {
                    "status": "already_exists",
                    "message": f"Отчет за {report_date} уже существует ({existing_count} записей)",
                    "date": report_date
                }
            
            orders_result = await db.execute(
                select(Order)
                .where(func.date(Order.created_at) == date_obj)
            )
            orders = orders_result.scalars().all()
            
            if not orders:
                return {
                    "status": "no_orders",
                    "message": f"Нет заказов за дату {report_date}",
                    "date": report_date
                }
            
            reports_created = 0
            for order in orders:
                report = DailyOrderReport(
                    report_at=date_obj,
                    order_id=order.id,
                    count_product=order.quantity or 1
                )
                db.add(report)
                reports_created += 1
            
            await db.commit()
            
            return {
                "status": "success",
                "message": f"Создано {reports_created} отчетов за {report_date}",
                "date": report_date,
                "reports_created": reports_created
            }
    
    @get("/count")
    async def get_total_reports(self, db: AsyncSession = AsyncSessionLocal()) -> dict:
        async with db:
            result = await db.execute(select(func.count(DailyOrderReport.id)))
            count = result.scalar()
            return {"total_reports": count}