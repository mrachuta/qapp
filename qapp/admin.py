from django.contrib import admin
from .models import Tram, OperationArea, Gate, Comment, Log, GateFile, Bogie
# Register your models here.


class TramAdmin(admin.ModelAdmin):
    list_display = ('number', 'manufactured_date')


admin.site.register(Tram, TramAdmin)

class BogieAdmin(admin.ModelAdmin):
    list_display = ('number', 'manufactured_date')


admin.site.register(Bogie, BogieAdmin)

admin.site.register(OperationArea)


class GateFileToGateAdmin(admin.TabularInline):
    model = GateFile
    extra = 0


class GateAdmin(admin.ModelAdmin):

    list_display = ('tram', 'bogie', 'car', 'area', 'operation_no',)
    inlines = [GateFileToGateAdmin]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


admin.site.register(Gate, GateAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('com_rel_gate', 'text', 'date_time', )
    ordering = ('-date_time', )


admin.site.register(Comment, CommentAdmin)

admin.site.register(Log)