from django.contrib import admin

from blog.models import Blog, Discussion, ViewedBlog

admin.site.register(Blog)
admin.site.register(Discussion)
admin.site.register(ViewedBlog)
