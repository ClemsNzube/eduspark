from django.contrib import admin
from .models import Grade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'score', 'letter_grade', 'last_updated')
    list_filter = ('subject', 'last_updated')
    search_fields = ('student__full_name', 'subject__name')
    ordering = ('-last_updated',)
    readonly_fields = ('letter_grade',)

    def letter_grade(self, obj):
        return obj.letter_grade
    letter_grade.short_description = 'Letter Grade'
