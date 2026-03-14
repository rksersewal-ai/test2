from django.apps import AppConfig

class OcrQueueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ocr_queue'
    verbose_name = 'OCR Queue'
