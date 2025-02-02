# veiculos/admin.py
from django.contrib import admin
from .models import Truck, Driver, TruckLocation, Route, RouteLocation, DiscardLocation

# Customizando a visualização do modelo Truck
class TruckAdmin(admin.ModelAdmin):
    list_display = ('truck_id', 'model', 'plate')  # Campos exibidos na lista de caminhões
    search_fields = ('truck_id', 'plate')  # Campos pesquisáveis
    list_filter = ('model',)  # Filtro por modelo

# Customizando a visualização do modelo Driver
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'truck_id', 'cpf', 'birth_date')  # Campos exibidos na lista de motoristas
    search_fields = ('name', 'cpf')  # Campos pesquisáveis
    list_filter = ('truck_id',)  # Filtro por caminhão

    def save_model(self, request, obj, form, change):
        """
        Override do método save_model para garantir que a senha do motorista seja salva de forma segura.
        Aqui, podemos implementar a lógica para criptografar a senha, se necessário.
        """
        if obj.password:
            # Aqui você pode criptografar a senha, se necessário.
            pass  # Deixe isso vazio ou implemente a criptografia.
        super().save_model(request, obj, form, change)

# Customizando a visualização do modelo TruckLocation
class TruckLocationAdmin(admin.ModelAdmin):
    list_display = ('truck', 'latitude', 'longitude', 'address', 'postcode', 'updated_at')  # Campos exibidos na lista de localizações
    search_fields = ('truck__truck_id',)  # Pesquisa pelo ID do caminhão
    list_filter = ('truck',)  # Filtro por caminhão

# Inline para mostrar as localizações da rota dentro do formulário da rota
class RouteLocationInline(admin.TabularInline):
    model = RouteLocation
    extra = 1  # Número de campos em branco para adicionar novas localizações

# Customizando a visualização do modelo Route
class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_id', 'truck', 'route_neighborhood', 'start_address', 'end_address', 'created_at', 'updated_at')  # Campos exibidos na lista de rotas
    search_fields = ('route_id', 'truck__truck_id')  # Pesquisa pelo ID da rota e pelo ID do caminhão
    list_filter = ('truck', 'created_at', 'updated_at')  # Filtro por caminhão, data de criação e atualização
    inlines = [RouteLocationInline]  # Adicionando o inline das localizações

# Customizando a visualização do modelo RouteLocation
class RouteLocationAdmin(admin.ModelAdmin):
    list_display = ('route', 'latitude', 'longitude', 'address', 'order')  # Campos exibidos na lista de localizações de rotas
    search_fields = ('route__route_id', 'address')  # Pesquisa pelo ID da rota e pelo endereço
    list_filter = ('route', 'order')  # Filtro por rota e ordem


class DiscardLocationAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista no admin
    list_display = ('name', 'neighborhood', 'content_types', 'latitude', 'longitude', 'created_at', 'updated_at')
    
    # Campos para busca
    search_fields = ('name', 'neighborhood', 'address', 'content_types')
    
    # Filtros laterais
    list_filter = ('neighborhood', 'content_types', 'created_at', 'updated_at')
    
    # Campos para edição no modo inline
    fields = ('name', 'latitude', 'longitude', 'address', 'neighborhood', 'content_types')
    
    # Ordem padrão
    ordering = ['neighborhood', 'name']
    
    # Campos que são somente leitura
    readonly_fields = ('created_at', 'updated_at')

    # Configurações avançadas (caso você queira exportar ou usar ações específicas)
    actions = ['mark_as_updated']
    
    # Ações personalizadas
    def mark_as_updated(self, request, queryset):
        queryset.update(updated_at=None)  # Exemplo de ação personalizada
        self.message_user(request, f"{queryset.count()} locais marcados como atualizados.")
    mark_as_updated.short_description = "Marcar como atualizado"

# Registrando os modelos no admin
admin.site.register(Truck, TruckAdmin) 
admin.site.register(Driver, DriverAdmin)
admin.site.register(TruckLocation, TruckLocationAdmin) 
admin.site.register(Route, RouteAdmin)
admin.site.register(RouteLocation, RouteLocationAdmin)
admin.site.register(DiscardLocation, DiscardLocationAdmin)
