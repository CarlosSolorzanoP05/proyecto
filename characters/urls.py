# C:\DjangoProject\characters\urls.py

from django.urls import path
from . import views # Importa todas las vistas de tu archivo views.py

app_name = 'characters' # CRÍTICO para el namespace

urlpatterns = [
    # URLs para personajes de USUARIO (Warrior, Mage)
    path('list/', views.CharacterListView.as_view(), name='character_list'),

    path('warrior/create/', views.WarriorCreateView.as_view(), name='warrior_create'),
    path('warrior/<int:pk>/update/', views.WarriorUpdateView.as_view(), name='warrior_update'),
    path('warrior/<int:pk>/delete/', views.WarriorDeleteView.as_view(), name='warrior_delete'),
    path('warrior/export/', views.WarriorExportView.as_view(), name='warrior_export'),   # AÑADIDA
    path('warrior/import/', views.WarriorImportView.as_view(), name='warrior_import'),   # AÑADIDA

    path('mage/create/', views.MageCreateView.as_view(), name='mage_create'),
    path('mage/<int:pk>/update/', views.MageUpdateView.as_view(), name='mage_update'),
    path('mage/<int:pk>/delete/', views.MageDeleteView.as_view(), name='mage_delete'),
    path('mage/export/', views.MageExportView.as_view(), name='mage_export'),   # AÑADIDA
    path('mage/import/', views.MageImportView.as_view(), name='mage_import'),   # AÑADIDA

    # URLs para ENEMIGOS (Admin)
    path('enemies/', views.EnemyListView.as_view(), name='enemy_list'),
    path('enemies/create/', views.EnemyCreateView.as_view(), name='enemy_create'),
    path('enemies/<int:pk>/update/', views.EnemyUpdateView.as_view(), name='enemy_update'),
    path('enemies/<int:pk>/delete/', views.EnemyDeleteView.as_view(), name='enemy_delete'),
    path('enemies/export/', views.EnemyExportView.as_view(), name='enemy_export'),   # AÑADIDA
    path('enemies/import/', views.EnemyImportView.as_view(), name='enemy_import'),   # AÑADIDA

    # URLs para ÍTEMS (Admin)
    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/update/', views.ItemUpdateView.as_view(), name='item_update'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    path('items/export/', views.ItemExportView.as_view(), name='item_export'),
    path('items/import/', views.ItemImportView.as_view(), name='item_import'),
]