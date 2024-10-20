import io, os
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from faker import Faker
from pathlib import Path
from PIL import Image
from random import randint
from rest_framework.test import APIClient
from rest_framework import status

from categories.models import Category
from companies.models import Company
from document_types.models import DocumentType
from employees.models import Employee

from .forms import ProductForm
from .models import Product
from .serializers import ProductsSerializer, ProductSerializer

User = get_user_model()


class ProductTest(TestCase):
    def setUp(self) -> None:
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
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
        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

    def test_create_product_returns_a_product_instance(self):
        product = Product.objects.create(
            name="Test Product",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.faker.image_url(),
            description=self.faker.paragraph(),
        )

        self.assertIsInstance(product, Product)

    def test_product_str_returns_name(self):
        product = Product.objects.create(
            name="Test Product",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.faker.image_url(),
            description=self.faker.paragraph(),
        )

        product_name = str(product)

        self.assertEqual(product.name, product_name)

    def test_delete_category_raises_protected_error(self):
        with self.assertRaises(ProtectedError):
            Product.objects.create(
                name="Test Product",
                category=self.category,
                company=self.company,
                price=self.faker.random_int(min=100, max=10000),
                stock=self.faker.random_int(min=1, max=100),
                picture=self.faker.image_url(),
                description=self.faker.paragraph(),
            )

            self.category.delete()


