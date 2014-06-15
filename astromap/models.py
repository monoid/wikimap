from django.contrib.gis.db import models

class Point(models.Model):
    id = models.AutoField(primary_key=True)
    mapid = models.IntegerField(null=False)
    title = models.CharField(max_length=256, null=False)
    zoom = models.IntegerField(null=False, default=13)
    point = models.PointField()
    kook = models.CharField(max_length=40, null=True)
    ip = models.PositiveIntegerField(null=True)  # TODO models.IPAddressField()
    ts = models.DateTimeField(auto_now=True, auto_now_add=True)
    ptxt = models.CharField(max_length=1024, null=True)

    objects = models.GeoManager()

    def to_dict(self):
        return {'id': self.id,
                'mapid': self.mapid,
                'title': self.title,
                'zoom': self.zoom,
                'point': self.point,
                'kook': self.kook,
                'ts': self.ts}

    def __unicode__(self):
        return u"%s %s" % (self.title, unicode(self.point))

    class Meta:
        db_table = 'points'
        ordering = ['-ts']
        get_latest_by = 'ts'
        managed = False
