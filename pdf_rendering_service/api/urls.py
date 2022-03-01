from django.urls import path

from .views import (
    upload_pdf,
    status_pdf,
    view_page,
)


urlpatterns = [
    path('documents', upload_pdf),
    path('documents/<int:document_id>', status_pdf),
    path('documents/<int:document_id>/pages/<int:n_page>', view_page),
]


