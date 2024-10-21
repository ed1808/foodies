import io, os

from django.db.transaction import atomic
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase
from faker import Faker
from pathlib import Path
from PIL import Image
from random import randint
from rest_framework.test import APIClient
from rest_framework import status

from categories.models import Category
from companies.models import Company
from customers.models import Customer
from document_types.models import DocumentType
from employees.models import Employee
from products.models import Product

from .models import Order, OrderDetail


class OrderModelTest(TestCase):

    def setUp(self):
        # Configurar Faker para generar datos ficticios
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))

        # Crear una instancia de Company
        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )
        self.company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un cliente
        self.customer = Customer.objects.create(
            name=self.faker.name(),
            phone_number=self.faker.phone_number(),
            address=self.faker.address(),
            neighborhood="Test neighborhood",
        )

        self.customer.companies.add(self.company)

    def test_create_order(self):
        """Probar que se puede crear una orden correctamente"""
        order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )

        self.assertIsInstance(order, Order)
        self.assertEqual(order.attended_by, self.user)
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.company, self.company)

    def test_created_at_auto_now_add(self):
        """Probar que el campo 'created_at' se rellena automáticamente en la creación"""
        order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )
        self.assertIsNotNone(order.created_at)

    def test_updated_at_auto_now(self):
        """Probar que el campo 'updated_at' se actualiza automáticamente"""
        order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )
        original_updated_at = order.updated_at

        # Actualizar el pedido
        order.save()
        self.assertNotEqual(order.updated_at, original_updated_at)

    def test_order_str_representation(self):
        """Probar que el método __str__ devuelve el formato esperado"""
        order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )
        self.assertEqual(str(order), f"Orden #{order.id}")

    def test_delete_user_protected(self):
        """Probar que eliminar un usuario relacionado con una orden está protegido"""
        order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )

        with self.assertRaises(
            Exception
        ):  # Debe lanzar una excepción por la protección
            self.user.delete()

        # Asegurarse de que la orden aún exista
        self.assertTrue(Order.objects.filter(id=order.id).exists())

    def test_delete_customer_protected(self):
        """Probar que eliminar un cliente relacionado con una orden está protegido"""
        order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )

        with self.assertRaises(
            Exception
        ):  # Debe lanzar una excepción por la protección
            self.customer.delete()

        # Asegurarse de que la orden aún exista
        self.assertTrue(Order.objects.filter(id=order.id).exists())

    def test_delete_company_protected(self):
        """Probar que eliminar una compañía relacionada con una orden está protegido"""
        order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )

        with self.assertRaises(
            Exception
        ):  # Debe lanzar una excepción por la protección
            self.company.delete()

        # Asegurarse de que la orden aún exista
        self.assertTrue(Order.objects.filter(id=order.id).exists())


