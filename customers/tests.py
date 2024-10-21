from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from faker import Faker
from random import randint
from rest_framework.test import APIClient
from rest_framework import status

from companies.models import Company
from document_types.models import DocumentType
from employees.models import Employee

from .models import Customer
from .serializers import CustomersSerializer


class CustomerModelTest(TestCase):
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

        # Crear una instancia de Customer
        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="1234567890",
            address="123 Main Street",
            neighborhood="Centro",
        )
        # Relacionar el cliente con las compañías
        self.customer.companies.add(self.company1, self.company2)

    def test_customer_creation(self):
        """Prueba que se pueda crear un cliente correctamente"""
        self.assertEqual(self.customer.name, "John Doe")
        self.assertEqual(self.customer.phone_number, "1234567890")
        self.assertEqual(self.customer.address, "123 Main Street")
        self.assertEqual(self.customer.neighborhood, "Centro")

    def test_customer_str(self):
        """Prueba que el método __str__ devuelva el nombre del cliente"""
        self.assertEqual(str(self.customer), "John Doe")

    def test_customer_companies_relation(self):
        """Prueba la relación ManyToMany entre Customer y Company"""
        self.assertEqual(self.customer.companies.count(), 2)
        self.assertIn(self.company1, self.customer.companies.all())
        self.assertIn(self.company2, self.customer.companies.all())

    def test_customer_verbose_name(self):
        """Prueba el verbose_name del modelo"""
        self.assertEqual(Customer._meta.verbose_name, "Cliente")
        self.assertEqual(Customer._meta.verbose_name_plural, "Clientes")

    def test_customer_max_length(self):
        """Prueba los atributos max_length de los campos"""
        name_max_length = Customer._meta.get_field("name").max_length
        phone_number_max_length = Customer._meta.get_field("phone_number").max_length
        address_max_length = Customer._meta.get_field("address").max_length
        neighborhood_max_length = Customer._meta.get_field("neighborhood").max_length

        self.assertEqual(name_max_length, 255)
        self.assertEqual(phone_number_max_length, 30)
        self.assertEqual(address_max_length, 255)
        self.assertEqual(neighborhood_max_length, 255)


class CustomerCreateViewTest(TestCase):
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

        # Autenticar al usuario
        self.client.login(username="testuser", password="password")

        # URL de la vista
        self.url = reverse("add_customer")

    def test_view_uses_correct_template(self):
        """Prueba que la vista use el template correcto"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_customer.html")

    def test_redirect_if_not_logged_in(self):
        """Prueba que un usuario no autenticado sea redirigido al login"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_form_valid_creates_customer(self):
        """Prueba que el formulario válido cree un nuevo cliente y lo asocie a la compañía del usuario"""
        data = {
            "name": "John Doe",
            "phone_number": "1234567890",
            "address": "123 Main Street",
            "neighborhood": "Centro",
        }
        response = self.client.post(self.url, data)

        # Verifica que se creó el cliente
        self.assertEqual(Customer.objects.count(), 1)
        new_customer = Customer.objects.first()
        self.assertEqual(new_customer.name, "John Doe")
        self.assertEqual(new_customer.phone_number, "1234567890")
        self.assertEqual(new_customer.address, "123 Main Street")
        self.assertEqual(new_customer.neighborhood, "Centro")

        # Verifica que la compañía del usuario esté asociada al cliente
        self.assertIn(self.company, new_customer.companies.all())

    def test_invalid_form_does_not_create_customer(self):
        """Prueba que un formulario inválido no cree un cliente"""
        data = {
            "name": "",
            "phone_number": "1234567890",
            "address": "123 Main Street",
            "neighborhood": "Centro",
        }
        response = self.client.post(self.url, data)

        # Verifica que no se haya creado ningún cliente
        self.assertEqual(Customer.objects.count(), 0)

        # Asegúrate de que el formulario no sea válido y que el campo 'name' tenga un error
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertFormError(form, "name", "Este campo es requerido.")


