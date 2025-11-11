from rest_framework_nested import routers
from django.urls import path, include
from .views import (
    ContractViewSet,
    ContractDocumentViewSet,
    ContractTypeViewSet,
    ContractCommentViewSet,
)

# Main router
router = routers.SimpleRouter()
router.register(r"contracts", ContractViewSet, basename="contracts")
router.register(r"contract-types", ContractTypeViewSet, basename="contract-types")

# Nested routers
contracts_router = routers.NestedSimpleRouter(router, r"contracts", lookup="contract")
contracts_router.register(
    r"documents", ContractDocumentViewSet, basename="contract-documents"
)
contracts_router.register(
    r"comments", ContractCommentViewSet, basename="contract-comments"
)

# URLs
urlpatterns = [
    path("", include(router.urls)),
    path("", include(contracts_router.urls)),
]