class OrderDetailModelTest(TestCase):

    def setUp(self):
        # Configurar Faker para generar datos ficticios
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))

        # Crear una instancia de Company
        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )
        self.company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un cliente
        self.customer = Customer.objects.create(
            name=self.faker.name(),
            phone_number=self.faker.phone_number(),
            address=self.faker.address(),
            neighborhood="Test neighborhood",
        )

        self.customer.companies.add(self.company)

        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        self.product = Product.objects.create(
            name="Test product",
            description=self.faker.paragraph(),
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            category=self.category,
            company=self.company,
        )

        self.order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )

    def tearDown(self) -> None:
        try:
            os.remove(
                Path(__file__).resolve().parent.parent / "static/images/test_image.jpg"
            )
        except FileNotFoundError:
            pass

    def generate_test_image(self):
        image = Image.new("RGB", (100, 100), color="red")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        return SimpleUploadedFile(
            "test_image.jpg", byte_io.read(), content_type="image/jpeg"
        )

    def test_create_order_detail(self):
        """Probar que se puede crear un detalle de pedido correctamente"""
        order_detail = OrderDetail.objects.create(
            order=self.order, product=self.product, quantity=5
        )

        self.assertIsInstance(order_detail, OrderDetail)
        self.assertEqual(order_detail.order, self.order)
        self.assertEqual(order_detail.product, self.product)
        self.assertEqual(order_detail.quantity, 5)

    def test_quantity_is_positive(self):
        """Probar que el campo 'quantity' es un entero positivo"""
        order_detail = OrderDetail.objects.create(
            order=self.order, product=self.product, quantity=10
        )
        self.assertGreater(order_detail.quantity, 0)

    def test_order_detail_str_representation(self):
        """Probar que el método __str__ devuelve el formato esperado"""
        order_detail = OrderDetail.objects.create(
            order=self.order, product=self.product, quantity=3
        )
        self.assertEqual(str(order_detail), f"Detalle del pedido #{order_detail.id}")

    def test_delete_product_protected(self):
        """Probar que eliminar un producto relacionado con un detalle de pedido está protegido"""
        order_detail = OrderDetail.objects.create(
            order=self.order, product=self.product, quantity=5
        )

        with self.assertRaises(
            Exception
        ):  # Debe lanzar una excepción por la protección
            self.product.delete()

        # Asegurarse de que el detalle del pedido aún exista
        self.assertTrue(OrderDetail.objects.filter(id=order_detail.id).exists())

    def test_delete_order_cascade(self):
        """Probar que eliminar un pedido también elimina los detalles asociados"""
        order_detail = OrderDetail.objects.create(
            order=self.order, product=self.product, quantity=5
        )

        # Eliminar el pedido
        self.order.delete()

        # Verificar que el detalle del pedido haya sido eliminado en cascada
        self.assertFalse(OrderDetail.objects.filter(id=order_detail.id).exists())


class OrderListViewTest(TestCase):

    def setUp(self):
        # Configurar Faker para generar datos ficticios
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))

        # Crear una instancia de Company
        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )

        self.company1 = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        self.company2 = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        self.user1 = User.objects.create_user(username="user1", password="password")
        self.user2 = User.objects.create_user(username="user2", password="password")

        self.employee1 = Employee.objects.create(user=self.user1, company=self.company1)
        self.employee2 = Employee.objects.create(user=self.user2, company=self.company2)

        # Crear un cliente
        self.customer1 = Customer.objects.create(
            name=self.faker.name(),
            phone_number=self.faker.phone_number(),
            address=self.faker.address(),
            neighborhood="Test neighborhood",
        )

        self.customer2 = Customer.objects.create(
            name=self.faker.name(),
            phone_number=self.faker.phone_number(),
            address=self.faker.address(),
            neighborhood="Test neighborhood",
        )

        self.customer1.companies.add(self.company1)
        self.customer2.companies.add(self.company2)

        # Crear pedidos para las compañías
        self.order1 = Order.objects.create(
            attended_by=self.user1, customer=self.customer1, company=self.company1
        )
        self.order2 = Order.objects.create(
            attended_by=self.user2, customer=self.customer2, company=self.company2
        )

    def test_redirect_if_not_logged_in(self):
        """Probar que la vista redirige al login si el usuario no está autenticado"""
        response = self.client.get(reverse("orders"))
        self.assertRedirects(response, "/employees/login/?next=/orders/")

    def test_logged_in_user_can_access_order_list(self):
        """Probar que un usuario autenticado puede acceder a la lista de pedidos"""
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("orders"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders.html")

    def test_orders_filtered_by_company(self):
        """Probar que la vista solo muestra los pedidos de la compañía del usuario autenticado"""
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("orders"))

        # Verificar que solo los pedidos de la compañía del usuario autenticado están presentes
        self.assertQuerySetEqual(
            response.context["orders"],
            [self.order1],  # Solo debería ver el pedido de su compañía
            transform=lambda x: x,
        )

    def test_other_company_orders_not_shown(self):
        """Probar que los pedidos de otra compañía no se muestran al usuario"""
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("orders"))

        # Verificar que el pedido de la otra compañía no esté presente
        self.assertNotIn(self.order2, response.context["orders"])

    def test_context_object_name(self):
        """Probar que la clave de contexto 'orders' está presente en la vista"""
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("orders"))
        self.assertIn("orders", response.context)


