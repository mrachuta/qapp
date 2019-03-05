from django.contrib import admin
from .models import Tram, OperationArea, Gate, Comment, Log, GateFile, Bogie, CommentFile


class TramAdmin(admin.ModelAdmin):

    list_display = ('number', 'manufactured_date')


admin.site.register(Tram, TramAdmin)


class BogieAdmin(admin.ModelAdmin):

    list_display = ('number', 'manufactured_date', 'btype')


admin.site.register(Bogie, BogieAdmin)


class OperationAreaAdmin(admin.ModelAdmin):

    list_display = ('area', 'foreman')


admin.site.register(OperationArea, OperationAreaAdmin)


class GateFileToGateAdmin(admin.TabularInline):

    model = GateFile
    extra = 0


class GateAdmin(admin.ModelAdmin):

    list_display = ('id', 'tram', 'bogie', 'car', 'area', 'operation_no', 'name')
    inlines = [GateFileToGateAdmin]
    ordering = ('-tram', '-bogie')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


admin.site.register(Gate, GateAdmin)


class CommentFileToCommentAdmin(admin.TabularInline):
    model = CommentFile
    extra = 0


class CommentAdmin(admin.ModelAdmin):

    list_display = ('id', 'com_rel_gate', 'text', 'date_time', )
    inlines = [CommentFileToCommentAdmin]
    ordering = ('-date_time', )


admin.site.register(Comment, CommentAdmin)


class LogAdmin(admin.ModelAdmin):

    list_display = ('id', 'log_rel_gate', 'date_time', 'author', 'action')


admin.site.register(Log, LogAdmin)
