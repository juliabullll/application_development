import pytest
import asyncio
from app.repositories.product_repository import ProductRepository
from app.models import Product, ProductCreate, ProductUpdate

class TestProductRepository:
    """Тесты для ProductRepository"""
    
    def test_create_product(self, product_repository: ProductRepository, session):
        """Тест создания продукта"""
        product_data = ProductCreate(
            name="Test Product",
            description="Test product description",
            price=99.99
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            product = loop.run_until_complete(product_repository.create(session, product_data))
            
            assert product.id is not None
            assert product.name == "Test Product"
            assert product.description == "Test product description"
            assert product.price == 99.99
            
            print("Create product - SUCCESS")
        finally:
            loop.close()

    def test_get_product_by_id(self, product_repository: ProductRepository, session):
        """Тест получения продукта по ID"""
        product_data = ProductCreate(
            name="Product to find",
            description="Product to find by ID",
            price=50.0
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            product = loop.run_until_complete(product_repository.create(session, product_data))
            
            found_product = loop.run_until_complete(product_repository.get_by_id(session, product.id))
            
            assert found_product is not None
            assert found_product.id == product.id
            assert found_product.name == "Product to find"
            
            print("Get product by ID - SUCCESS")
        finally:
            loop.close()

    def test_update_product(self, product_repository: ProductRepository, session):
        """Тест обновления продукта"""
        product_data = ProductCreate(
            name="Original Product",
            description="Original description",
            price=100.0
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            product = loop.run_until_complete(product_repository.create(session, product_data))
            
            update_data = ProductUpdate(
                name="Updated Product",
                price=150.0
            )
            updated_product = loop.run_until_complete(product_repository.update(session, product.id, update_data))
            
            assert updated_product.name == "Updated Product"
            assert updated_product.price == 150.0
            assert updated_product.description == "Original description"  # Не меняли
            
            print("Update product - SUCCESS")
        finally:
            loop.close()

    def test_delete_product(self, product_repository: ProductRepository, session):
        """Тест удаления продукта"""
        product_data = ProductCreate(
            name="Product to delete",
            description="Will be deleted",
            price=25.0
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            product = loop.run_until_complete(product_repository.create(session, product_data))
            
            result = loop.run_until_complete(product_repository.delete(session, product.id))
            
            assert result is True
            
            found_product = loop.run_until_complete(product_repository.get_by_id(session, product.id))
            assert found_product is None
            
            print("Delete product - SUCCESS")
        finally:
            loop.close()

    def test_get_all_products(self, product_repository: ProductRepository, session):
        """Тест получения всех продуктов"""
        products_data = [
            ProductCreate(name="Product A", description="Desc A", price=10.0),
            ProductCreate(name="Product B", description="Desc B", price=20.0),
            ProductCreate(name="Product C", description="Desc C", price=30.0)
        ]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            for product_data in products_data:
                loop.run_until_complete(product_repository.create(session, product_data))
            
            products = loop.run_until_complete(product_repository.get_by_filter(session, count=100, page=1))
            
            assert len(products) >= 3
            
            product_names = [product.name for product in products]
            assert "Product A" in product_names
            assert "Product B" in product_names
            assert "Product C" in product_names
            
            print("Get all products - SUCCESS")
        finally:
            loop.close()