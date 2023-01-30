from django.db import models

# Create your models here.
class PersonUnit(models.Model):
    name = models.CharField(max_length=50, null=False)
    person_id = models.CharField(primary_key=True, max_length=20, null=False)
    address = models.CharField(max_length=100, default="")
    contact = models.CharField(max_length=20, default="")

    def __str__(self):
        return "%s (%s)" % (self.name, self.person_id)


class PujaUnit(models.Model):
    # puja = 法會
    year = models.IntegerField(default=112, null=False)
    name = models.CharField(max_length=10, null=False)
    start = models.DateField(null=False)
    end = models.DateField(null=False)

    def __str__(self):
        return "%d-%s" % (self.year, self.name)


class DataUnit(models.Model):
    person = models.ForeignKey("PersonUnit", on_delete=models.CASCADE, null=False)
    puja = models.ForeignKey("PujaUnit", on_delete=models.CASCADE, null=False)
    info_type = models.CharField(max_length=5, null=False)

    def __str__(self):
        return "%s (%s) -> %d-%s" % (self.person.name, self.person.person_id, self.puja.year, self.puja.name)


