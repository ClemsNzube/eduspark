from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import *


class UserAdmin(BaseUserAdmin):
    # Customize fields in the admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('fullname', 'phone', 'dob', 'address1', 'address2', 'city', 'state', 'country', 'postal_code', 'image', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('email', 'fullname', 'role', 'is_active', 'is_staff')
    search_fields = ('email', 'fullname', 'role')
    ordering = ('email',)


@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'student_class', 'address')
    search_fields = ('full_name',)
    list_filter = ('student_class',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'subject', 'phone_number', 'years_of_experience')
    search_fields = ('full_name', 'subject')
    list_filter = ('subject',)


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number')
    search_fields = ('full_name',)
    filter_horizontal = ('children',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'day_of_week', 'start_time', 'end_time', 'room', 'student_class')
    search_fields = ('subject__name', 'teacher__full_name', 'student_class__name')
    list_filter = ('day_of_week', 'student_class')


# Register the custom user admin
admin.site.register(User, UserAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'completed', 'created_at')  # Fields to display in the list view
    list_filter = ('completed', 'created_at')  # Filters in the sidebar
    search_fields = ('name', 'user__username')  # Fields for the search bar
    ordering = ('-created_at',)  # Default ordering (newest tasks first)

admin.site.register(Task, TaskAdmin)

class ContentAdminForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(),  # Use CKEditor widget for the 'description' field
        }

class ContentAdmin(admin.ModelAdmin):
    form = ContentAdminForm  # Attach the custom form
    list_display = ('title', 'subject', 'teacher', 'content_type', 'date_uploaded')
    list_filter = ('subject', 'content_type', 'teacher', 'date_uploaded')
    search_fields = ('title', 'description', 'teacher__name', 'subject__name')
    ordering = ('-date_uploaded',)
    date_hierarchy = 'date_uploaded'


# Register the Content model with the customized admin
admin.site.register(Content, ContentAdmin)

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'content', 'date_submitted', 'status', 'feedback')
    list_filter = ('status', 'date_submitted', 'content')
    search_fields = ('student__full_name', 'content__title')
    ordering = ('-date_submitted',)
    
    # Make 'status' and 'feedback' fields editable from the list view
    list_editable = ('status', 'feedback')

    # Customize the form view for submission editing
    fieldsets = (
        (None, {
            'fields': ('student', 'content', 'answer', 'status', 'feedback')
        }),
        ('Date Information', {
            'fields': ('date_submitted',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date_submitted',)

    # Show a count of the number of submissions per content
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'content')

# Register the Submission model with the custom admin class
admin.site.register(Submission, SubmissionAdmin)