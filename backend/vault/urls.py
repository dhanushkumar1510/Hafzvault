from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("receipts", views.ReceiptViewSet, basename="receipt")

urlpatterns = [
    path("health/", views.HealthView.as_view()),
    path("accounts/lookup/", views.AccountLookupView.as_view()),
    path("accounts/", views.AccountCreateView.as_view()),
    path("profile/", views.ProfileView.as_view()),
    path("summary/", views.SummaryView.as_view()),
    path("", include(router.urls)),
]
