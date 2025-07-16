# C:\DjangoProject\characters\resources.py

from import_export import resources
from .models import Warrior, Mage, Enemy, Item

class WarriorResource(resources.ModelResource):
    class Meta:
        model = Warrior
        fields = ('id', 'owner', 'name', 'health', 'damage', 'defense')

class MageResource(resources.ModelResource):
    class Meta:
        model = Mage
        fields = ('id', 'owner', 'name', 'health', 'magic_damage', 'mana', 'defense')

class EnemyResource(resources.ModelResource):
    class Meta:
        model = Enemy
        fields = ('id', 'name', 'health', 'attack', 'defense')

class ItemResource(resources.ModelResource):
    class Meta:
        model = Item
        # Asegúrate de que estos campos existan en tu modelo Item
        fields = ('id', 'name', 'item_type', 'description', 'value',
                  'damage_buff', 'health_restore', 'mana_restore', 'extra_attributes')