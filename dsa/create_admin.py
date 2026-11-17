from django.contrib.auth.models import User

if User.objects.filter(username="admin").exists():
    print("Админ уже есть")
else:
    User.objects.create_superuser("admin", "", "907840505")
    print("Админ создан: admin / 907840505")
