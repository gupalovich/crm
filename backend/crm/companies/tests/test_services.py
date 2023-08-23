from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from crm.core.utils import html_to_pdf

from ..services import (
    ProductIntegrationService,
    company_create,
    company_render_business_card,
    document_create,
    product_create_update,
    product_image_create,
    product_images_replace,
    product_translate,
    product_translation_filter_by_keys,
    translate_dict_keys,
    user_create,
)
from .factories import (
    Company,
    CompanyFactory,
    CompanyMember,
    CompanyProductLinkFactory,
    Product,
    ProductFactory,
    ProductImage,
    ProductTranslation,
    ProductTranslationFactory,
    UserFactory,
)

User = get_user_model()


class ServicesTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.company = CompanyFactory()
        # create translations
        self.translation = ProductTranslationFactory(key="brand", value="Бренд")
        self.translation_1 = ProductTranslationFactory(key="model", value="Модель")
        self.translation_other = ProductTranslationFactory(key="test", value="Тест")
        # create product
        self.product = ProductFactory(
            company=self.company,
            data={
                "brand": "BMW",
                "model": "E3",
                "doors": 4,
            },
        )
        # create test data
        self.keys = ["brand", "model"]
        self.product_data_expected_result = {"Бренд": "BMW", "Модель": "E3", "doors": 4}
        self.test_url = "https://test.com/test.json"
        # build test data
        self.user_data = {
            "username": "test1211111",
            "password": "льное поле. Не более 150 с",
            "first_name": "Дмитрий",
            "middle_name": "123123",
            "last_name": "Гупало",
            "email": "mail@gmail.com",
            "phone_number": "8 (978) 787-39-19",
            "role": User.Roles.MANAGER,
            "company": self.company,
        }
        self.company_data = {
            "company_type": self.company.company_type,
            "name": self.company.name,
            "executive_name": self.company.executive_name,
            "executive_position": self.company.executive_position,
            "address": self.company.address,
            "logo_image": self.company.logo_image,
        }
        self.product_data = {
            "company": self.product.company,
            "pid": "12312312",
            "name": self.product.name,
            "price": self.product.price,
            "price_special": self.product.price_special,
            "url": self.product.url,
            "data": self.product.data,
            "data_options": self.product.data_options,
        }
        # request
        self.rf = RequestFactory()
        self.request = self.rf.get("/")
        self.request.user = self.user

    def test_document_create(self):
        pdf_file = html_to_pdf(
            self.request,
            self.company.offer_template,
            {"user": self.user, "company": self.company, "product": self.product},
        )
        document_data = {
            "pdf_file": {"content": pdf_file, "name": "test_file_name.pdf"},
            "name": "test document",
            "product": self.product,
        }
        document = document_create(document_data=document_data)
        # test document
        self.assertEqual(document.name, document_data["name"])
        self.assertEqual(document.product, document_data["product"])

    def test_create_user(self):
        user = user_create(user_data=self.user_data)
        company_member = CompanyMember.objects.filter(user=user, company=self.company).exists()
        self.assertIsInstance(user, User)
        self.assertNotEqual(user.password, self.user_data["password"])
        self.assertTrue(company_member)

    def test_company_create(self):
        company = company_create(user=self.user, company_data=self.company_data)
        self.assertIsInstance(company, Company)
        company_members_count = CompanyMember.objects.count()
        company_member = CompanyMember.objects.get(user=self.user, company=company)
        self.assertEqual(company_members_count, 1)
        self.assertTrue(company_member)

    def test_translations_filter_by_keys(self):
        translations = list(ProductTranslation.objects.filter(key__in=self.keys))
        translations_filtered = list(product_translation_filter_by_keys(keys=self.keys))
        self.assertEqual(translations, translations_filtered)

    def test_translate_dict_keys(self):
        translations = product_translation_filter_by_keys(keys=self.keys)
        data = translate_dict_keys(data=self.product.data, translations=translations)
        self.assertEqual(data, self.product_data_expected_result)

    def test_product_translate(self):
        product = product_translate(product=self.product)
        self.assertEqual(product.data, self.product_data_expected_result)

    def test_product_translate_hard_save(self):
        product = product_translate(product=self.product, hard_save=True)
        product.refresh_from_db()
        self.assertEqual(product.data, self.product_data_expected_result)

    def test_product_image_create(self):
        product_image = product_image_create(product=self.product, url=self.test_url)
        self.assertIsInstance(product_image, ProductImage)
        self.assertEqual(ProductImage.objects.count(), 0)

    def test_product_image_create_hard_save(self):
        product_image = product_image_create(product=self.product, url=self.test_url, hard_save=True)
        self.assertIsInstance(product_image, ProductImage)
        self.assertEqual(ProductImage.objects.count(), 1)

    def test_product_images_replace(self):
        images_1 = ["https://test.com/test.jpg", "https://test.com/test1.jpg", "https://test.com/test2.jpg"]
        images_2 = ["https://test.com/test.jpg"]
        images_3 = ["https://test.com/new_image1.jpg", "https://test.com/new_image2.jpg"]
        test_cases = [  # images, expected_count
            (images_1, 3, "Create 3 images for Product"),
            (images_1, 3, "Repeating duplicate will not yield result"),
            (images_2, 1, "Update existing product images will update-remove unused"),
            (images_3, 2, "Create 2 completely new images will update-remove unused"),
        ]
        for images, expected_count, *optional_message in test_cases:
            product_images = product_images_replace(product=self.product, images=images)
            expected_images_set = set(product_images.values_list("url", flat=True))
            self.assertEqual(product_images.count(), expected_count, optional_message)
            self.assertFalse(expected_images_set - set(images))
            self.assertEqual(ProductImage.objects.count(), expected_count)

    def test_product_create_update(self):
        product = product_create_update(product_data=self.product_data)
        self.assertIsInstance(product, Product)
        self.assertEqual(Product.objects.count(), 2)

    def test_product_create_update_inactive_will_not_update(self):
        product_inactive = ProductFactory(company=self.company, pid="123", is_active=False)
        product = product_create_update(
            product_data={"company": self.company, "pid": "123", "is_active": True}
        )
        product_inactive.refresh_from_db()
        self.assertIsInstance(product, Product)
        self.assertFalse(product_inactive.is_active)

    def test_company_render_business_card(self):
        user = self.user
        business_card = "Я {first_name} {middle_name} {last_name} {phone_number} {email}"
        expected_result = (
            f"Я {user.first_name} {user.middle_name} {user.last_name} {user.phone_number} {user.email}"
        )
        result = company_render_business_card(user=user, bc=business_card)
        self.assertEqual(result, expected_result)