class CustomersListViewTest(TestCase):
    def setUp(self):
        # Configurar Faker para generar datos ficticios
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))

        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )

        # Crear dos compañías
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

        # Crear dos usuarios con empleados asociados a diferentes compañías
        self.user1 = User.objects.create_user(username="user1", password="password")
        self.employee1 = Employee.objects.create(user=self.user1, company=self.company1)

        self.user2 = User.objects.create_user(username="user2", password="password")
        self.employee2 = Employee.objects.create(user=self.user2, company=self.company2)

        # Crear clientes asociados a cada compañía
        self.customer1 = Customer.objects.create(
            name="John Doe",
            phone_number="1234567890",
            address="123 Main St",
            neighborhood="Centro",
        )
        self.customer1.companies.add(self.company1)

        self.customer2 = Customer.objects.create(
            name="Jane Smith",
            phone_number="0987654321",
            address="456 Other St",
            neighborhood="Sur",
        )
        self.customer2.companies.add(self.company2)

        # Autenticar al usuario 1
        self.client.login(username="user1", password="password")

        # URL de la vista
        self.url = reverse("customers")

    def test_view_uses_correct_template(self):
        """Prueba que la vista use el template correcto"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customers.html")

    def test_redirect_if_not_logged_in(self):
        """Prueba que un usuario no autenticado sea redirigido al login"""
        self.client.logout()  # Asegúrate de que el usuario no esté autenticado
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_view_shows_customers_for_user_company(self):
        """Prueba que la vista muestre solo los clientes asociados a la compañía del usuario autenticado"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        customers = response.context["customers"]

        # Verifica que solo se muestra el cliente de la compañía del usuario autenticado
        self.assertIn(self.customer1, customers)
        self.assertNotIn(self.customer2, customers)

    def test_view_shows_no_customers_for_other_company(self):
        """Prueba que la vista no muestre clientes de otras compañías"""
        self.client.login(username="user2", password="password")  # Cambia al usuario 2
        response = self.client.get(self.url)
        customers = response.context["customers"]

        # Verifica que el cliente de la compañía 2 es visible y el de la compañía 1 no lo es
        self.assertIn(self.customer2, customers)
        self.assertNotIn(self.customer1, customers)


class CustomerDetailViewTest(TestCase):
    def setUp(self):
        # Configurar Faker para generar datos ficticios
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

        # Crear un usuario con empleado asociado a la compañía
        self.user = User.objects.create_user(username="user1", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un cliente asociado a la compañía
        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="1234567890",
            address="123 Main St",
            neighborhood="Centro",
        )
        self.customer.companies.add(self.company)

        # Autenticar al usuario
        self.client.login(username="user1", password="password")

        # URL de la vista de detalle del cliente
        self.url = reverse("detail_customer", kwargs={"id": self.customer.id})

    def test_view_uses_correct_template(self):
        """Prueba que la vista use el template correcto"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "detail_customer.html")

    def test_redirect_if_not_logged_in(self):
        """Prueba que un usuario no autenticado sea redirigido al login"""
        self.client.logout()  # Asegúrate de que el usuario no esté autenticado
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_view_displays_correct_customer(self):
        """Prueba que la vista muestre el cliente correcto"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        customer = response.context["customer"]
        self.assertEqual(customer.id, self.customer.id)
        self.assertEqual(customer.name, self.customer.name)

    def test_view_returns_404_if_customer_not_found(self):
        """Prueba que la vista devuelva 404 si el cliente no existe"""
        invalid_url = reverse("detail_customer", kwargs={"id": 9999})  # ID inexistente
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


