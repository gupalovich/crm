from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from .companies.views import CompanyViewset
from .companylinks.views import CompanyProductLinkViewset
from .companytypes.views import CompanyTypeViewset
from .customers.views import CustomerViewset
from .deals.views import DealViewset
from .documents.views import DocumentViewset
from .pdfblocks.views import PDFBlockViewset
from .products.views import ProductViewset
from .translations.views import ProductTranslationViewset
from .users.views import UserViewset

app_name = "api"

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewset)
router.register("companies", CompanyViewset)
router.register("company-types", CompanyTypeViewset)
router.register("company-links", CompanyProductLinkViewset)
router.register("products", ProductViewset)
router.register("translations", ProductTranslationViewset, basename="translation")
router.register("customers", CustomerViewset)
router.register("deals", DealViewset)
router.register("pdf-blocks", PDFBlockViewset)
router.register("documents", DocumentViewset)


urlpatterns = router.urls
