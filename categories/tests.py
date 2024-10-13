from django.db.utils import IntegrityError
from django.test import TestCase
from random import randint

from faker import Faker

from companies.models import Company
from document_types.models import DocumentType
from .models import Category


class CategoryTest(TestCase):
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

    def test_create_category_returns_a_category_instance(self):
        category = Category.objects.create(
            name="Testing",
            company=self.company,
        )

        self.assertIsInstance(category, Category)

    def test_create_category_without_name_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name=None,
                company=self.company,
            )

    def test_delete_company_deletes_category(self):
        category = Category.objects.create(
            name="Testing",
            company=self.company,
        )

        category.delete()

        self.assertEqual(Category.objects.count(), 0)

    def test_category_str_returns_name(self):
        category = Category.objects.create(
            name="Testing",
            company=self.company,
        )

        category_name = str(category)

        self.assertEqual(category.name, category_name)
