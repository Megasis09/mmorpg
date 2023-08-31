from django.contrib import admin
from .models import Ad

class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()

        assign_perm('ads.view_ad', request.user, obj)
        assign_perm('ads.change_ad', obj.author, obj)
        assign_perm('ads.delete_ad', obj.author, obj)

admin.site.register(Ad, AdAdmin)