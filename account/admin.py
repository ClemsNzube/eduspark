from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.utils.html import format_html
from .models import *
from grades.models import Grade  # Import Grade model from the grades app


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
    list_display = ('full_name', 'subject', 'phone_number', 'years_of_experience', 'assigned_class_display')
    search_fields = ('full_name', 'subject', 'phone_number', 'assigned_class__name')
    list_filter = ('assigned_class', 'years_of_experience', 'subject')
    ordering = ('full_name',)
    autocomplete_fields = ('assigned_class',)

    def assigned_class_display(self, obj):
        return obj.assigned_class.name if obj.assigned_class else "No class assigned"
    assigned_class_display.short_description = "Assigned Class"


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



# Inline admin for the Grade model, used in the Submission admin
class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1  # Display one empty form for a new Grade entry (if needed)

# Admin configuration for the Submission model
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'content', 'status', 'date_submitted', 'feedback')
    list_filter = ('status', 'date_submitted', 'subject')
    search_fields = ('student__full_name', 'content__title', 'answer')
    ordering = ('-date_submitted',)  # Order by the most recent submissions
    actions = ['mark_as_correct', 'mark_as_incorrect', 'mark_as_pending']

    # Custom actions for marking the status of submissions
    def mark_as_correct(self, request, queryset):
        queryset.update(status='correct')
    mark_as_correct.short_description = "Mark selected submissions as Correct"

    def mark_as_incorrect(self, request, queryset):
        queryset.update(status='incorrect')
    mark_as_incorrect.short_description = "Mark selected submissions as Incorrect"

    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = "Mark selected submissions as Pending"

    # Inline admin for related Grade entries
    inlines = [GradeInline]

# Register the Submission model and the custom admin configuration
admin.site.register(Submission, SubmissionAdmin)


class AttendanceAdmin(admin.ModelAdmin):
    # Display the fields you want in the list view
    list_display = ('student', 'subject', 'content', 'attended', 'attendance_points', 'timestamp', 'attendance_status')
    
    # Add search capability for student and subject
    search_fields = ('student__full_name', 'subject__name', 'content__title')
    
    # Filter by attendance status
    list_filter = ('attended', 'subject', 'content')

    # Custom method to display the attendance status with color
    def attendance_status(self, obj):
        if obj.attended:
            return format_html('<span style="color: green;">Attended</span>')
        else:
            return format_html('<span style="color: red;">Absent</span>')
    attendance_status.short_description = 'Attendance Status'

    # Allow ordering by timestamp
    ordering = ('-timestamp',)

    # Customizing the fields for the detail view
    fieldsets = (
        (None, {
            'fields': ('student', 'subject', 'content', 'attended', 'attendance_points')
        }),
        # Removed the timestamp field from the form since it's auto-generated
    )

    # Exclude the 'timestamp' field from being manually edited
    exclude = ('timestamp',)

    # Allow only superusers to mark attendance
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Register the Attendance model with the customized admin
admin.site.register(Attendance, AttendanceAdmin)