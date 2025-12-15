import os
import sys
from pathlib import Path
from datetime import datetime
from litestar import Litestar, get, post
from litestar.openapi import OpenAPIConfig
from litestar.params import Parameter
from litestar.status_codes import HTTP_404_NOT_FOUND
from litestar.exceptions import HTTPException

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.endpoints import reports
from app.db.session import AsyncSessionLocal
from app.models.database_models import DailyOrderReport, Order
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

@get("/")
async def root() -> dict:
    return {
        "message": "Report System API",
        "endpoints": {
            "docs": "/schema",
            "get_report": "GET /report?report_date=YYYY-MM-DD",
            "summary": "GET /report/summary?report_date=YYYY-MM-DD",
            "detailed": "GET /report/detailed?report_date=YYYY-MM-DD",
            "generate": "POST /report/generate?report_date=YYYY-MM-DD",
            "count": "GET /report/count"
        }
    }

@get("/report")
async def get_daily_report(
    report_date: str = Parameter(title="Дата отчета", description="Формат YYYY-MM-DD"),
    db: AsyncSession = AsyncSessionLocal()
) -> dict:
    try:
        from datetime import date
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
        reports_list = result.scalars().all()
        
        if not reports_list:
            raise HTTPException(
                detail=f"Отчеты за дату {report_date} не найдены",
                status_code=HTTP_404_NOT_FOUND
            )
        
        return {
            "date": report_date,
            "total_reports": len(reports_list),
            "reports": [
                {
                    "id": str(report.id),
                    "order_id": str(report.order_id),
                    "count_product": report.count_product,
                    "created_at": report.created_at.isoformat()
                }
                for report in reports_list
            ]
        }

@get("/report/summary")
async def get_daily_summary(
    report_date: str = Parameter(title="Дата отчета", description="Формат YYYY-MM-DD"),
    db: AsyncSession = AsyncSessionLocal()
) -> dict:
    try:
        from datetime import date
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
            "average_products_per_order": round(total_products / total_reports, 2) if total_reports > 0 else 0
        }

@post("/report/generate")
async def generate_report(
    report_date: str = Parameter(title="Дата для генерации", description="Формат YYYY-MM-DD"),
    db: AsyncSession = AsyncSessionLocal()
) -> dict:
    try:
        from datetime import date
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

@get("/report/count")
async def get_total_reports(db: AsyncSession = AsyncSessionLocal()) -> dict:
    async with db:
        result = await db.execute(select(func.count(DailyOrderReport.id)))
        count = result.scalar()
        return {"total_reports": count}

@get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Report System API"
    }

app = Litestar(
    route_handlers=[
        root,
        get_daily_report,
        get_daily_summary,
        generate_report,
        get_total_reports,
        health_check
    ],
    debug=True,
    cors_config={"allow_origins": ["*"]},
    openapi_config=OpenAPIConfig(
        title="Report System API",
        version="1.0.0",
        description="API для работы с отчетами по заказам"
    )
)

if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting Report System API on {HOST}:{PORT}")
    print(f"Swagger UI: http://{HOST}:{PORT}/schema")
    print(f"OpenAPI schema: http://{HOST}:{PORT}/schema/openapi.json")
    
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )  