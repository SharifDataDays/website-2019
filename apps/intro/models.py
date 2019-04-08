from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=20, default="")
    team = models.CharField(max_length=20, default="")
    image = models.ImageField(null=True, upload_to='staff_pic')

    def __str__(self):
        return str(self.name)

