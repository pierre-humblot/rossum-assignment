
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from .models import Document
from .serializers import DocumentStatusSerializer
from .serializers import DocumentIdSerializer
from .tasks import process_pdf



@api_view(["POST"])
def upload_pdf(request):

	try:
		file = request.FILES["file"]
	except MultiValueDictKeyError:
		return Response({"res": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

	if file.content_type != "application/pdf":
		return Response({"res": "Only pdf files are accepted"}, status=status.HTTP_400_BAD_REQUEST)

	# 2 steps since pdf_file filename depends on document.id
	document = Document.objects.create()
	document.pdf_file = file

	try:
		document.full_clean() # calls validators (file_size)
		document.save()
	except ValidationError as e:
		return Response({"res": e}, status=status.HTTP_400_BAD_REQUEST)

	process_pdf.send(document.id)
	
	serializer = DocumentIdSerializer(document)
	return Response(serializer.data, status = status.HTTP_201_CREATED)



@api_view(["GET"])
def status_pdf(request, document_id):

	try:
		document = Document.objects.get(id=document_id)
		serializer = DocumentStatusSerializer(document)
		return Response(serializer.data)
	except Document.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(["GET"])
def view_page(request, document_id, n_page):

	try:
		document = Document.objects.get(id=document_id)
		if document.status != Document.STATUS_DONE or n_page > document.n_pages:
			return Response(status=status.HTTP_404_NOT_FOUND)
		file_name = document.get_png_filename(n_page)
		fs = FileSystemStorage(settings.MEDIA_ROOT)
		response = FileResponse(fs.open(file_name, 'rb'), content_type='application/force-download')
		response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
		return response
	except (Document.DoesNotExist, OSError):
		return Response(status=status.HTTP_404_NOT_FOUND)