class CustomerDeleteViewTest(TestCase):
    def setUp(self):
        # Configurar Faker para generar datos ficticios
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

        # Crear un usuario con empleado asociado a la compañía
        self.user = User.objects.create_user(username="user1", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un cliente asociado a la compañía
        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="1234567890",
            address="123 Main St",
            neighborhood="Centro",
        )
        self.customer.companies.add(self.company)

        # Autenticar al usuario
        self.client.login(username="user1", password="password")

        # URL de la vista de eliminación del cliente
        self.url = reverse("delete_customer", kwargs={"id": self.customer.id})

    def test_view_uses_correct_template(self):
        """Prueba que la vista use el template correcto"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete_customer.html")

    def test_redirect_if_not_logged_in(self):
        """Prueba que un usuario no autenticado sea redirigido al login"""
        self.client.logout()  # Asegúrate de que el usuario no esté autenticado
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_customer_deletion(self):
        """Prueba que el cliente sea eliminado correctamente"""
        response = self.client.post(self.url)

        # Verifica que el cliente ha sido eliminado
        self.assertEqual(Customer.objects.count(), 0)
        self.assertRedirects(response, reverse("customers"))  # Verifica la redirección

    def test_view_returns_404_if_customer_not_found(self):
        """Prueba que la vista devuelva 404 si el cliente no existe"""
        invalid_url = reverse("delete_customer", kwargs={"id": 9999})  # ID inexistente
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


class CustomerUpdateViewTest(TestCase):
    def setUp(self):
        # Configurar Faker para generar datos ficticios
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

        # Crear un usuario con empleado asociado a la compañía
        self.user = User.objects.create_user(username="user1", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un cliente asociado a la compañía
        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="1234567890",
            address="123 Main St",
            neighborhood="Centro",
        )
        self.customer.companies.add(self.company)

        # Autenticar al usuario
        self.client.login(username="user1", password="password")

        # URL de la vista de actualización del cliente
        self.url = reverse("update_customer", kwargs={"id": self.customer.id})

    def test_view_uses_correct_template(self):
        """Prueba que la vista use el template correcto"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "update_customer.html")

    def test_redirect_if_not_logged_in(self):
        """Prueba que un usuario no autenticado sea redirigido al login"""
        self.client.logout()  # Asegúrate de que el usuario no esté autenticado
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/employees/login/?next={self.url}")

    def test_view_displays_correct_customer(self):
        """Prueba que la vista muestre el cliente correcto para editar"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        customer = response.context["customer"]
        self.assertEqual(customer.id, self.customer.id)
        self.assertEqual(customer.name, self.customer.name)

    def test_customer_update(self):
        """Prueba que el cliente sea actualizado correctamente"""
        updated_data = {
            "name": "Jane Doe",
            "phone_number": "9876543210",
            "address": "456 Another St",
            "neighborhood": "Norte",
        }
        response = self.client.post(self.url, updated_data)

        # Verificar que el cliente se ha actualizado
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Jane Doe")
        self.assertEqual(self.customer.phone_number, "9876543210")
        self.assertEqual(self.customer.address, "456 Another St")
        self.assertEqual(self.customer.neighborhood, "Norte")

        # Verificar la redirección al detalle del cliente actualizado
        self.assertRedirects(
            response, reverse("detail_customer", kwargs={"id": self.customer.id})
        )

    def test_invalid_form_does_not_update_customer(self):
        """Prueba que un formulario inválido no actualice el cliente"""
        invalid_data = {
            "name": "",  # Nombre requerido
            "phone_number": "1234567890",
            "address": "123 Main St",
            "neighborhood": "Centro",
        }
        response = self.client.post(self.url, invalid_data)

        # El cliente no debe actualizarse
        self.customer.refresh_from_db()
        self.assertNotEqual(self.customer.name, "")

        # Verificar que el formulario contiene el error esperado
        form = response.context["form"]
        self.assertFormError(form, "name", "Este campo es requerido.")

    def test_view_returns_404_if_customer_not_found(self):
        """Prueba que la vista devuelva 404 si el cliente no existe"""
        invalid_url = reverse("update_customer", kwargs={"id": 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


class CustomersAPITest(TestCase):

    def setUp(self):
        # Configurar Faker para generar datos ficticios
        self.faker = Faker("es_CO")
        self.faker.seed_instance(randint(0, 9999))

        document_type = DocumentType.objects.create(
            name="Número de Identificación Tributaria", code="NIT"
        )

        # Crear una compañía
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

        # Creación del usuario y empleado para la compañía 1
        self.user1 = User.objects.create_user(username="testuser1", password="password")
        self.employee1 = Employee.objects.create(user=self.user1, company=self.company1)

        # Creación de otro usuario y empleado para la compañía 2
        self.user2 = User.objects.create_user(username="testuser2", password="password")
        self.employee2 = Employee.objects.create(user=self.user2, company=self.company2)

        # Creación del cliente API
        self.client = APIClient()

        # URL del endpoint
        self.url = reverse("api_customers")

    def test_authentication_required(self):
        """Verificar que se requiere autenticación para acceder al endpoint"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_customers_success(self):
        """Verificar que un usuario autenticado puede obtener la lista de clientes"""
        # Creación de clientes
        customer1 = Customer.objects.create(name="Customer 1")
        customer2 = Customer.objects.create(name="Customer 2")

        customer1.companies.add(self.company1)
        customer2.companies.add(self.company2)

        self.client.login(username="testuser1", password="password")

        # Realizar la solicitud GET
        response = self.client.get(self.url)

        # Obtener los clientes que deberían devolverse
        customers = Customer.objects.filter(companies=self.company1)
        serializer = CustomersSerializer(customers, many=True)

        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que los datos devueltos son correctos
        self.assertEqual(response.data, serializer.data)

    def test_get_no_customers(self):
        """Verificar que si no hay clientes, la respuesta sea una lista vacía"""
        self.client.login(username="testuser1", password="password")

        # Realizar la solicitud GET
        response = self.client.get(self.url)

        # Verificar que la respuesta es 200 OK pero sin clientes
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # Debe devolver una lista vacía

    def test_user_cannot_see_other_company_customers(self):
        """Verificar que un usuario de otra empresa no pueda ver clientes de una empresa diferente"""
        customer1 = Customer.objects.create(name="Customer 1")
        customer1.companies.add(self.company1)

        # Iniciar sesión como usuario de la segunda compañía
        self.client.login(username="testuser2", password="password")

        # Realizar la solicitud GET
        response = self.client.get(self.url)

        # Obtener los clientes que deberían devolverse (de la compañía 2)
        customers = Customer.objects.filter(companies=self.company2)
        serializer = CustomersSerializer(customers, many=True)

        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que solo los clientes de la compañía 2 se devuelvan
        self.assertEqual(response.data, serializer.data)

        # Verificar que el cliente de la compañía 1 no esté en la lista
        customer_ids = [customer["id"] for customer in response.data]
        self.assertNotIn(customer1.id, customer_ids)
