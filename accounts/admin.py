from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, UserProfile

from .forms import SankhofaUserCreationForm, SankhofaUserChangeForm

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(BaseUserAdmin):
    add_form = SankhofaUserCreationForm
    form = SankhofaUserChangeForm
    inlines = (UserProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'get_verified_status', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'profile__is_verified')
    readonly_fields = ('last_login', 'date_joined')
     
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password', 'password_2'),
        }),
    )
    ordering = ('email',)
    actions = ['verify_users', 'unverify_users']

    def get_verified_status(self, obj):
        try:
            return obj.profile.is_verified
        except UserProfile.DoesNotExist:
            return False
    get_verified_status.boolean = True
    get_verified_status.short_description = 'Vérifié'

    @admin.action(description="Valider les profils sélectionnés")
    def verify_users(self, request, queryset):
        for user in queryset:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_verified = True
            profile.save()
        self.message_user(request, "Les profils ont été validés avec succès.")

    @admin.action(description="Révoquer la validation des profils")
    def unverify_users(self, request, queryset):
        for user in queryset:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_verified = False
            profile.save()
        self.message_user(request, "La validation a été révoquée.")

admin.site.register(CustomUser, CustomUserAdmin)
# Register UserProfile separately if needed, but Inline is better for validation flow
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'phone_number', 'business_name', 'vehicle_type', 'coverage_area')
    list_filter = ('is_verified', 'user__role', 'vehicle_type', 'country')
    search_fields = ('user__email', 'business_name', 'phone_number')
    actions = ['verify_profiles']

    @admin.action(description="Valider le profil")
    def verify_profiles(self, request, queryset):
        queryset.update(is_verified=True)
