from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# python to human readable text
from django.utils.translation import gettext as _

from core.models import UserAccount


class UserAccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_superuser')
    ordering = ['id']
    readonly_fields = ('date_joined', 'last_login')

    # we have to override UserAdmin as well, if you want to see your custom fields from core/model/UserAccount()
    # Customizing our user_admin field sets to support our Custom_user_model as opposed to the default model.
    fieldsets = (
        (None, {'fields': ('email',
                           'password'
                           )
                }),
        (_('Personal Info'), {'fields': ('username',)
                              }),
        (_('Permossions'), {'fields': ('is_active',
                                       'is_staff',
                                       'is_superuser')
                            }),
        (_('Important dates'), {'fields': ('last_login',
                                           'date_joined')
                                }),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


# Register your models here
admin.site.register(UserAccount, UserAccountAdmin)