class ProductsListViewTest(TestCase):

    def setUp(self):
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
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

        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        self.product1 = Product.objects.create(
            name="Product 1",
            description="A test product description",
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            category=self.category,
            company=self.company,
        )
        self.product2 = Product.objects.create(
            name="Product 2",
            description="A test product description",
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            category=self.category,
            company=self.company,
        )

        other_company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        other_category = Category.objects.create(
            name="Test Category",
            company=other_company,
        )

        self.product_other = Product.objects.create(
            name="Other Product",
            description="A test product description",
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            category=other_category,
            company=other_company,
        )

        self.url = reverse("products")

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

    def test_view_requires_login(self):
        """La vista requiere que el usuario esté autenticado"""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_view_returns_correct_template(self):
        """La vista utiliza el template correcto"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products.html")

    def test_view_returns_products_for_user_company(self):
        """La vista devuelve los productos solo para la compañía del empleado autenticado"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        products = response.context["products"]

        # Asegurarse de que solo se devuelven los productos de la compañía del usuario
        self.assertIn(self.product1, products)
        self.assertIn(self.product2, products)
        self.assertNotIn(self.product_other, products)

    def test_context_object_name(self):
        """El contexto debe contener 'products' como nombre del objeto"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("products", response.context)


class ProductDetailViewTest(TestCase):

    def setUp(self):
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
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

        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        # Crear un usuario y empleado
        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un producto
        self.product = Product.objects.create(
            name="Test Product",
            description="A test product description",
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            category=self.category,
            company=self.company,
        )

        # URL de la vista
        self.url = reverse("detail_product", kwargs={"id": self.product.id})

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

    def test_view_requires_login(self):
        """La vista requiere que el usuario esté autenticado"""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_view_uses_correct_template(self):
        """La vista utiliza la plantilla correcta"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "detail_product.html")

    def test_view_returns_correct_object(self):
        """La vista devuelve el objeto correcto basado en el ID proporcionado"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)

        # Comprobar que el producto en el contexto tiene los datos correctos
        product = response.context["product"]
        self.assertEqual(product["id"], self.product.id)
        self.assertEqual(product["name"], self.product.name)
        self.assertEqual(product["description"], self.product.description)
        self.assertEqual(product["price"], self.product.price)
        self.assertEqual(product["stock"], self.product.stock)
        self.assertEqual(product["picture"], self.product.picture)
        self.assertEqual(product["category__name"], self.category.name)

    def test_invalid_product_id(self):
        """Si se pasa un ID inválido, la vista no debería encontrar el producto"""
        self.client.login(username="testuser", password="password")

        # URL con un ID que no existe
        invalid_url = reverse("detail_product", kwargs={"id": 999})
        response = self.client.get(invalid_url)

        # Verificar que el producto no se encuentra y el código de estado es 404
        self.assertEqual(response.status_code, 404)


class CreateProductViewTest(TestCase):

    def setUp(self):
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )

        # Crear una compañía
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

        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        # Crear un usuario y empleado
        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # URL de la vista
        self.url = reverse("add_product")

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

    def test_view_requires_login(self):
        """La vista requiere que el usuario esté autenticado"""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_view_uses_correct_template(self):
        """La vista utiliza la plantilla correcta"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_product.html")

    def test_view_uses_correct_form(self):
        """La vista utiliza el formulario correcto (ProductForm)"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], ProductForm)

    def test_form_valid_creates_product_with_correct_company(self):
        """Al enviar un formulario válido, el producto se crea con la compañía del usuario autenticado"""
        self.client.login(username="testuser", password="password")

        test_image = self.generate_test_image()

        product_data = {
            "name": "Test Product",
            "category": self.category.id,
            "price": self.faker.random_int(min=100, max=10000),
            "stock": self.faker.random_int(min=1, max=100),
            "picture": test_image,
            "description": self.faker.paragraph(),
        }

        # Enviar el formulario con los datos del producto
        response = self.client.post(self.url, data=product_data)

        # Verificar que el producto fue creado
        product = Product.objects.get(name="Test Product")
        self.assertEqual(product.company, self.company)

        # Verificar redireccionamiento a la URL de éxito
        self.assertRedirects(response, reverse_lazy("products"))

    def test_invalid_form_does_not_create_product(self):
        """Si el formulario es inválido, no se debe crear el producto"""
        self.client.login(username="testuser", password="password")

        # Datos inválidos (por ejemplo, falta el precio)
        invalid_product_data = {
            "name": "Invalid Product",
            "description": "An invalid product",
            # No se incluye el precio, que es requerido
        }

        # Intentar enviar el formulario con datos inválidos
        response = self.client.post(self.url, data=invalid_product_data)

        # Verificar que no se ha creado ningún producto
        self.assertFalse(Product.objects.filter(name="Invalid Product").exists())

        # Verificar que el formulario fue reenviado y contiene errores
        self.assertEqual(response.status_code, 200)

        # Asegurarse de que el formulario está en el contexto y tiene errores
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("price", form.errors)


class UpdateProductViewTest(TestCase):

    def setUp(self):
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
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
        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            description=self.faker.paragraph(),
        )

        # Crear un usuario y empleado
        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # URL de la vista para actualizar
        self.url = reverse("update_product", kwargs={"id": self.product.id})

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

    def test_view_requires_login(self):
        """La vista requiere que el usuario esté autenticado"""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_view_uses_correct_template(self):
        """La vista utiliza la plantilla correcta"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "update_product.html")

    def test_successful_product_update(self):
        """Actualización exitosa del producto"""
        self.client.login(username="testuser", password="password")

        # Nuevos datos para actualizar el producto
        new_data = {
            "name": "Updated Product",
            "description": "Updated description",
            "price": 75.00,
            "stock": 5,
            "category": self.category.id,  # Debes pasar el ID de la categoría en los formularios
        }

        response = self.client.post(self.url, new_data)

        # Verificar que la actualización se realizó correctamente
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")
        self.assertEqual(self.product.description, "Updated description")
        self.assertEqual(self.product.price, 75.00)
        self.assertEqual(self.product.stock, 5)

        # Verificar la redirección a la página de detalle del producto
        self.assertRedirects(
            response, reverse("detail_product", kwargs={"id": self.product.id})
        )

    def test_invalid_product_id_returns_404(self):
        """Intento de actualizar un producto que no existe debe devolver 404"""
        self.client.login(username="testuser", password="password")

        # Intentar actualizar un producto con un ID que no existe
        invalid_url = reverse("update_product", kwargs={"id": 999})
        response = self.client.get(invalid_url)

        # Verificar que la respuesta es 404
        self.assertEqual(response.status_code, 404)

    def test_invalid_form(self):
        """Formulario inválido debería retornar el formulario con errores"""
        self.client.login(username="testuser", password="password")

        # Datos incorrectos para el formulario (campo 'name' vacío)
        invalid_data = {
            "name": "",
            "description": "Updated description",
            "price": 75.00,
            "stock": 5,
            "category": self.category.id,
        }

        response = self.client.post(self.url, invalid_data)

        # Verificar que la respuesta es 200 OK (se muestra de nuevo el formulario)
        self.assertEqual(response.status_code, 200)

        # Acceder al formulario desde el contexto de la respuesta
        form = response.context["form"]

        # Verificar que el formulario es inválido
        self.assertFalse(form.is_valid())

        # Verificar que el campo 'name' tiene un error
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], ["Este campo es requerido."])


