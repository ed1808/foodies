from django.db.models import QuerySet
from django.db.utils import IntegrityError
from django.test import TestCase

from .models import DocumentType


class DocumentTypesTest(TestCase):

    def test_create_document_type_returns_a_document_type_instance(self):
        document_type = DocumentType.objects.create(
            name="Tarjeta de identidad", code="TI"
        )

        self.assertIsInstance(document_type, DocumentType)

    def test_create_document_type_without_name_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            DocumentType.objects.create(name=None, code="TI")

    def test_create_document_type_without_code_raises_integrity_error(self):
        with self.assertRaises(IntegrityError):
            DocumentType.objects.create(name="Tarjeta de identidad", code=None)

    def test_get_all_document_types_returns_a_queryset(self):
        tarjeta_de_identidad = DocumentType(name="Tarjeta de identidad", code="TI")
        cedula_de_ciudadania = DocumentType(name="Cedula de ciudadanía", code="CC")
        pasaporte = DocumentType(name="Pasaporte", code="P")

        DocumentType.objects.bulk_create(
            [tarjeta_de_identidad, cedula_de_ciudadania, pasaporte]
        )

        document_types_list = DocumentType.objects.all()

        self.assertIsInstance(document_types_list, QuerySet)

    def test_document_type_str_returns_name(self):
        document_type = DocumentType(name="Tarjeta de identidad", code="TI")
        self.assertEqual(str(document_type), "Tarjeta de identidad")
