from django.db.models.query import QuerySet
from django.test import TestCase

from crm.documents.tests.factories import DocumentFactory, PDFBlockFactory
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory

from ..selectors import (
    company_list,
    company_product_link_list,
    company_type_list,
    customer_list,
    deal_list,
    document_list,
    pdf_block_list,
    pdf_block_list_filter_by_ids,
    product_list,
    user_get_company_ids,
    user_list,
)
from .factories import (
    CompanyFactory,
    CompanyMemberFactory,
    CompanyProductLinkFactory,
    CompanyTypeFactory,
    CustomerFactory,
    DealFactory,
    ProductFactory,
)


class TestSelectors(TestCase):
    def setUp(self):
        # create users
        self.superuser = SuperUserFactory()
        self.admin = AdminUserFactory()
        self.manager = ManagerUserFactory()
        self.other_superuser = SuperUserFactory()
        # create company types
        self.company_type = CompanyTypeFactory(user=self.superuser)
        self.company_type_1 = CompanyTypeFactory(user=self.superuser)
        self.other_company_type = CompanyTypeFactory(user=self.other_superuser)
        # create companies
        self.company = CompanyFactory(company_type=self.company_type)
        self.company_1 = CompanyFactory(company_type=self.company_type)
        self.other_company = CompanyFactory(company_type=self.other_company_type)
        # create company member
        self.members = [
            CompanyMemberFactory(user=self.superuser, company=self.company),
            CompanyMemberFactory(user=self.superuser, company=self.company_1),
            CompanyMemberFactory(user=self.admin, company=self.company),
            CompanyMemberFactory(user=self.manager, company=self.company),
            CompanyMemberFactory(user=self.other_superuser, company=self.other_company),
        ]
        # create company product links
        self.company_link = CompanyProductLinkFactory(company=self.company)
        self.company_link_1 = CompanyProductLinkFactory(company=self.company_1)
        self.other_company_link = CompanyProductLinkFactory(company=self.other_company)
        # create company product
        self.product = ProductFactory(company=self.company)
        self.product_1 = ProductFactory(company=self.company_1)
        self.other_product = ProductFactory(company=self.other_company)
        # create customers
        self.customer = CustomerFactory(company=self.company)
        self.customer_1 = CustomerFactory(company=self.company_1)
        self.other_customer = CustomerFactory(company=self.other_company)
        # create deals
        self.deal = DealFactory(manager=self.manager, customer=self.customer, product=self.product)
        self.deal_1 = DealFactory(manager=self.superuser, customer=self.customer, product=self.product_1)
        self.other_deal = DealFactory(
            manager=self.other_superuser, customer=self.other_customer, product=self.other_product
        )
        # create pdf blocks
        self.pdf_block = PDFBlockFactory(company=self.company)
        self.pdf_block_1 = PDFBlockFactory(company=self.company_1)
        self.other_pdf_block = PDFBlockFactory(company=self.other_company)
        # create documents
        self.document = DocumentFactory(product=self.product)
        self.document_1 = DocumentFactory(product=self.product_1)
        self.other_document = DocumentFactory(product=self.other_product)

    def test_user_get_company_ids(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.company.id, self.company_1.id]),
            (self.admin, [self.company.id]),
            (self.manager, [self.company.id]),
            (self.other_superuser, [self.other_company.id]),
        ]
        for user, expected_result in test_cases:
            result = user_get_company_ids(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_user_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.superuser, self.manager, self.admin]),
            (self.admin, [self.superuser, self.manager, self.admin]),
            (self.manager, [self.superuser, self.manager, self.admin]),
            (self.other_superuser, [self.other_superuser]),
        ]
        for user, expected_result in test_cases:
            result = user_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_pdf_block_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.pdf_block, self.pdf_block_1]),
            (self.admin, [self.pdf_block]),
            (self.manager, [self.pdf_block]),
            (self.other_superuser, [self.other_pdf_block]),
        ]
        for user, expected_result in test_cases:
            result = pdf_block_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_pdf_block_list_filter_by_ids(self):
        payload = [1, 2, self.pdf_block_1.id, self.other_pdf_block.id]
        test_cases = [  # for_user, payload, expected_result
            (self.superuser, payload, [self.pdf_block_1]),
            (self.admin, payload, []),
            (self.manager, payload, []),
            (self.other_superuser, payload, [self.other_pdf_block]),
        ]
        for user, payload, expected_result in test_cases:
            result = pdf_block_list_filter_by_ids(user, payload)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_document_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.document, self.document_1]),
            (self.admin, [self.document]),
            (self.manager, [self.document]),
            (self.other_superuser, [self.other_document]),
        ]
        for user, expected_result in test_cases:
            result = document_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_company_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.company, self.company_1]),
            (self.admin, [self.company]),
            (self.manager, [self.company]),
            (self.other_superuser, [self.other_company]),
        ]
        for user, expected_result in test_cases:
            result = company_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_company_type_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.company_type, self.company_type_1]),
            (self.admin, [self.company_type]),
            (self.manager, [self.company_type]),
            (self.other_superuser, [self.other_company_type]),
        ]
        for user, expected_result in test_cases:
            result = company_type_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_company_product_link_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.company_link, self.company_link_1]),
            (self.admin, [self.company_link]),
            (self.manager, [self.company_link]),
            (self.other_superuser, [self.other_company_link]),
        ]
        for user, expected_result in test_cases:
            result = company_product_link_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_customer_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.customer, self.customer_1]),
            (self.admin, [self.customer]),
            (self.manager, [self.customer]),
            (self.other_superuser, [self.other_customer]),
        ]
        for user, expected_result in test_cases:
            result = customer_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_product_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.product, self.product_1]),
            (self.admin, [self.product]),
            (self.manager, [self.product]),
            (self.other_superuser, [self.other_product]),
        ]
        for user, expected_result in test_cases:
            result = product_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))

    def test_deal_list(self):
        test_cases = [  # for_user, expected_result
            (self.superuser, [self.deal, self.deal_1]),
            (self.admin, [self.deal]),
            (self.manager, [self.deal]),
            (self.other_superuser, [self.other_deal]),
        ]
        for user, expected_result in test_cases:
            result = deal_list(user)
            # test result
            self.assertIsInstance(result, QuerySet)
            self.assertFalse(set(result) - set(expected_result))
