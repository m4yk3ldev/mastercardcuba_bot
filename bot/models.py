from django.db import models


# Create your models here.
class Profile(models.Model):
    external_id = models.IntegerField(verbose_name="ID Telegram", unique=True)
    username = models.CharField(max_length=250, verbose_name="Username de telegram")
    name = models.CharField(max_length=250, verbose_name="Nombre del Usuario")
    email = models.CharField(max_length=250, verbose_name="Correo del Usuario", null=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f'ID {self.external_id} username {self.username}'
