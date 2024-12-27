from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Teacher, Parent

class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'fullname', 'role', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'fullname', 'role')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('fullname', 'phone', 'dob', 'address1', 'address2', 'city', 'state', 'country', 'postal_code', 'image'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

class StudentAdmin(admin.ModelAdmin):
    model = Student
    list_display = ('full_name', 'student_class', 'date_of_birth', 'address')
    search_fields = ('full_name', 'student_class')
    list_filter = ('student_class',)

class TeacherAdmin(admin.ModelAdmin):
    model = Teacher
    list_display = ('full_name', 'subject', 'phone_number', 'years_of_experience')
    search_fields = ('full_name', 'subject')
    list_filter = ('subject',)

class ParentAdmin(admin.ModelAdmin):
    model = Parent
    list_display = ('full_name', 'phone_number', 'children_count')
    search_fields = ('full_name', 'phone_number')

    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = 'Number of Children'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Parent, ParentAdmin)
