from django import forms


class InsertForm(forms.Form):
    txt = forms.CharField(max_length=256)
    lat = forms.FloatField()
    lon = forms.FloatField()
    zoom = forms.IntegerField()


class UpdattrForm(forms.Form):
    id = forms.IntegerField()
    txt = forms.CharField(max_length=256)


class UpdgeomForm(forms.Form):
    id = forms.IntegerField()
    lat = forms.FloatField()
    lon = forms.FloatField()
    zoom = forms.IntegerField()


class DelForm(forms.Form):
    id = forms.IntegerField()