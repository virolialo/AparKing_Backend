from django.test import TestCase
from .models import Report
from .enums import Status
from .serializers import ReportSerializer
from apps.authentication.models import CustomUser
from apps.authentication.enums import Gender
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from .views import user_reports, user_report_create
from datetime import date

class ReportSerializerTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="viryi", email='testuser@example.com', password='12345', dni='12345678A', birth_date='2000-01-01', gender=Gender.FEMALE, phone='+34123456789')
        self.report_data = {
            'title': 'Test Report',
            'category': 'bug',
            'description': 'This is a test report.',
            'user': self.user
        }
        self.serializer_data = {
            'title': 'Another Test Report',
            'category': 'otro',
            'description': 'This is another test report.',
            'user': self.user.id
        }
        self.report = Report.objects.create(**self.report_data)
        self.serializer = ReportSerializer(instance=self.report)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['title', 'category', 'description', 'user', 'created_at', 'status']))

    def test_description_field(self):
        # Test for empty description
        self.serializer_data['description'] = ''
        serializer = ReportSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())

        # Test for description length > 500
        self.serializer_data['description'] = 'a' * 501
        serializer = ReportSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())

    def test_category_field(self):
        # Test for invalid category
        self.serializer_data['category'] = 'invalid'
        serializer = ReportSerializer(data=self.serializer_data)
        self.assertFalse(serializer.is_valid())

    def test_create_report(self):
        serializer = ReportSerializer(data=self.serializer_data)
        if serializer.is_valid():
            report = serializer.save()
            self.assertEqual(report.title, self.serializer_data['title'])
            self.assertEqual(report.description, self.serializer_data['description'])
            self.assertEqual(report.category, self.serializer_data['category'])
            self.assertEqual(report.user, self.user)
        else:
            self.fail('Serializer data was not valid.')

class ReportModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="viryi", email='testuser@example.com', password='12345', dni='12345678A', birth_date='2000-01-01', gender=Gender.FEMALE, phone='+34123456789')
        self.report_data = {
            'title': 'Test Report',
            'category': 'bug',
            'description': 'This is a test report.',
            'user': self.user
        }

    def test_create_report(self):
        report = Report.objects.create(**self.report_data)
        self.assertIsNotNone(report.id)
        self.assertEqual(report.title, 'Test Report')
        self.assertEqual(report.category, 'bug')
        self.assertEqual(report.description, 'This is a test report.')
        self.assertEqual(report.user, self.user)

    def test_report_without_title(self):
        self.report_data['title'] = ''
        with self.assertRaises(ValidationError):
            Report.objects.create(**self.report_data).full_clean()

    def test_report_without_category(self):
        self.report_data['category'] = ''
        with self.assertRaises(ValidationError):
            Report.objects.create(**self.report_data).full_clean()

    def test_report_default_status(self):
        report = Report.objects.create(**self.report_data)
        self.assertEqual(report.status, Status.PENDIENTE)

    def test_report_to_json(self):
        report = Report.objects.create(**self.report_data)
        expected_json = {
            'id': report.id,
            'title': 'Test Report',
            'category': 'bug',
            'description': 'This is a test report.',
            'status': Status.PENDIENTE,
            'created_at': str(report.created_at),
        }
        self.assertEqual(report.to_json(), expected_json)

class ReportViewsTestCase(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            birth_date=date(1990, 1, 1),
        )

        self.report_data = {
            'title': 'Test Report',
            'category': 'bug',
            'description': 'This is a test report.',
            'status': Status.PENDIENTE,
            'created_at': datetime.now(),
            'user': self.user.id
        }

        self.client.force_authenticate(user=self.user)
        self.client.login(username='testuser', password='testpass')

    def test_user_reports_no_reports(self):
        response = self.client.get(reverse(user_reports))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_report_create_valid(self):
        response = self.client.post(reverse(user_report_create), self.report_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserReportsTest(TestCase):
    def test_access_without_authentication(self):
        response = self.client.get(reverse(user_reports))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserReportCreateTest(TestCase):
    def test_access_without_authentication(self):
        response = self.client.post(reverse(user_report_create), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
