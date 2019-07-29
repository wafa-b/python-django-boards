from django.contrib import admin
from .models import Board
from .models import Topic
from .models import Post

# Register your models here.
admin.site.register(Board)
admin.site.register(Topic)
admin.site.register(Post)

