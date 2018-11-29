from django.contrib import admin

from book.models import User, Book, Author

admin.site.register(User)
admin.site.register(Book)
admin.site.register(Author)
