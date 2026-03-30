from django.contrib import admin

from.models import Campagne, DemandeUrgente, Donneur,Hopital,ReponseAppel,Inscription,Don

admin.site.register(Donneur)
admin.site.register(Hopital)
admin.site.register(DemandeUrgente)
admin.site.register(Campagne)
admin.site.register(Inscription)
admin.site.register(ReponseAppel)   
admin.site.register(Don)