import ssl
from django.core.mail.backends.smtp import EmailBackend
EmailBackend.ssl_context = ssl._create_unverified_context()
