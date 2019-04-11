from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=128, default="")
    team = models.CharField(max_length=128, default="")
    image = models.ImageField(null=True, upload_to='staff_pic')

    def __str__(self):
        return str(self.name)


class StaffReborn(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    sub_team = models.ForeignKey('StaffSubTeam', null=False, blank=False)
    image = models.ImageField(upload_to='staff_pic', null=False, blank=False)
    
    def __str__(self):
        return '{} : {}'.format(self.name.__str__(), self.sub_team.__str__())


class StaffTeam(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return self.name.__str__()


class StaffSubTeam(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    parent_team = models.ForeignKey('StaffTeam', null=False, blank=False)
    
    def __str__(self):
        return '{} - {}'.format(self.parent_team.__str__(), self.name.__str__())

