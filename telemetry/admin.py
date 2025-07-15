from django.contrib import admin
from .models import DriverComparison
from .utils import fetch_and_store_comparison
from django.contrib import messages

# Register your models here.
@admin.register(DriverComparison)
class DriverComparisonAdmin(admin.ModelAdmin):
    list_display = ('season', 'race', 'driver1', 'driver2', 'comparison_type','created_at')

    actions = ['fetch_telemetry_data']


    @admin.action(description="Fetch and store telemetry data")
    def fetch_telemetry_data(self, request, queryset):
        success_count = 0

        for obj in queryset:
            try:
                fetch_and_store_comparison(
                    obj.season, obj.race, obj.driver1, obj.driver2, obj.comparison_type
                )
                success_count+=1
            except Exception as e:
                self.message_user(request, f"Failed for {obj}: {e}", level=messages.ERROR)

        self.message_user(request, f"Fetched telemetry data for {success_count} comparison(s)",
                          level=messages.SUCCESS)