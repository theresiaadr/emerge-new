from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import FollowUpWA, Instansi, Kunjungan, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "no_hp", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (("Profil Srikaton", {"fields": ("role", "no_hp")}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profil Srikaton", {"fields": ("first_name", "last_name", "role", "no_hp")}),
    )


@admin.register(Instansi)
class InstansiAdmin(admin.ModelAdmin):
    list_display = ("nama", "dibuat_oleh", "dibuat_pada")
    search_fields = ("nama",)
    readonly_fields = ("dibuat_pada",)


class FollowUpInline(admin.TabularInline):
    model = FollowUpWA
    extra = 0
    readonly_fields = ("waktu",)


@admin.register(Kunjungan)
class KunjunganAdmin(admin.ModelAdmin):
    list_display = ("instansi", "sales", "tanggal", "status", "tahap")
    list_filter = ("status", "sales", "tahap")
    search_fields = ("instansi__nama",)
    date_hierarchy = "tanggal"
    autocomplete_fields = ("instansi",)
    inlines = [FollowUpInline]


@admin.register(FollowUpWA)
class FollowUpWAAdmin(admin.ModelAdmin):
    list_display = ("kunjungan", "jenis", "oleh", "waktu")
    list_filter = ("jenis",)
    search_fields = ("kunjungan__instansi__nama",)