class ProductIntegrationServiceTests(TestCase):
    def setUp(self):
        # create product links
        self.product_link = CompanyProductLinkFactory()
        self.product_link_invalid = CompanyProductLinkFactory(url="https://used.dealer-car.ru/")
        # create product integration service
        self.integration = ProductIntegrationService(self.product_link)
        self.integration_invalid = ProductIntegrationService(self.product_link_invalid)
        # fetch data, fetch only once
        self.valid_fetch = self.integration.fetch_products()

    def test_fetch_products(self):
        self.assertEqual(len(self.integration.raw_products), 2)

    def test_fetch_products_invalid(self):
        self.integration_invalid.fetch_products(max_attempts=1)
        self.integration_invalid.build_products()
        # Test that product link is invalidated
        self.assertFalse(self.product_link_invalid.is_valid)
        self.assertFalse(self.integration_invalid.raw_products)
        self.assertFalse(self.integration_invalid.products)

    def test_build_products(self):
        self.integration.build_products()
        self.assertEqual(len(self.integration.products), 2)
        for product in self.integration.products:
            self.assertEqual(len(product), 9)
            self.assertIn("company", product)
            self.assertIn("pid", product)
            self.assertIn("name", product)
            self.assertIn("price", product)
            self.assertIn("price_special", product)
            self.assertIn("url", product)
            self.assertIn("data", product)
            self.assertIn("data_options", product)
            self.assertIn("images", product)

    def test_flow(self):
        # Test the valid flow
        self.integration.fetch_products()
        self.integration.build_products()
        self.integration.save_products()
        # Test that product link is valid
        self.assertTrue(self.product_link.is_valid)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(ProductImage.objects.count(), 68)
        # Test repeating save will not create duplicated
        self.integration.build_products()
        self.integration.save_products()
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(ProductImage.objects.count(), 68)

    def test_invalid_flow(self):
        self.integration_invalid.fetch_products(max_attempts=1)
        self.integration_invalid.build_products()
        self.integration_invalid.save_products()
        # test products not added
        self.assertEqual(Product.objects.count(), 0)
