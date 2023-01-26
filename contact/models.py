from django.db import models

# Create your models here.
class PersonUnit(models.Model):
    name = models.CharField(max_length=50, null=False)
    person_id = models.CharField(primary_key=True, max_length=10, null=False)
    natural = models.BooleanField(default=True)
    legal = models.BooleanField(default=False)
    address = models.CharField(max_length=100, default="")
    contact = models.CharField(max_length=20, default="")

    def __str__(self):
        if self.legal:
            return "%s (%s)" % (self.name, self._id)

        return "%s (%s*****%s)" % (self.name, self._id[:3], self._id[:2])


class PujaUnit(models.Model):
    # puja = 法會
    year = models.IntegerField(default=2023, null=False)
    name = models.CharField(max_length=10, null=False)

    def __str__(self):
        return "%d-%s" % (self.year, self.name)


class DataUnit(models.Model):
    person = models.ForeignKey("PersonUnit", on_delete=models.CASCADE, null=False)
    puja = models.ForeignKey("PujaUnit", on_delete=models.CASCADE, null=False)
    info_type = models.CharField(max_length=5, null=False)

    def __str__(self):
        return "%s-%s" % (person.__str__(), puja.__str__())


