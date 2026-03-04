from django.contrib import admin

from .models import AnalysisResult


class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text",
        "user_type",
        "user_category",
        "user_location",
        "analyzed_text",
        "improved_text",
        "reference_urls",
    )


admin.site.register(AnalysisResult, AnalysisResultAdmin)
