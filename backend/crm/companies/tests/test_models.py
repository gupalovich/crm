from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from crm.users.tests.factories import SuperUserFactory, User

from .factories import (
    Company,
    CompanyFactory,
    CompanyMember,
    CompanyMemberFactory,
    CompanyProductLink,
    CompanyProductLinkFactory,
    CompanyType,
    CompanyTypeFactory,
    Customer,
    CustomerFactory,
    Deal,
    DealFactory,
    Product,
    ProductFactory,
    ProductImage,
    ProductImageFactory,
    ProductTranslation,
    ProductTranslationFactory,
    fake,
)


class CompanyTypeTests(TestCase):
    def setUp(self):
        self.test_name = "Company Type"
        self.company_type = CompanyTypeFactory(name=self.test_name)
        self.init_count = CompanyType.objects.count()
        self.batch_size = 2

    def test_create(self):
        CompanyTypeFactory.create_batch(self.batch_size)
        self.assertEqual(CompanyType.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.company_type.title = self.test_name
        self.company_type.full_clean()
        self.company_type.save()
        self.assertEqual(self.company_type.title, self.test_name)

    def test_delete(self):
        self.company_type.delete()
        self.assertEqual(CompanyType.objects.count(), 0)

    def test_fields(self):
        self.assertEqual(self.company_type.name, self.test_name)
        self.assertTrue(self.company_type.created_at)
        self.assertTrue(self.company_type.updated_at)

    def test_str(self):
        self.assertEqual(self.company_type.name, str(self.company_type))


class CompanyTests(TestCase):
    def setUp(self):
        self.test_name = "Company Name"
        self.company = CompanyFactory(name=self.test_name)
        self.init_count = Company.objects.count()
        self.batch_size = 2

    def test_create(self):
        CompanyFactory.create_batch(self.batch_size)
        self.assertEqual(Company.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.company.name = self.test_name
        self.company.full_clean()
        self.company.save()
        self.assertEqual(self.company.name, self.test_name)

    def test_delete(self):
        self.company.delete()
        self.assertEqual(Company.objects.count(), 0)

    def test_fields(self):
        company_type = CompanyTypeFactory()
        company = CompanyFactory(company_type=company_type, name=self.test_name)
        company_2 = CompanyFactory(name=self.test_name)
        # test fields
        self.assertEqual(company.company_type, company_type)
        self.assertTrue(company.members)
        self.assertEqual(company.name, self.test_name)
        self.assertEqual(company.name, company_2.name)
        self.assertTrue(company.executive_name)
        self.assertTrue(company.executive_position)
        self.assertTrue(company.address)
        self.assertTrue(company.logo_image)
        self.assertTrue(company.signature_image)
        self.assertTrue(company.created_at)
        self.assertTrue(company.updated_at)

    def test_str(self):
        company = CompanyFactory()
        self.assertEqual(company.name, str(company))

    def test_company_type_set_null(self):
        self.company.company_type.delete()
        self.company.refresh_from_db()
        self.assertFalse(self.company.company_type)


class CompanyMemberTests(TestCase):
    def setUp(self):
        self.company_member = CompanyMemberFactory()
        self.init_count = CompanyMember.objects.count()
        self.batch_size = 2

    def test_create(self):
        CompanyMemberFactory.create_batch(self.batch_size)
        self.assertEqual(CompanyMember.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        new_company = CompanyFactory()
        self.company_member.company = new_company
        self.company_member.full_clean()
        self.company_member.save()
        self.assertEqual(self.company_member.company, new_company)

    def test_delete(self):
        self.company_member.delete()
        self.assertEqual(CompanyMember.objects.count(), 0)

    def test_fields(self):
        self.assertTrue(self.company_member.company)
        self.assertTrue(self.company_member.user)
        self.assertTrue(self.company_member.created_at)
        self.assertTrue(self.company_member.updated_at)

    def test_unique_together_user_company(self):
        with self.assertRaises(IntegrityError):
            CompanyMemberFactory(user=self.company_member.user, company=self.company_member.company)

    def test_str(self):
        self.assertEqual(
            f"{self.company_member.user} - {self.company_member.company}", str(self.company_member)
        )


class CustomerTests(TestCase):
    def setUp(self):
        self.batch_size = 2
        self.test_name = "Иван"
        self.test_name = "Иван"
        self.customer = CustomerFactory()
        self.init_client_count = Customer.objects.count()

    def test_create(self):
        CustomerFactory.create_batch(self.batch_size)
        self.assertEqual(Customer.objects.count(), self.batch_size + self.init_client_count)

    def test_update(self):
        self.customer.first_name = self.test_name
        self.customer.full_clean()
        self.customer.save()
        self.assertEqual(self.customer.first_name, self.test_name)

    def test_delete(self):
        self.customer.delete()
        self.assertEqual(Customer.objects.count(), 0)

    def test_fields(self):
        self.assertTrue(self.customer.company)
        self.assertTrue(self.customer.first_name)
        self.assertTrue(self.customer.middle_name)
        self.assertTrue(self.customer.last_name)
        self.assertTrue(self.customer.email)
        self.assertTrue(self.customer.phone_number)
        self.assertTrue(self.customer.created_at)
        self.assertTrue(self.customer.updated_at)

    def test_phone_number_required(self):
        with self.assertRaises(ValidationError):
            self.customer.phone_number = ""
            self.customer.full_clean()
            self.customer.save()

    def test_email_not_required(self):
        self.customer.email = ""
        self.customer.full_clean()
        self.customer.save()

    def test_str(self):
        self.assertEqual(f"{self.customer.first_name} {self.customer.last_name}", str(self.customer))


class ProductTests(TestCase):
    def setUp(self):
        self.test_name = "Product Name"
        self.company = CompanyFactory()
        self.product = ProductFactory(name=self.test_name, company=self.company)
        self.init_count = Product.objects.count()
        self.batch_size = 2

    def test_create(self):
        ProductFactory.create_batch(self.batch_size, company=self.company)
        self.assertEqual(Product.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.product.name = self.test_name
        self.product.full_clean()
        self.product.save()
        self.assertEqual(self.product.name, self.test_name)

    def test_delete(self):
        self.product.delete()
        self.assertEqual(Product.objects.count(), 0)

    def test_fields(self):
        self.assertEqual(self.product.company, self.company)
        self.assertEqual(self.product.name, self.test_name)
        self.assertTrue(self.product.created_at)
        self.assertTrue(self.product.updated_at)

    def test_str(self):
        self.assertEqual(f"{self.product.company.name} - {self.product.name}", str(self.product))


class ProductImageTests(TestCase):
    def setUp(self):
        self.test_url = "https://www.example.com"
        self.product = ProductFactory()
        self.product_image = ProductImageFactory(product=self.product)
        self.init_count = ProductImage.objects.count()
        self.batch_size = 2

    def test_create(self):
        ProductImageFactory.create_batch(self.batch_size, product=self.product)
        self.assertEqual(ProductImage.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.product_image.url = self.test_url
        self.product_image.full_clean()
        self.product_image.save()
        self.assertEqual(self.product_image.url, self.test_url)

    def test_delete(self):
        self.product_image.delete()
        self.assertEqual(ProductImage.objects.count(), 0)

    def test_fields(self):
        self.assertEqual(self.product_image.product, self.product)
        self.assertTrue(self.product_image.url)
        self.assertTrue(self.product_image.created_at)
        self.assertTrue(self.product_image.updated_at)

    def test_str(self):
        self.assertEqual(f"{self.product_image.url}", str(self.product_image))


class ProductTranslationTests(TestCase):
    def setUp(self):
        self.test_value = "Бренд"
        self.translation = ProductTranslationFactory()
        self.init_count = ProductTranslation.objects.count()
        self.batch_size = 2

    def test_create(self):
        ProductTranslationFactory.create_batch(self.batch_size)
        self.assertEqual(ProductTranslation.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.translation.value = self.test_value
        self.translation.full_clean()
        self.translation.save()
        self.assertEqual(self.translation.value, self.test_value)

    def test_delete(self):
        self.translation.delete()
        self.assertEqual(ProductTranslation.objects.count(), 0)

    def test_fields(self):
        self.assertTrue(self.translation.key)
        self.assertTrue(self.translation.value)
        self.assertTrue(self.translation.created_at)
        self.assertTrue(self.translation.updated_at)

    def test_str(self):
        self.assertEqual(f"{self.translation.key} - {self.translation.value}", str(self.translation))


class CompanyProductLinkTests(TestCase):
    def setUp(self):
        self.test_name = "Company Link Name"
        self.company_link = CompanyProductLinkFactory(name=self.test_name)
        self.init_count = CompanyProductLink.objects.count()
        self.batch_size = 2

    def test_create(self):
        CompanyProductLinkFactory.create_batch(self.batch_size)
        self.assertEqual(CompanyProductLink.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.company_link.name = self.test_name
        self.company_link.full_clean()
        self.company_link.save()
        self.assertEqual(self.company_link.name, self.test_name)

    def test_delete(self):
        self.company_link.delete()
        self.assertEqual(CompanyProductLink.objects.count(), 0)

    def test_fields(self):
        self.assertTrue(self.company_link.company)
        self.assertTrue(self.company_link.name)
        self.assertTrue(self.company_link.url)
        self.assertTrue(self.company_link.created_at)
        self.assertTrue(self.company_link.updated_at)

    def test_unique_together_company_url(self):
        with self.assertRaises(IntegrityError):
            CompanyProductLinkFactory(company=self.company_link.company, url=self.company_link.url)

    def test_str(self):
        self.assertEqual(
            f"{self.company_link.company} - {self.company_link.name} - {self.company_link.url}",
            str(self.company_link),
        )

    def test_save_link_url_resets_is_valid(self):
        self.company_link.is_valid = False
        self.company_link.save()
        self.company_link.refresh_from_db()
        self.assertFalse(self.company_link.is_valid)
        # update company_link url
        self.company_link.url = fake.url()
        self.company_link.save()
        self.company_link.refresh_from_db()
        # test is_valid is true again
        self.assertTrue(self.company_link.is_valid)


class DealTests(TestCase):
    def setUp(self):
        self.manager = SuperUserFactory()
        self.customer = CustomerFactory()
        self.product = ProductFactory()
        self.other_product = ProductFactory()
        self.deal = DealFactory(manager=self.manager, customer=self.customer, product=self.product)
        # batch
        self.init_count = Deal.objects.count()
        self.batch_size = 2

    def test_create(self):
        DealFactory.create_batch(
            self.batch_size,
            manager=self.manager,
            customer=self.customer,
            product=self.product,
        )
        self.assertEqual(Deal.objects.count(), self.batch_size + self.init_count)

    def test_update(self):
        self.deal.product = self.other_product
        self.deal.full_clean()
        self.deal.save()
        self.assertEqual(self.deal.product, self.other_product)

    def test_delete(self):
        self.deal.delete()
        self.assertEqual(Deal.objects.count(), 0)

    def test_delete_customer_sets_null(self):
        self.customer.delete()
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.customer, None)
        self.assertEqual(self.deal.manager, self.manager)
        self.assertEqual(self.deal.product, self.product)

    def test_delete_manager_sets_null(self):
        self.manager.delete()
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.manager, None)
        self.assertEqual(self.deal.customer, self.customer)
        self.assertEqual(self.deal.product, self.product)

    def test_delete_product_cascades(self):
        self.product.delete()
        self.assertEqual(Deal.objects.count(), 0)
        self.assertTrue(Customer.objects.count(), 1)
        self.assertTrue(User.objects.count(), 1)

    def test_fields(self):
        self.assertEqual(self.deal.manager, self.manager)
        self.assertEqual(self.deal.customer, self.customer)
        self.assertEqual(self.deal.product, self.product)
        self.assertTrue(self.deal.created_at)
        self.assertTrue(self.deal.updated_at)

    def test_str(self):
        self.assertEqual(f"{self.deal.customer} - {self.deal.product}", str(self.deal))
