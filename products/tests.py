import io, os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from pathlib import Path
from PIL import Image
from random import randint

from categories.models import Category
from companies.models import Company
from document_types.models import DocumentType
from .models import Product


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


class ProductDetailViewTest(TestCase):
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

    def test_product_detail_view_should_return_200(self):
        Product.objects.create(
            name="Test Product",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.faker.image_url(),
            description=self.faker.paragraph(),
        )

        url = reverse("detail_product", kwargs={"id": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_product_detail_view_should_return_product(self):
        product = Product.objects.create(
            name="Test Product",
            category=self.category,
            company=self.company,
            price=self.faker.random_int(min=100, max=10000),
            stock=self.faker.random_int(min=1, max=100),
            picture=self.faker.image_url(),
            description=self.faker.paragraph(),
        )

        url = reverse("detail_product", kwargs={"id": product.id})
        response = self.client.get(url)

        self.assertEqual(response.context["product"].get("name"), product.name)


class CreateProductViewTest(TestCase):
    def setUp(self) -> None:
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )
        company = Company.objects.create(
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
            company=company,
        )

    def tearDown(self) -> None:
        os.remove(
            Path(__file__).resolve().parent.parent / "static/images/test_image.jpg"
        )

    def generate_test_image(self):
        image = Image.new("RGB", (100, 100), color="red")
        byte_io = io.BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        return SimpleUploadedFile(
            "test_image.jpg", byte_io.read(), content_type="image/jpeg"
        )

    def test_create_product_view_should_contain_product_name(self):
        test_image = self.generate_test_image()

        product = {
            "name": "Test Product",
            "category": self.category.id,
            "price": self.faker.random_int(min=100, max=10000),
            "stock": self.faker.random_int(min=1, max=100),
            "picture": test_image,
            "description": self.faker.paragraph(),
        }

        url = reverse("add_product")

        response = self.client.post(url, data=product)

        self.assertRedirects(response, reverse("products"))


class UpdateProductViewTests(TestCase):
    def setUp(self):
        # Crear una categoría y una empresa para los productos
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
            picture=self.faker.image_url(),
            description=self.faker.paragraph(),
        )
        self.update_url = reverse("update_product", kwargs={"id": self.product.id})

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

    def test_update_product_view_renders_correct_template(self):
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "update_product.html")

    def test_update_product_view_context(self):
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"], self.product)

    def test_update_product_successful(self):
        updated_data = {
            "name": "Producto actualizado",
            "description": "Descripción actualizada",
            "price": 150.00,
            "stock": 20,
            "category": self.category.id,
            "company": self.company.id,
        }

        response = self.client.post(self.update_url, data=updated_data)

        self.product.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("detail_product", kwargs={"id": self.product.id})
        )

        self.assertEqual(self.product.name, "Producto actualizado")
        self.assertEqual(self.product.description, "Descripción actualizada")
        self.assertEqual(self.product.price, 150.00)
        self.assertEqual(self.product.stock, 20)

    def test_update_product_with_invalid_data(self):
        invalid_data = {
            "name": "Producto inválido",
            "description": "Descripción inválida",
            "price": -50.00,
            "stock": 10,
            "category": self.category.id,
            "company": self.company.id,
        }

        response = self.client.post(self.update_url, data=invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "update_product.html")

        self.product.refresh_from_db()
        self.assertNotEqual(self.product.price, -50.00)

    def test_update_product_with_image_upload(self):
        image = self.generate_test_image()

        updated_data = {
            "name": "Producto con imagen",
            "description": "Descripción con imagen",
            "price": 200.00,
            "stock": 15,
            "category": self.category.id,
            "company": self.company.id,
            "picture": image,
        }

        response = self.client.post(self.update_url, data=updated_data)

        # Verificar que la imagen fue guardada y que redirige correctamente
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(self.product.picture)
        self.assertTrue(self.product.picture.name.endswith("test_image.jpg"))


class DeleteProductViewTests(TestCase):
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
            picture=self.faker.image_url(),
            description=self.faker.paragraph(),
        )

        self.delete_url = reverse("delete_product", kwargs={"id": self.product.id})
        self.success_url = reverse("products")

    def test_delete_product_view_renders_correct_template(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete_product.html")

    def test_delete_product_view_context(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"], self.product)

    def test_delete_product_successful(self):
        response = self.client.post(self.delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.success_url)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_delete_non_existent_product(self):
        non_existent_url = reverse("delete_product", kwargs={"id": 9999})

        with self.assertRaises(Product.DoesNotExist):
            self.client.get(non_existent_url)
