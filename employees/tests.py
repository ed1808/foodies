from django.test import TestCase
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy

from faker import Faker
from random import randint

from companies.models import Company
from document_types.models import DocumentType
from .forms import EmployeeUpdateForm
from .models import Employee

User = get_user_model()


class EmployeeModelTest(TestCase):

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

        # Crear un usuario
        self.user = User.objects.create_user(username="testuser", password="password")

        # Crear un empleado
        self.employee = Employee.objects.create(user=self.user, company=self.company)

    def test_employee_creation(self):
        company_name = str(self.company)

        self.assertEqual(self.employee.user.username, "testuser")
        self.assertEqual(self.employee.company.name, company_name)

    def test_employee_str_method(self):
        """El método __str__ debe devolver el nombre de usuario del User asociado"""
        self.assertEqual(str(self.employee), "testuser")

    def test_employee_delete_cascade_user(self):
        """Eliminar un usuario debe eliminar el empleado correspondiente"""
        self.user.delete()
        with self.assertRaises(Employee.DoesNotExist):
            Employee.objects.get(id=self.employee.id)

    def test_employee_delete_cascade_company(self):
        """Eliminar una compañía debe eliminar el empleado correspondiente"""
        self.company.delete()
        with self.assertRaises(Employee.DoesNotExist):
            Employee.objects.get(id=self.employee.id)


class EmployeeListViewTest(TestCase):

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

        # Crear usuarios y empleados
        self.user = User.objects.create_user(
            username="testuser", password="password", is_active=True
        )
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        self.other_user = User.objects.create_user(
            username="otheruser", password="password", is_active=True
        )
        self.other_employee = Employee.objects.create(
            user=self.other_user, company=other_company
        )

        # Crear un usuario inactivo en la misma compañía
        self.inactive_user = User.objects.create_user(
            username="inactiveuser", password="password", is_active=False
        )
        self.inactive_employee = Employee.objects.create(
            user=self.inactive_user, company=self.company
        )

        # URL de la vista
        self.url = reverse("employees")

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
        self.assertTemplateUsed(response, "employees.html")

    def test_view_returns_only_active_employees_from_same_company(self):
        """La vista devuelve solo los empleados activos de la misma compañía que el usuario autenticado"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        employees = response.context["employees"]

        # Asegurarse de que solo se devuelven los empleados activos de la compañía del usuario autenticado
        self.assertIn(self.user, employees)
        self.assertNotIn(self.other_user, employees)  # De otra compañía
        self.assertNotIn(self.inactive_user, employees)  # Inactivo de la misma compañía

    def test_context_object_name(self):
        """El contexto debe contener 'employees' como nombre del objeto"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("employees", response.context)