class DeleteProductViewTest(TestCase):

    def setUp(self):
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
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
        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        # Crear un usuario y empleado
        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un producto
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            description=self.faker.paragraph(),
        )

        # URL de la vista para eliminar
        self.url = reverse("delete_product", kwargs={"id": self.product.id})
        self.success_url = reverse("products")

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

    def test_view_requires_login(self):
        """La vista requiere que el usuario esté autenticado"""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_view_uses_correct_template(self):
        """La vista utiliza la plantilla correcta"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete_product.html")

    def test_successful_product_deletion(self):
        """La eliminación del producto funciona correctamente"""
        self.client.login(username="testuser", password="password")

        # Verificar que el producto existe antes de eliminarlo
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())

        # Realizar la solicitud POST para eliminar el producto
        response = self.client.post(self.url)

        # Verificar que el producto ha sido eliminado
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

        # Verificar que la redirección es correcta
        self.assertRedirects(response, reverse("products"))

    def test_invalid_product_id_returns_404(self):
        """Si se intenta eliminar un producto que no existe, devuelve un 404"""
        self.client.login(username="testuser", password="password")

        # Intentar eliminar un producto que no existe (ID no válido)
        invalid_url = reverse("delete_product", kwargs={"id": 999})
        response = self.client.get(invalid_url)

        # Verificar que la respuesta es 404
        self.assertEqual(response.status_code, 404)


class ProductsAPITest(TestCase):

    def setUp(self):
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
        self.document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )
        self.company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=self.document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )
        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        # Crear un usuario y empleado
        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Creación de un cliente API
        self.client = APIClient()

        # URL del endpoint
        self.url = reverse("api_products")

        # Creación de productos para el test
        self.product1 = Product.objects.create(
            name="Product 1",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            description=self.faker.paragraph(),
        )
        self.product2 = Product.objects.create(
            name="Product 2",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            description=self.faker.paragraph(),
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

    def test_authentication_required(self):
        """Verificar que se requiere autenticación para acceder al endpoint"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_products_success(self):
        """Verificar que un usuario autenticado puede obtener la lista de productos"""
        self.client.login(username="testuser", password="password")

        # Realizar la solicitud GET
        response = self.client.get(self.url)

        # Obtener los productos que deberían devolverse
        products = Product.objects.filter(company=self.user.employee.company)
        serializer = ProductsSerializer(products, many=True)

        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que los datos devueltos son correctos
        self.assertEqual(response.data, serializer.data)

    def test_no_products_in_company(self):
        """Verificar que si no hay productos, la respuesta es una lista vacía"""
        # Eliminar los productos de la base de datos
        Product.objects.all().delete()

        self.client.login(username="testuser", password="password")

        # Realizar la solicitud GET
        response = self.client.get(self.url)

        # Verificar que la respuesta es 200 OK y que la lista de productos está vacía
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_products_for_different_company(self):
        """Verificar que un usuario no puede acceder a productos de otra compañía"""
        # Crear un segundo usuario y compañía
        other_company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=self.document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )
        other_user = User.objects.create_user(username="otheruser", password="password")
        Employee.objects.create(user=other_user, company=other_company)

        self.client.login(username="otheruser", password="password")

        # Realizar la solicitud GET
        response = self.client.get(self.url)

        # Verificar que no devuelve los productos de la primera compañía
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class ProductAPITest(TestCase):

    def setUp(self):
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
        self.document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )
        self.company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=self.document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )
        self.category = Category.objects.create(
            name="Test Category",
            company=self.company,
        )

        # Crear un usuario y empleado
        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Creación de un cliente API
        self.client = APIClient()

        # Creación de productos para el test
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.generate_test_image(),
            description=self.faker.paragraph(),
        )

        # URL del endpoint
        self.url = reverse("api_get_product", kwargs={"id": self.product.id})

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

    def test_authentication_required(self):
        """Verificar que se requiere autenticación para acceder al endpoint"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_product_success(self):
        """Verificar que un usuario autenticado puede obtener los detalles de un producto"""
        self.client.login(username="testuser", password="password")

        # Realizar la solicitud GET
        response = self.client.get(self.url)

        # Obtener el producto que debería devolverse
        product = Product.objects.get(id=self.product.id)
        serializer = ProductSerializer(product)

        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que los datos devueltos son correctos
        self.assertEqual(response.data, serializer.data)

    def test_product_not_found(self):
        """Verificar que si el producto no existe, se devuelve 404"""
        self.client.login(username="testuser", password="password")

        # Realizar la solicitud GET con un ID de producto inexistente
        non_existent_url = reverse("api_get_product", kwargs={"id": 9999})
        response = self.client.get(non_existent_url)

        # Verificar que se devuelve 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
