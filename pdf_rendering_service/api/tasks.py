
import dramatiq
import PIL
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError
from pika.exceptions import ConnectionWrongStateError

from django.conf import settings
from .models import Document



@dramatiq.actor
def process_pdf(document_id):

	print("processing document {}".format(document_id))

	try:
		document = Document.objects.get(id=document_id)
		pdf_file = settings.MEDIA_ROOT + "document{}.pdf".format(document_id)
		pages = convert_from_path(pdf_file, dpi=200, size=(1200, 1600) )
		for i, page in enumerate(pages):
			png_file =  settings.MEDIA_ROOT + document.get_png_filename(i+1)
			page.save(png_file, 'PNG')
			print(png_file)
		document.status = Document.STATUS_DONE
		document.n_pages = len(pages)
		document.save()
		print("document {} processed successfully !".format(document.id))
	except Document.DoesNotExist:
		# document.status = Document.STATUS_FAILED
		print('pdf file does not exist')	
	except PIL.Image.DecompressionBombError:
		# document.status = Document.STATUS_FAILED
		print("pdf file too large")	
	except PDFPageCountError:
		# document.status = Document.STATUS_FAILED
		print('invalid pdf file')	

	# to avoid "missed heartbeats from client" warnings from rabbitmq, see https://github.com/Bogdanp/django_dramatiq/issues/44
	try:
		dramatiq.get_broker().connection.close()
	except ConnectionWrongStateError:
		pass







