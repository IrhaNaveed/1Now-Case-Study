from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'plate_number', 'owner', 'daily_rate', 'status', 'created_at')
    list_filter = ('status', 'fuel_type', 'transmission', 'year', 'created_at')
    search_fields = ('make', 'model', 'plate_number', 'owner__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'make', 'model', 'year', 'plate_number')
        }),
        ('Specifications', {
            'fields': ('fuel_type', 'transmission', 'color', 'seats', 'mileage')
        }),
        ('Pricing & Status', {
            'fields': ('daily_rate', 'status', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
