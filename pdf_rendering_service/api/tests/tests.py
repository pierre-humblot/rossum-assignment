"""

Testing can be improved and extended in the following ways:
- more content-type testing and request / response validation
- having dramatiq working in the testing environment in order to test the production and format of produced png files:
    - test png obtained from get response,
    - test resolution 1200x1600,
    - test number of pages for multiple page pdfs


"""

import time

from django.test import TestCase
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from api.models import Document

client = Client()



class DocumentTestCase(TestCase):

    def test_document_id(self):
        """Created documents are correctly created and identified"""

        Document.objects.create()
        document = Document.objects.get(id=1)
        self.assertEqual(document.id, 1)
        self.assertEqual(document.status, Document.STATUS_PROCESSING)
        self.assertEqual(document.pdf_file, "")



class RequestUploadTestCase(TestCase):

    def test_upload_pdf(self):
        """Uploading a simple pdf document"""

        with open(settings.TEST_FILES_PATH + "simple_file.pdf", "rb") as f:
            response = client.post("http://localhost:8000/api/documents", {"file": f})
            self.assertEqual(response.status_code, 201)
            self.assertIn("id", response.data)
            self.assertIsInstance(response.data["id"], int)
            response = client.get("http://localhost:8000/api/documents/{}".format(response.data["id"]))
            self.assertEqual(response.status_code, 200)

    def test_upload_multiple_file(self):
        """Uploading a document with multiple pages"""

        with open(settings.TEST_FILES_PATH + "multiple_file.pdf", "rb") as f:
            response = client.post("http://localhost:8000/api/documents", {"file": f})
            self.assertEqual(response.status_code, 201)
            self.assertIn("id", response.data)
            self.assertIsInstance(response.data["id"], int)
            response = client.get("http://localhost:8000/api/documents/{}".format(response.data["id"]))
            self.assertEqual(response.status_code, 200)

    def test_upload_non_pdf_file(self):
        """Uploading a non-pdf document"""

        with open(settings.TEST_FILES_PATH + "jpeg_file.jpeg", "rb") as f:
            response = client.post("http://localhost:8000/api/documents", {"file": f})
            self.assertEqual(response.status_code, 400)

    def test_upload_large_file(self):
        """Uploading a large file > 10 Mb"""

        with open(settings.TEST_FILES_PATH + "large_file.pdf", "rb") as f:
            response = client.post("http://localhost:8000/api/documents", {"file": f})
            self.assertEqual(response.status_code, 400)



class RequestGettingTestCase(TestCase):

    def test_get_non_existing_document(self):
        """Getting non-existing document"""
        
        response = client.get("http://localhost:8000/api/documents/1")
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_document_or_page(self):
        """Getting document with wrong id format"""
        
        response = client.get("http://localhost:8000/api/documents/abc")
        self.assertEqual(response.status_code, 404)
        response = client.get("http://localhost:8000/api/documents/-1")
        self.assertEqual(response.status_code, 404)
        response = client.get("http://localhost:8000/api/documents/-1/pages/1")
        self.assertEqual(response.status_code, 404)

    def test_get_png_output(self):
        """Getting correct png output from simple pdf processing"""
        
        with open(settings.TEST_FILES_PATH + "simple_file.pdf", "rb") as f:
            response = client.post("http://localhost:8000/api/documents", {"file": f})
            self.assertEqual(response.status_code, 201)
            self.assertIn("id", response.data)
            self.assertIsInstance(response.data["id"], int)
            time.sleep(2)
            response = client.get("http://localhost:8000/api/documents/{}".format(response.data["id"]))
            self.assertEqual(response.status_code, 200)
            self.assertIn("status", response.data)
            self.assertEqual(response.data["status"], Document.STATUS_DONE) # fails because dramatiq not working concurrently to the testing environment
            self.assertIn("n_pages", response.data)
            self.assertEqual(response.data["n_pages"], 1)



