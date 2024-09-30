from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Customer)
admin.site.register(Connection)
admin.site.register(Bill)
admin.site.register(Unitrate)
admin.site.register(Bill_cal)
admin.site.register(Bill_load)
admin.site.register(Bill_fppas)
admin.site.register(Bill_cess)
admin.site.register(Bill_duty)

admin.site.register(Feedback)