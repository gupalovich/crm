from config import celery_app

from .services import CompanyProductLink, ProductIntegrationService


@celery_app.task()
def parse_product_task(company_product_link_pk: int) -> str:
    try:
        company_product_link = CompanyProductLink.objects.get(pk=company_product_link_pk)
    except CompanyProductLink.DoesNotExist:
        return "Invalid company_product_link_pk"
    else:
        try:
            product_integration = ProductIntegrationService(company_product_link)
            product_integration.fetch_products()
            product_integration.build_products()
            product_integration.save_products()
            return f"Product integration task for {company_product_link_pk} completed successfully."
        except Exception as e:
            raise e


@celery_app.task(bind=True)
def products_integration_task(self):
    try:
        # Get all valid CompanyProductLink instances
        valid_links = CompanyProductLink.objects.filter(is_valid=True)
        total_links = valid_links.count()
        processed_links = 0

        # Iterate through each valid CompanyProductLink and perform the integration steps
        for company_product_link in valid_links:
            try:
                product_integration = ProductIntegrationService(company_product_link)
                product_integration.fetch_products()
                product_integration.build_products()
                product_integration.save_products()
            except Exception as e:
                raise e
            finally:
                # Update task progress
                processed_links += 1
                self.update_state(state="PROGRESS", meta={"current": processed_links, "total": total_links})

        return "Products integration task completed successfully."
    except Exception as e:
        raise e