class EmployeeUpdateViewTest(TestCase):

    def setUp(self):
        # Crear una compañía
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

        # Crear un usuario y empleado
        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un segundo usuario para probar la actualización
        self.other_user = User.objects.create_user(
            username="otheruser", first_name="Other", password="password"
        )
        self.other_employee = Employee.objects.create(
            user=self.other_user, company=self.company
        )

        # URL de la vista
        self.url = reverse("update_employee", kwargs={"id": self.other_user.id})

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
        self.assertTemplateUsed(response, "update_employee.html")

    def test_view_returns_correct_object(self):
        """La vista devuelve el objeto correcto (User) basado en el ID proporcionado"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        employee = response.context["employee"]
        self.assertEqual(employee, self.other_user)

    def test_view_uses_correct_form(self):
        """La vista utiliza el formulario correcto (EmployeeUpdateForm)"""
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], EmployeeUpdateForm)

    def test_view_success_url(self):
        """Tras la actualización exitosa, redirige a la URL correcta"""
        self.client.login(username="testuser", password="password")

        # Realizar una actualización usando el formulario
        response = self.client.post(
            self.url,
            {
                "first_name": "Updated",
            },
        )
        updated_user = User.objects.get(id=self.other_user.id)

        # Verificar que el usuario fue actualizado
        self.assertEqual(updated_user.first_name, "Updated")

        # Verificar que redirige a la URL correcta tras la actualización
        self.assertRedirects(
            response, reverse_lazy("detail_employee", kwargs={"id": updated_user.id})
        )


class EmployeeDetailViewTest(TestCase):
    def setUp(self):
        # Crear una compañía
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

        # Crear un usuario y empleado
        self.user = User.objects.create_user(
            username="testuser",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password="password",
        )
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un segundo usuario para probar la actualización
        self.other_user = User.objects.create_user(
            username="otheruser", first_name="Other", password="password"
        )
        self.other_employee = Employee.objects.create(
            user=self.other_user, company=self.company
        )

        # URL de la vista
        self.url = reverse("detail_employee", kwargs={"id": self.other_user.id})

    def test_redirect_if_not_logged_in(self):
        # Verifica si un usuario no autenticado es redirigido al intentar acceder a la vista
        response = self.client.get(
            reverse("detail_employee", kwargs={"id": self.user.id})
        )
        self.assertRedirects(
            response, f"/employees/login/?next=/employees/{self.user.id}"
        )

    def test_view_url_exists_at_desired_location(self):
        # Verifica si la URL de la vista está disponible para un usuario autenticado
        self.client.login(username="testuser", password="password")
        response = self.client.get(f"/employees/{self.user.id}")
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        # Verifica si la vista está utilizando el template correcto
        self.client.login(username="testuser", password="password")
        response = self.client.get(
            reverse("detail_employee", kwargs={"id": self.user.id})
        )
        self.assertTemplateUsed(response, "detail_employee.html")

    def test_view_returns_correct_context_data(self):
        # Verifica si los datos correctos son devueltos en el contexto
        self.client.login(username="testuser", password="password")
        response = self.client.get(
            reverse("detail_employee", kwargs={"id": self.user.id})
        )

        # Verifica si el contexto contiene el usuario con los campos deseados
        self.assertEqual(response.context["employee"].id, self.user.id)
        self.assertEqual(response.context["employee"].first_name, "John")
        self.assertEqual(response.context["employee"].last_name, "Doe")
        self.assertEqual(response.context["employee"].email, "john.doe@example.com")

    def test_view_returns_404_for_nonexistent_user(self):
        # Verifica si la vista devuelve un error 404 cuando el usuario no existe
        self.client.login(username="testuser", password="password")
        response = self.client.get(
            reverse("detail_employee", kwargs={"id": 9999})
        )  # ID no existente
        self.assertEqual(response.status_code, 404)


class EmployeeLoginViewTest(TestCase):
    def setUp(self):
        # Crear una compañía
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

        # Crear un usuario y empleado
        self.user = User.objects.create_user(username="testuser", password="password")
        self.employee = Employee.objects.create(user=self.user, company=self.company)

        # Crear un segundo usuario para probar la actualización
        self.other_user = User.objects.create_user(
            username="otheruser", first_name="Other", password="password"
        )
        self.other_employee = Employee.objects.create(
            user=self.other_user, company=self.company
        )

    def test_login_view_url_exists_at_desired_location(self):
        # Verifica si la URL del login está disponible
        response = self.client.get("/employees/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_view_uses_correct_template(self):
        # Verifica si la vista utiliza el template correcto
        response = self.client.get(reverse("login"))
        self.assertTemplateUsed(response, "login.html")

    def test_login_view_uses_custom_login_form(self):
        # Verifica si la vista está utilizando el formulario correcto (LoginForm)
        response = self.client.get(reverse("login"))
        self.assertIsInstance(response.context["form"], AuthenticationForm)

    def test_login_with_valid_credentials(self):
        # Verifica si un usuario puede iniciar sesión con credenciales correctas
        login_data = {"username": "testuser", "password": "password"}
        response = self.client.post(reverse("login"), login_data)
        self.assertRedirects(response, reverse("orders"))

    def test_redirect_if_already_logged_in(self):
        # Verifica si un usuario autenticado es redirigido cuando intenta acceder a la página de login
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("orders"))
