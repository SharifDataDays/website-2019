from django.contrib import admin

from apps.intro.models import StaffReborn, StaffTeam, StaffSubTeam, Staff


class StaffRebornAdmin(admin.ModelAdmin):
    fields = [
               'name',
               'sub_team',
               'image'
               ]


class StafAdmin(admin.ModelAdmin):
    fields = ['name', 'team', 'image']


class StafTeamAdmin(admin.ModelAdmin):
    fields = ['name']


class StafSubTeamAdmin(admin.ModelAdmin):
    fields = ['name', 'parent_team']


admin.site.register(Staff, StafAdmin)
admin.site.register(StaffSubTeam, StafSubTeamAdmin)
admin.site.register(StaffTeam, StafTeamAdmin)
admin.site.register(StaffReborn, StaffRebornAdmin)
