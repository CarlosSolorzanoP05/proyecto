# C:\DjangoProject\characters\views.py

from django.shortcuts import render
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    View
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
import json

# Import your models
from .models import Warrior, Mage, Enemy, Item
# Import your forms
from .forms import WarriorForm, MageForm, EnemyForm, ItemForm

# --- Reusable Mixins for JSON Export/Import ---

class JSONExportMixin(LoginRequiredMixin, UserPassesTestMixin, View):
    model = None
    fields_to_export = []
    filename = "data.json"

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        if not self.model or not self.fields_to_export:
            raise NotImplementedError("JSONExportMixin requires 'model' and 'fields_to_export' attributes.")

        data = []
        for obj in self.model.objects.all():
            item_data = {}
            for field_name in self.fields_to_export:
                value = getattr(obj, field_name)
                # Handle specific field types if needed during export
                if hasattr(value, 'pk') and field_name != 'id': # Handle ForeignKeys (export only the ID)
                    item_data[field_name] = value.pk
                else:
                    item_data[field_name] = value
            data.append(item_data)

        # Prepare the JSON response for download
        response = HttpResponse(json.dumps(data, indent=4, ensure_ascii=False), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'
        return response

class JSONImportMixin(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Mixin for importing model data from a JSON file.
    Requires 'model', 'fields_mapping', and 'success_url_name' attributes.
    Uses a generic template for the import form.
    Only accessible by staff users.
    """
    model = None
    template_name = 'characters/generic_import.html' # A generic template for all imports
    fields_mapping = {} # Maps JSON keys to model field names
    success_url_name = 'characters:character_list' # Default redirect after successful import

    def test_func(self):
        # Only staff users can import data
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        # Render the import form
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if not self.model or not self.fields_mapping:
            raise NotImplementedError("JSONImportMixin requires 'model' and 'fields_mapping' attributes.")

        json_file = request.FILES.get('json_file')
        if not json_file:
            return render(request, self.template_name, {'error_message': 'No file selected.'})

        if not json_file.name.endswith('.json'):
            return render(request, self.template_name, {'error_message': 'The file must be a JSON file.'})

        try:
            file_data = json_file.read().decode('utf-8')
            data_list = json.loads(file_data)
        except json.JSONDecodeError as e:
            return render(request, self.template_name, {'error_message': f'Error reading JSON file: {e}'})
        except Exception as e:
            return render(request, self.template_name, {'error_message': f'Unexpected error processing file: {e}'})

        if not isinstance(data_list, list):
            return render(request, self.template_name, {'error_message': 'The JSON file must contain a list of objects.'})

        created_count = 0
        updated_count = 0
        errors = []

        for row_num, item_data_json in enumerate(data_list):
            try:
                instance_data = {}
                for json_key, model_field in self.fields_mapping.items():
                    if json_key in item_data_json:
                        # Special handling for ForeignKey fields (e.g., 'owner_id')
                        # For owned characters, 'owner' will be set by the overridden post method.
                        # For other models, if a foreign key ID is provided, use it.
                        if model_field.endswith('_id') and json_key == model_field: # If JSON key matches model_field_id
                             instance_data[model_field] = item_data_json[json_key]
                        elif not model_field.endswith('_id'): # For non-id fields, just map directly
                            instance_data[model_field] = item_data_json[json_key]

                # Special handling for JSONField (like 'extra_attributes')
                if 'extra_attributes' in self.fields_mapping.values() and 'extra_attributes' in item_data_json:
                    attr_value = item_data_json['extra_attributes']
                    if isinstance(attr_value, str):
                        # If it comes as a string, try parsing it (might be stringified JSON)
                        try:
                            instance_data['extra_attributes'] = json.loads(attr_value)
                        except json.JSONDecodeError:
                            instance_data['extra_attributes'] = {} # Default to empty dict on parse error
                            errors.append(f"Object {row_num + 1}: Invalid JSON in 'extra_attributes'.")
                    else: # If it's already a JSON object (dict/list)
                        instance_data['extra_attributes'] = attr_value


                # Use 'id' for update_or_create
                obj_id = instance_data.pop('id', None)

                if obj_id is not None: # If ID is provided, try to update
                    obj, created = self.model.objects.update_or_create(
                        pk=obj_id,
                        defaults=instance_data
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else: # If no ID, create a new object
                    self.model.objects.create(**instance_data)
                    created_count += 1
            except Exception as e:
                errors.append(f"Object {row_num + 1}: Error processing '{item_data_json}': {e}")

        context = {
            'message': f'Import completed. Created: {created_count}, Updated: {updated_count}.',
            'errors': errors
        }
        # Optionally redirect on success, otherwise render the same page with results
        # if not errors and created_count > 0 or updated_count > 0:
        #     return redirect(self.success_url_name)
        return render(request, self.template_name, context)

# --- Views for User Characters (Warrior, Mage) ---

class CharacterListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all characters (warriors and mages).
    Admins see all characters. Regular users see all characters.
    """
    template_name = 'characters/character_list.html'
    context_object_name = 'characters' # Este context_object_name ya no es solo 'characters' sino 'warriors' y 'mages'

    def get_queryset(self):
        # We don't need a specific queryset here since we're passing
        # warriors and mages separately in get_context_data.
        # This can return an empty queryset or any placeholder.
        return Warrior.objects.none() # Or Warrior.objects.all() if you want to use 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add ALL warriors and ALL mages to the context
        context['warriors'] = Warrior.objects.all() # <-- AHORA MUESTRA TODOS LOS GUERREROS
        context['mages'] = Mage.objects.all()       # <-- AHORA MUESTRA TODOS LOS MAGOS
        return context

class WarriorCreateView(LoginRequiredMixin, CreateView):
    model = Warrior
    form_class = WarriorForm
    template_name = 'characters/character_form.html'
    success_url = reverse_lazy('characters:character_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user # Assign the logged-in user as owner
        return super().form_valid(form)

class WarriorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Warrior
    form_class = WarriorForm
    template_name = 'characters/character_form.html'
    success_url = reverse_lazy('characters:character_list')

    def test_func(self):
        # Admins can update any warrior. Regular users can only update their own.
        warrior = self.get_object()
        return self.request.user.is_staff or warrior.owner == self.request.user

class WarriorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Warrior
    template_name = 'characters/character_confirm_delete.html'
    success_url = reverse_lazy('characters:character_list')

    def test_func(self):
        # Admins can delete any warrior. Regular users can only delete their own.
        warrior = self.get_object()
        return self.request.user.is_staff or warrior.owner == self.request.user

class MageCreateView(LoginRequiredMixin, CreateView):
    model = Mage
    form_class = MageForm
    template_name = 'characters/character_form.html'
    success_url = reverse_lazy('characters:character_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user # Assign the logged-in user as owner
        return super().form_valid(form)

class MageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mage
    form_class = MageForm
    template_name = 'characters/character_form.html'
    success_url = reverse_lazy('characters:character_list')

    def test_func(self):
        # Admins can update any mage. Regular users can only update their own.
        mage = self.get_object()
        return self.request.user.is_staff or mage.owner == self.request.user

class MageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mage
    template_name = 'characters/character_confirm_delete.html'
    success_url = reverse_lazy('characters:character_list')

    def test_func(self):
        # Admins can delete any mage. Regular users can only delete their own.
        mage = self.get_object()
        return self.request.user.is_staff or mage.owner == self.request.user

# --- Views for Enemies (Admin Only) ---

class EnemyListView(LoginRequiredMixin, ListView):
    model = Enemy
    template_name = 'characters/enemy_list.html'
    context_object_name = 'enemies'
    def get_queryset(self):
        # All enemies are visible to any logged-in user
        return Enemy.objects.all()

class EnemyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Enemy
    form_class = EnemyForm
    template_name = 'characters/enemy_form.html'
    success_url = reverse_lazy('characters:enemy_list')

    def test_func(self):
        # Only staff (admins) can create enemies
        return self.request.user.is_staff

class EnemyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Enemy
    form_class = EnemyForm
    template_name = 'characters/enemy_form.html'
    success_url = reverse_lazy('characters:enemy_list')

    def test_func(self):
        # Only staff (admins) can update enemies
        return self.request.user.is_staff

class EnemyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Enemy
    template_name = 'characters/enemy_confirm_delete.html'
    success_url = reverse_lazy('characters:enemy_list')

    def test_func(self):
        # Only staff (admins) can delete enemies
        return self.request.user.is_staff

# --- Views for Items (Admin Only) ---

class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'characters/item_list.html'
    context_object_name = 'items'
    def get_queryset(self):
        # Assume items are global and not owned
        return Item.objects.all()

class ItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'characters/item_form.html'
    success_url = reverse_lazy('characters:item_list')

    def test_func(self):
        # Only staff (admins) can create items
        return self.request.user.is_staff

class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'characters/item_form.html'
    success_url = reverse_lazy('characters:item_list')

    def test_func(self):
        # Only staff (admins) can update items
        return self.request.user.is_staff

class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item
    template_name = 'characters/item_confirm_delete.html'
    success_url = reverse_lazy('characters:item_list')

    def test_func(self):
        # Only staff (admins) can delete items
        return self.request.user.is_staff

# --- JSON Export/Import Views for each Model (Modificaciones para Warrior/Mage) ---

class WarriorExportView(JSONExportMixin):
    model = Warrior
    fields_to_export = ['id', 'name', 'health', 'damage', 'defense', 'owner_id'] # Export owner's ID
    filename = "warriors.json"

class WarriorImportView(JSONImportMixin):
    model = Warrior
    template_name = 'characters/generic_import.html' # Use the generic import template
    success_url_name = 'characters:character_list'
    fields_mapping = {
        'id': 'id',
        'name': 'name',
        'health': 'health',
        'damage': 'damage',
        'defense': 'defense',
        'owner_id': 'owner_id', # Se incluye para que el Mixin base lo maneje si es necesario
    }

    # Aquí es donde cambia la lógica de importación para Warrior/Mage
    def post(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return HttpResponse("You don't have permission to import data.", status=403)

        json_file = request.FILES.get('json_file')
        if not json_file:
            return render(request, self.template_name, {'error_message': 'No file selected.'})

        if not json_file.name.endswith('.json'):
            return render(request, self.template_name, {'error_message': 'The file must be a JSON file.'})

        try:
            file_data = json_file.read().decode('utf-8')
            data_list = json.loads(file_data)
        except json.JSONDecodeError as e:
            return render(request, self.template_name, {'error_message': f'Error reading JSON file: {e}'})
        except Exception as e:
            return render(request, self.template_name, {'error_message': f'Unexpected error processing file: {e}'})

        if not isinstance(data_list, list):
            return render(request, self.template_name, {'error_message': 'The JSON file must contain a list of objects.'})

        created_count = 0
        updated_count = 0
        errors = []

        for row_num, item_data_json in enumerate(data_list):
            try:
                instance_data = {}
                for json_key, model_field in self.fields_mapping.items():
                    if json_key in item_data_json:
                        if model_field.endswith('_id') and json_key == model_field:
                             instance_data[model_field] = item_data_json[json_key]
                        elif not model_field.endswith('_id'):
                            instance_data[model_field] = item_data_json[json_key]

                # Si el importador es un admin, puede importar con el owner_id del JSON
                # Si no hay owner_id en el JSON o el importador no es admin, asigna el owner al usuario logueado.
                # Esta es la lógica clave para permitir la flexibilidad.
                if self.request.user.is_staff and 'owner_id' in item_data_json:
                    # Intentamos obtener el usuario por owner_id
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        owner_obj = User.objects.get(pk=item_data_json['owner_id'])
                        instance_data['owner'] = owner_obj
                    except User.DoesNotExist:
                        errors.append(f"Object {row_num + 1}: Owner with ID {item_data_json['owner_id']} not found. Assigning to current admin.")
                        instance_data['owner'] = self.request.user # Asigna al admin si el owner original no existe
                else:
                    # Si no es admin, o si el JSON no tiene owner_id, asigna al usuario logueado
                    instance_data['owner'] = self.request.user

                obj_id = instance_data.pop('id', None)

                if obj_id is not None:
                    # Cuando un admin actualiza, puede actualizar cualquier personaje.
                    # Cuando un usuario normal actualiza, solo puede actualizar el suyo.
                    # update_or_create con `owner` en `defaults` si se asignó, o en `pk` si es el caso del admin.
                    if self.request.user.is_staff:
                        # Si es admin, puede actualizar por ID directamente, y defaults maneja el owner
                        obj, created = self.model.objects.update_or_create(
                            pk=obj_id,
                            defaults=instance_data
                        )
                    else:
                        # Si es un usuario normal, debe ser su personaje
                        obj, created = self.model.objects.update_or_create(
                            pk=obj_id,
                            owner=self.request.user, # Asegura que solo actualiza el suyo
                            defaults=instance_data
                        )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    self.model.objects.create(**instance_data)
                    created_count += 1
            except Exception as e:
                errors.append(f"Object {row_num + 1}: Error processing '{item_data_json}': {e}")

        context = {
            'message': f'Import completed. Created: {created_count}, Updated: {updated_count}.',
            'errors': errors
        }
        return render(request, self.template_name, context)

class MageExportView(JSONExportMixin):
    model = Mage
    fields_to_export = ['id', 'name', 'health', 'magic_damage', 'mana', 'defense', 'owner_id']
    filename = "mages.json"

class MageImportView(JSONImportMixin):
    model = Mage
    template_name = 'characters/generic_import.html' # Use the generic import template
    success_url_name = 'characters:character_list'
    fields_mapping = {
        'id': 'id',
        'name': 'name',
        'health': 'health',
        'magic_damage': 'magic_damage',
        'mana': 'mana',
        'defense': 'defense',
        'owner_id': 'owner_id',
    }

    # Aquí es donde cambia la lógica de importación para Warrior/Mage
    def post(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            return HttpResponse("You don't have permission to import data.", status=403)

        json_file = request.FILES.get('json_file')
        if not json_file:
            return render(request, self.template_name, {'error_message': 'No file selected.'})

        if not json_file.name.endswith('.json'):
            return render(request, self.template_name, {'error_message': 'The file must be a JSON file.'})

        try:
            file_data = json_file.read().decode('utf-8')
            data_list = json.loads(file_data)
        except json.JSONDecodeError as e:
            return render(request, self.template_name, {'error_message': f'Error reading JSON file: {e}'})
        except Exception as e:
            return render(request, self.template_name, {'error_message': f'Unexpected error processing file: {e}'})

        if not isinstance(data_list, list):
            return render(request, self.template_name, {'error_message': 'The JSON file must contain a list of objects.'})

        created_count = 0
        updated_count = 0
        errors = []

        for row_num, item_data_json in enumerate(data_list):
            try:
                instance_data = {}
                for json_key, model_field in self.fields_mapping.items():
                    if json_key in item_data_json:
                        if model_field.endswith('_id') and json_key == model_field:
                             instance_data[model_field] = item_data_json[json_key]
                        elif not model_field.endswith('_id'):
                            instance_data[model_field] = item_data_json[json_key]

                # Lógica para asignar el owner:
                if self.request.user.is_staff and 'owner_id' in item_data_json:
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        owner_obj = User.objects.get(pk=item_data_json['owner_id'])
                        instance_data['owner'] = owner_obj
                    except User.DoesNotExist:
                        errors.append(f"Object {row_num + 1}: Owner with ID {item_data_json['owner_id']} not found. Assigning to current admin.")
                        instance_data['owner'] = self.request.user # Asigna al admin si el owner original no existe
                else:
                    instance_data['owner'] = self.request.user

                obj_id = instance_data.pop('id', None)

                if obj_id is not None:
                    if self.request.user.is_staff:
                        obj, created = self.model.objects.update_or_create(
                            pk=obj_id,
                            defaults=instance_data
                        )
                    else:
                        obj, created = self.model.objects.update_or_create(
                            pk=obj_id,
                            owner=self.request.user,
                            defaults=instance_data
                        )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    self.model.objects.create(**instance_data)
                    created_count += 1
            except Exception as e:
                errors.append(f"Object {row_num + 1}: Error processing '{item_data_json}': {e}")

        context = {
            'message': f'Import completed. Created: {created_count}, Updated: {updated_count}.',
            'errors': errors
        }
        return render(request, self.template_name, context)


class EnemyExportView(JSONExportMixin):
    model = Enemy
    fields_to_export = ['id', 'name', 'health', 'attack', 'defense']
    filename = "enemies.json"

class EnemyImportView(JSONImportMixin):
    model = Enemy
    template_name = 'characters/generic_import.html' # Use the generic import template
    success_url_name = 'characters:enemy_list'
    fields_mapping = {
        'id': 'id',
        'name': 'name',
        'health': 'health',
        'attack': 'attack',
        'defense': 'defense',
    }

class ItemExportView(JSONExportMixin):
    model = Item
    fields_to_export = ['id', 'name', 'item_type', 'description', 'value',
                         'damage_buff', 'health_restore', 'mana_restore', 'extra_attributes']
    filename = "items.json" # Changed to .json

class ItemImportView(JSONImportMixin):
    model = Item
    template_name = 'characters/generic_import.html' # You can use generic_import.html if you want
    success_url_name = 'characters:item_list'
    fields_mapping = {
        'id': 'id',
        'name': 'name',
        'item_type': 'item_type',
        'description': 'description',
        'value': 'value',
        'damage_buff': 'damage_buff',
        'health_restore': 'health_restore',
        'mana_restore': 'mana_restore',
        'extra_attributes': 'extra_attributes'
    }