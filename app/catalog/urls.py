from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("services/", views.ServiceListView.as_view(), name="service_list"),
    path("services/manage/", views.ServiceAdminListView.as_view(), name="service_admin_list"),
    path("services/create/", views.ServiceCreateView.as_view(), name="service_create"),
    path("services/<slug:slug>/edit/", views.ServiceUpdateView.as_view(), name="service_edit"),
    path("services/<slug:slug>/", views.ServiceDetailView.as_view(), name="service_detail"),
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tags/search/", views.tag_search, name="tag_search"),
    path("tags/get-or-create/", views.tag_get_or_create, name="tag_get_or_create"),
    path("tags/<int:pk>/delete/", views.tag_delete, name="tag_delete"),
]
