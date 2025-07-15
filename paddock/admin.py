from django.contrib import admin, messages
from .models import Team, Driver, Race, PaddockImporter
import fastf1, os

# Register your models here.
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'team')
    search_fields = ('name', 'code')
    list_filter = ('team',)

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('season', 'name')
    search_fields = ('name',)
    list_filter = ('season',)

@admin.register(PaddockImporter)
class PaddockImporterAdmin(admin.ModelAdmin):
    list_display = ('run',)
    actions = ['fetch_paddock_data']

    @admin.action(description='Fetch and Store Teams, Drivers, and Races')
    def fetch_paddock_data(self, request, queryset):
        print(f"Action triggered")
        try:
            cache_path = './cache'
            season = 2025
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)
            fastf1.Cache.enable_cache(cache_path)

            session = fastf1.get_session(season, 'Australia', 'R')
            session.load()

            laps = session.laps

            added_teams = 0
            added_drivers = 0

            for drv_code in laps['Driver'].unique():
                lap = laps.pick_driver(drv_code).pick_quicklaps().reset_index()
                drv_info = lap['Driver']
                team_name = str(lap['Team']).strip()[:100]

                # save team
                team_obj, created_team = Team.objects.get_or_create(name=team_name)
                if created_team:
                    added_teams += 1

                drv_obj, created_driver = Driver.objects.get_or_create(
                    code=drv_code,
                    defaults={'name': drv_info, 'team':team_obj}
                )
                if not created_driver:
                    drv_obj.team = team_obj
                    drv_obj.save()
                else:
                    added_drivers += 1

            Race.objects.get_or_create(name='Australia', season=season)

            self.message_user(request, f"Imported: {added_teams} teams, {added_drivers} drivers", level=messages.SUCCESS)

        except Exception as e:
            self.message_user(request, f"Error: {e}", level=messages.ERROR)