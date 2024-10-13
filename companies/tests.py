from django.db.utils import IntegrityError
from django.test import TestCase

from faker import Faker
from random import randint

from document_types.models import DocumentType
from .models import Company


class CompaniesTest(TestCase):
    def setUp(self) -> None:
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))
        self.document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )

    def test_create_company_returns_a_company_instance(self):
        company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=self.document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        self.assertIsInstance(company, Company)

    def test_create_company_without_name_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                name=None,
                email=self.faker.company_email(),
                phone=self.faker.phone_number(),
                document_number=self.faker.legal_person_nit(),
                document_type=self.document_type,
                address=self.faker.address(),
                city=self.faker.city(),
                country=self.faker.country(),
            )

    def test_company_str_returns_name(self):
        company = Company.objects.create(
            name=self.faker.company(),
            email=self.faker.company_email(),
            phone=self.faker.phone_number(),
            document_number=self.faker.legal_person_nit(),
            document_type=self.document_type,
            address=self.faker.address(),
            city=self.faker.city(),
            country=self.faker.country(),
        )

        company_name = str(company)

        self.assertEqual(company.name, company_name)

    def test_delete_document_type_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                name=self.faker.company(),
                email=self.faker.company_email(),
                phone=self.faker.phone_number(),
                document_number=self.faker.legal_person_nit(),
                document_type=self.document_type,
                address=self.faker.address(),
                city=self.faker.city(),
                country=self.faker.country(),
            )

            self.document_type.delete()
