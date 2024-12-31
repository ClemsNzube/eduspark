from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentClass, Student, Teacher, Parent, Subject, Timetable


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
