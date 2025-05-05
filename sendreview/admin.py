from django.contrib import admin
from sendreview.models import Workers
from sendreview.models import Student
from sendreview.models import Company
from sendreview.models import City
from sendreview.models import CompanyCity
from sendreview.models import Comment

admin.site.register(Workers)
admin.site.register(Student)
admin.site.register(Company)
admin.site.register(City)
admin.site.register(CompanyCity)
admin.site.register(Comment)