from django.contrib import admin
from django.apps import apps

app = apps.get_app_config('wildlife')
#register all models to be displayed in the admin app
for model in app.get_models():
    admin.site.register(model)
