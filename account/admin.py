from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Teacher, Parent

class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'role', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
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
    list_display = ('full_name', 'subject', 'phone_number')
    search_fields = ('full_name', 'subject')
    list_filter = ('subject',)

class ParentAdmin(admin.ModelAdmin):
    model = Parent
    list_display = ('full_name', 'children_count')
    search_fields = ('full_name',)

    def children_count(self, obj):
        return obj.children.count()  # Get count of associated children
    children_count.short_description = 'Number of Children'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Parent, ParentAdmin)
