from django.conf import settings
from django.test import TestCase
from django.urls import reverse
import httpx
import pytest


class TestView(TestCase):

    def test_index(self):
        response = self.client.get(reverse('namespub-index'))
        self.assertEqual(response.status_code, 200)

    def test_farrecords(self):
        response = self.client.get(reverse('namespub-farrecords'))
        self.assertEqual(response.status_code, 200)

    def test_farrecord(self):
        response = self.client.get(reverse('namespub-farrecord'))
        self.assertEqual(response.status_code, 200)

    def test_wrarecords(self):
        response = self.client.get(reverse('namespub-wrarecords'))
        self.assertEqual(response.status_code, 200)

    def test_wrarecord(self):
        response = self.client.get(reverse('namespub-wrarecord'))
        self.assertEqual(response.status_code, 200)

    def test_persons(self):
        response = self.client.get(reverse('namespub-persons'))
        self.assertEqual(response.status_code, 200)

    def test_person(self):
        response = self.client.get(reverse('namespub-person'))
        self.assertEqual(response.status_code, 200)

    def test_farpages(self):
        response = self.client.get(reverse('namespub-farpages'))
        self.assertEqual(response.status_code, 200)

    def test_farpage(self):
        response = self.client.get(reverse('namespub-farpage'))
        self.assertEqual(response.status_code, 200)
