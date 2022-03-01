# from django.conf.urls import url
# from django.urls import path, include

# urlpatterns = [
#     path('api/', include('app.api.urls')),
# ]


from django.urls import path
# from django.conf import settings
# from django.conf.urls.static import static


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


