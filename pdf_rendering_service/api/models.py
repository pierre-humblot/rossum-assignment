
from django.db import models
from django.core.exceptions import ValidationError


def file_size(value):
	limit = 10 * 1024 * 1024
	if value.size > limit:
		raise ValidationError('File too large. Size should not exceed 10 MiB.')



class Document(models.Model):

	def upload_path(self, file):
		return 'document{}.pdf'.format(self.id)

	STATUS_PROCESSING = "processing"
	STATUS_FAILED = "failed"
	STATUS_DONE = "done"
	STATUSES = [
		(STATUS_PROCESSING, "Processing"),
		(STATUS_FAILED, "Failed"),
		(STATUS_DONE, "Done"),
	]

	status = models.CharField(max_length=10, default=STATUS_PROCESSING, choices=STATUSES)
	n_pages = models.PositiveSmallIntegerField(default = 0)
	pdf_file = models.FileField(upload_to=upload_path, null = True, validators=[file_size])

	def get_png_filename(self, n_page):
		return "document{}_{}.png".format(self.id, n_page)

	def __str__(self):
		return 'Document({})'.format(", ".join(["{}:{}".format(key,value) for key, value in self.__dict__.items() if not key.startswith("_")]))

