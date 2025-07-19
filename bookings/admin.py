from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'vehicle', 'start_date', 'end_date', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'deposit_paid', 'start_date', 'end_date', 'created_at')
    search_fields = ('customer__username', 'vehicle__plate_number', 'vehicle__make', 'vehicle__model')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'duration_days', 'is_active', 'is_overdue')
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('customer', 'vehicle', 'start_date', 'end_date', 'status')
        }),
        ('Financial', {
            'fields': ('total_amount', 'deposit_amount', 'deposit_paid')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
        ('Calculated Fields', {
            'fields': ('duration_days', 'is_active', 'is_overdue'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
