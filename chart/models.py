from django.db import models
from django.contrib import admin

class Chart(models.Model):
	"""Chart"""
	options = models.TextField(null=True, blank=True)
	data_provider = models.TextField()
	auth_required = models.BooleanField(default=False)
	
	class Meta:
		app_label = 'chart'

class ChartAdmin(admin.ModelAdmin):
    """Chart admin class"""

admin.site.register(Chart, ChartAdmin)
