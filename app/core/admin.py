from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from accounts import models
from university import models as university_models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name', 'cpf', 'phone')}),
        (_('Address Info'), {'fields': ('street',
                                        'state',
                                        'city',
                                        'zip_code',
                                        'complement')}),
        (
            _('Persmissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Groups'), {'fields': ('groups',)}),
        (_('Important Dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': 'wide',
            'fields': ('email', 'password1', 'password2')
        }),
    )
    filter_horizontal = ('groups',)


admin.site.register(models.User, UserAdmin)
admin.site.register(university_models.Employee)
admin.site.register(university_models.Job)
