from datetime import date
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.models.database_models import DailyOrderReport, Order

class ReportRepository:
    
    @staticmethod
    async def create_daily_report(
        session: AsyncSession,
        report_at: date,
        order_id: UUID,
        count_product: int
    ) -> DailyOrderReport:
        report = DailyOrderReport(
            report_at=report_at,
            order_id=order_id,
            count_product=count_product
        )
        session.add(report)
        await session.commit()
        await session.refresh(report)
        return report
    
    @staticmethod
    async def get_daily_reports(
        session: AsyncSession,
        report_date: date
    ) -> List[DailyOrderReport]:
        result = await session.execute(
            select(DailyOrderReport)
            .where(DailyOrderReport.report_at == report_date)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_order_product_count(session: AsyncSession, order_id: UUID) -> int:
        result = await session.execute(
            select(Order.quantity).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        return order if order else 0
    
    @staticmethod
    async def get_orders_by_date(session: AsyncSession, order_date: date) -> List[Order]:
        result = await session.execute(
            select(Order)
            .where(func.date(Order.created_at) == order_date)
        )
        return result.scalars().all()
    
    @staticmethod
    async def delete_old_reports(session: AsyncSession, days_old: int = 30):
        from datetime import timedelta
        old_date = date.today() - timedelta(days=days_old)
        
        result = await session.execute(
            delete(DailyOrderReport)
            .where(DailyOrderReport.report_at < old_date)
        )
        
        await session.commit()
        return result.rowcount