class OrderDetailViewTest(TestCase):

    def setUp(self):

        # Configurar Faker para generar datos ficticios
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))

        # Crear una instancia de Company
        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )

        self.company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        self.user = User.objects.create_user(username="testuser", password="password")

        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un cliente
        self.customer = Customer.objects.create(
            name=self.faker.name(),
            phone_number=self.faker.phone_number(),
            address=self.faker.address(),
            neighborhood="Test neighborhood",
        )

        self.customer.companies.add(self.company)

        # Crear pedidos para las compañías
        self.order = Order.objects.create(
            attended_by=self.user, customer=self.customer, company=self.company
        )

        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        # Crear productos
        self.product1 = Product.objects.create(
            name="Test product",
            description=self.faker.paragraph(),
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            category=self.category,
            company=self.company,
        )

        self.product2 = Product.objects.create(
            name="Test product",
            description=self.faker.paragraph(),
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            category=self.category,
            company=self.company,
        )

        # Crear detalles del pedido
        self.order_detail1 = OrderDetail.objects.create(
            order=self.order, product=self.product1, quantity=2
        )
        self.order_detail2 = OrderDetail.objects.create(
            order=self.order, product=self.product2, quantity=3
        )

    def tearDown(self) -> None:
        try:
            os.remove(
                Path(__file__).resolve().parent.parent / "static/images/test_image.jpg"
            )
        except FileNotFoundError:
            pass

    def generate_test_image(self):
        image = Image.new("RGB", (100, 100), color="red")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        return SimpleUploadedFile(
            "test_image.jpg", byte_io.read(), content_type="image/jpeg"
        )

    def test_redirect_if_not_logged_in(self):
        """Probar que la vista redirige al login si el usuario no está autenticado"""
        response = self.client.get(
            reverse("detail_order", kwargs={"id": self.order.id})
        )
        self.assertRedirects(
            response, f"/employees/login/?next=/orders/order-details/{self.order.id}/"
        )

    def test_logged_in_user_can_access_order_detail(self):
        """Probar que un usuario autenticado puede acceder a los detalles del pedido"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(
            reverse("detail_order", kwargs={"id": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "detail_order.html")

    def test_order_details_filtered_by_order_id(self):
        """Probar que la vista solo muestra los detalles del pedido correspondiente al ID"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(
            reverse("detail_order", kwargs={"id": self.order.id})
        )

        # Verificar que solo los detalles del pedido con el ID especificado están presentes
        self.assertQuerySetEqual(
            list(response.context["order_detail"]),
            [self.order_detail1, self.order_detail2],  # Detalles del pedido esperado
            transform=lambda x: x,
        )

    def test_context_object_name(self):
        """Probar que la clave de contexto 'order_detail' está presente en la vista"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(
            reverse("detail_order", kwargs={"id": self.order.id})
        )
        self.assertIn("order_detail", response.context)

    def test_no_order_details_for_invalid_order_id(self):
        """Probar que no se muestran detalles si se proporciona un ID de pedido no válido"""
        self.client.login(username="testuser", password="password")
        invalid_order_id = 999  # Un ID de pedido que no existe
        response = self.client.get(
            reverse("detail_order", kwargs={"id": invalid_order_id})
        )

        # Verificar que no hay detalles de pedido para un ID no válido
        self.assertQuerySetEqual(response.context["order_detail"], [])


class OrderCreateViewTest(TestCase):

    def setUp(self):
        # Crear un usuario para las pruebas
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_redirect_if_not_logged_in(self):
        """Probar que la vista redirige al login si el usuario no está autenticado"""
        response = self.client.get(reverse("create_order"))
        self.assertRedirects(response, "/employees/login/?next=/orders/add-order/")

    def test_logged_in_user_can_access_create_order_view(self):
        """Probar que un usuario autenticado puede acceder a la vista de crear pedido"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("create_order"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_order.html")

    def test_template_used(self):
        """Probar que la vista usa la plantilla correcta"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("create_order"))

        # Verificar que se use la plantilla correcta
        self.assertTemplateUsed(response, "create_order.html")


class OrderCreateAPIViewTest(TestCase):

    def setUp(self):
        # Configuración inicial: Crear usuario, compañía, cliente, y productos
        self.client_api = APIClient()

        # Configurar Faker para generar datos ficticios
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))

        # Crear una instancia de Company
        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )

        self.company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        self.user = User.objects.create_user(username="testuser", password="password")

        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un cliente
        self.customer = Customer.objects.create(
            name=self.faker.name(),
            phone_number=self.faker.phone_number(),
            address=self.faker.address(),
            neighborhood="Test neighborhood",
        )

        self.customer.companies.add(self.company)

        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        # Crear productos
        self.product1 = Product.objects.create(
            name="Test product",
            description=self.faker.paragraph(),
            price=self.faker.random_int(min=100, max=10000),
            stock=10,
            picture=self.generate_test_image(),
            category=self.category,
            company=self.company,
        )

        self.product2 = Product.objects.create(
            name="Test product",
            description=self.faker.paragraph(),
            price=self.faker.random_int(min=100, max=10000),
            stock=5,
            picture=self.generate_test_image(),
            category=self.category,
            company=self.company,
        )

    def tearDown(self) -> None:
        try:
            os.remove(
                Path(__file__).resolve().parent.parent / "static/images/test_image.jpg"
            )
        except FileNotFoundError:
            pass

    def generate_test_image(self):
        image = Image.new("RGB", (100, 100), color="red")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        return SimpleUploadedFile(
            "test_image.jpg", byte_io.read(), content_type="image/jpeg"
        )

    def test_redirect_if_not_authenticated(self):
        """Probar que el endpoint redirige si el usuario no está autenticado"""
        response = self.client_api.post(reverse("create_order_api"), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_success(self):
        """Probar que un usuario autenticado puede crear un pedido exitosamente"""
        self.client_api.force_authenticate(user=self.user)
        data = {
            "customer": self.customer.id,
            "items": [
                {"product": self.product1.id, "quantity": 2},
                {"product": self.product2.id, "quantity": 3}
            ]
        }
        response = self.client_api.post(reverse("create_order_api"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderDetail.objects.count(), 2)

        # Verificar que el stock se haya reducido correctamente
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 8)
        self.assertEqual(self.product2.stock, 2)

    def test_create_order_insufficient_stock(self):
        """Probar que no se puede crear un pedido si el producto no tiene suficiente stock"""
        self.client_api.force_authenticate(user=self.user)
        data = {
            "customer": self.customer.id,
            "items": [
                {"product": self.product1.id, "quantity": 15},  # Stock insuficiente
            ]
        }
        response = self.client_api.post(reverse("create_order_api"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["message"], "Product out of stock")

        # Asegurarse de que no se haya creado ninguna orden
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderDetail.objects.count(), 0)

    def test_create_order_invalid_product(self):
        """Probar que no se puede crear un pedido con un producto no existente"""
        self.client_api.force_authenticate(user=self.user)
        data = {
            "customer": self.customer.id,
            "items": [
                {"product": 9999, "quantity": 2},  # Producto no existente
            ]
        }
        response = self.client_api.post(reverse("create_order_api"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("Product matching query does not exist", response.data["message"])

        # Asegurarse de que no se haya creado ninguna orden
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderDetail.objects.count(), 0)

    def test_atomic_transaction_rollback(self):
        """Probar que si ocurre un error, la transacción se revierte completamente"""
        self.client_api.force_authenticate(user=self.user)
        data = {
            "customer": self.customer.id,
            "items": [
                {"product": self.product1.id, "quantity": 2},
                {"product": self.product2.id, "quantity": 10}  # Stock insuficiente para este producto
            ]
        }

        # Usar un parche para simular un error dentro de la transacción
        response = self.client_api.post(reverse("create_order_api"), data, format="json")
        self.assertEqual(response.data["status"], "error")

        # Verificar que no se haya creado ninguna orden ni detalle
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderDetail.objects.count(), 0)
