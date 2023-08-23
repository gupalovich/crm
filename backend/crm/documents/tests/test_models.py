from django.test import TestCase

from .factories import CompanyFactory, Document, DocumentFactory, PDFBlock, PDFBlockFactory


class PDFBlockTests(TestCase):
    def setUp(self) -> None:
        self.test_name = "Company Type"
        self.company = CompanyFactory()
        self.pdf_block = PDFBlockFactory(company=self.company)
        self.other_pdf_block = PDFBlockFactory()
        self.init_count = PDFBlock.objects.count()
        self.batch_size = 2

    def test_create(self):
        PDFBlockFactory.create_batch(self.batch_size)
        self.assertEqual(PDFBlock.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.pdf_block.name = self.test_name
        self.pdf_block.full_clean()
        self.pdf_block.save()
        self.assertEqual(self.pdf_block.name, self.test_name)

    def test_delete(self):
        self.pdf_block.delete()
        self.assertEqual(PDFBlock.objects.count(), self.init_count - 1)

    def test_delete_cascade(self):
        self.company.delete()
        self.assertEqual(PDFBlock.objects.count(), self.init_count - 1)

    def test_fields(self):
        self.assertTrue(self.pdf_block.company)
        self.assertTrue(self.pdf_block.name)
        self.assertFalse(self.pdf_block.image)
        self.assertTrue(self.pdf_block.text)
        self.assertTrue(self.pdf_block.created_at)
        self.assertTrue(self.pdf_block.updated_at)

    def test_str(self):
        self.assertEqual(f"{self.pdf_block.company.name} - {self.pdf_block.name}", str(self.pdf_block))


class DocumentTests(TestCase):
    def setUp(self) -> None:
        self.test_name = "Document Name"
        self.document = DocumentFactory()
        self.init_count = Document.objects.count()
        self.batch_size = 2

    def test_create(self):
        DocumentFactory.create_batch(self.batch_size)
        self.assertEqual(Document.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.document.name = self.test_name
        self.document.full_clean()
        self.document.save()
        self.assertEqual(self.document.name, self.test_name)

    def test_delete(self):
        self.document.delete()
        self.assertEqual(Document.objects.count(), self.init_count - 1)

    def test_fields(self):
        self.assertTrue(self.document.product)
        self.assertTrue(self.document.name)
        self.assertTrue(self.document.url)
        self.assertTrue(self.document.created_at)
        self.assertTrue(self.document.updated_at)

    def test_str(self):
        self.assertEqual(self.document.name, str(self.document))
