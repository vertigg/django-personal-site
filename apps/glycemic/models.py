from django.db import models


class GlycemicData(models.Model):
    time = models.BigIntegerField(primary_key=True)
    glycemic = models.FloatField()

    class Meta:
        db_table = "glycemic_data"

    def __str__(self):
        return f"{self.time}: {self.glycemic}"
