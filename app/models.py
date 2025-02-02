from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Truck(models.Model):
    TRUCK_NEIGHBORHOODS = [
        ('Adrianópolis', 'Adrianópolis'),
        ('Aleixo', 'Aleixo'),
        ('Alvorada', 'Alvorada'),
        ('Armando Mendes', 'Armando Mendes'),
        ('Betânia', 'Betânia'),
        ('Cachoeirinha', 'Cachoeirinha'),
        ('Centro', 'Centro'),
        ('Chapada', 'Chapada'),
        ('Cidade de Deus', 'Cidade de Deus'),
        ('Cidade Nova', 'Cidade Nova'),
        ('Colônia Antônio Aleixo', 'Colônia Antônio Aleixo'),
        ('Colônia Oliveira Machado', 'Colônia Oliveira Machado'),
        ('Colônia Santo Antônio', 'Colônia Santo Antônio'),
        ('Colônia Terra Nova', 'Colônia Terra Nova'),
        ('Compensa', 'Compensa'),
        ('Coroado', 'Coroado'),
        ('Crespo', 'Crespo'),
        ('Da Paz', 'Da Paz'),
        ('Distrito Industrial I', 'Distrito Industrial I'),
        ('Distrito Industrial II', 'Distrito Industrial II'),
        ('Dom Pedro', 'Dom Pedro'),
        ('Educandos', 'Educandos'),
        ('Flores', 'Flores'),
        ('Gilberto Mestrinho', 'Gilberto Mestrinho'),
        ('Glória', 'Glória'),
        ('Japiim', 'Japiim'),
        ('Jorge Teixeira', 'Jorge Teixeira'),
        ('Lago Azul', 'Lago Azul'),
        ('Lírio do Vale', 'Lírio do Vale'),
        ('Mauazinho', 'Mauazinho'),
        ('Monte das Oliveiras', 'Monte das Oliveiras'),
        ('Morro da Liberdade', 'Morro da Liberdade'),
        ('Nossa Senhora Aparecida', 'Nossa Senhora Aparecida'),
        ('Nossa Senhora das Graças', 'Nossa Senhora das Graças'),
        ('Nova Cidade', 'Nova Cidade'),
        ('Nova Esperança', 'Nova Esperança'),
        ('Novo Aleixo', 'Novo Aleixo'),
        ('Novo Israel', 'Novo Israel'),
        ('Parque 10 de Novembro', 'Parque 10 de Novembro'),
        ('Petrópolis', 'Petrópolis'),
        ('Planalto', 'Planalto'),
        ('Ponta Negra', 'Ponta Negra'),
        ('Praça 14 de Janeiro', 'Praça 14 de Janeiro'),
        ('Presidente Vargas', 'Presidente Vargas'),
        ('Puraquequara', 'Puraquequara'),
        ('Raiz', 'Raiz'),
        ('Redenção', 'Redenção'),
        ('Santa Etelvina', 'Santa Etelvina'),
        ('Santa Luzia', 'Santa Luzia'),
        ('Santo Agostinho', 'Santo Agostinho'),
        ('Santo Antônio', 'Santo Antônio'),
        ('São Francisco', 'São Francisco'),
        ('São Geraldo', 'São Geraldo'),
        ('São Jorge', 'São Jorge'),
        ('São José Operário', 'São José Operário'),
        ('São Lázaro', 'São Lázaro'),
        ('São Raimundo', 'São Raimundo'),
        ('Tancredo Neves', 'Tancredo Neves'),
        ('Tarumã', 'Tarumã'),
        ('Tarumã-Açu', 'Tarumã-Açu'),
        ('Vila Buriti', 'Vila Buriti'),
        ('Vila da Prata', 'Vila da Prata'),
        ('Zumbi dos Palmares', 'Zumbi dos Palmares'),
    ]

    truck_id = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=100)
    plate = models.CharField(max_length=10, unique=True)
    truck_neighborhood = models.CharField(
        max_length=50,
        choices=TRUCK_NEIGHBORHOODS,
        default='default',  # Valor padrão
    )

    def __str__(self):
        return self.truck_id


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Hash it in production
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True)

    def __str__(self):
        return self.name


class TruckLocation(models.Model):
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255, blank=True, null=True)  # Adicionado para integrar com Nominatim
    postcode = models.CharField(max_length=10, blank=True, null=True)  # CEP da localização
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Location of {self.truck.truck_id}"



## Refatorar para modular esse código em um módulo chamado Route Management
class Route(models.Model):

    ROUTE_NEIGHBORHOODS = [
        ('Adrianópolis', 'Adrianópolis'),
        ('Aleixo', 'Aleixo'),
        ('Alvorada', 'Alvorada'),
        ('Armando Mendes', 'Armando Mendes'),
        ('Betânia', 'Betânia'),
        ('Cachoeirinha', 'Cachoeirinha'),
        ('Centro', 'Centro'),
        ('Chapada', 'Chapada'),
        ('Cidade de Deus', 'Cidade de Deus'),
        ('Cidade Nova', 'Cidade Nova'),
        ('Colônia Antônio Aleixo', 'Colônia Antônio Aleixo'),
        ('Colônia Oliveira Machado', 'Colônia Oliveira Machado'),
        ('Colônia Santo Antônio', 'Colônia Santo Antônio'),
        ('Colônia Terra Nova', 'Colônia Terra Nova'),
        ('Compensa', 'Compensa'),
        ('Coroado', 'Coroado'),
        ('Crespo', 'Crespo'),
        ('Da Paz', 'Da Paz'),
        ('Distrito Industrial I', 'Distrito Industrial I'),
        ('Distrito Industrial II', 'Distrito Industrial II'),
        ('Dom Pedro', 'Dom Pedro'),
        ('Educandos', 'Educandos'),
        ('Flores', 'Flores'),
        ('Gilberto Mestrinho', 'Gilberto Mestrinho'),
        ('Glória', 'Glória'),
        ('Japiim', 'Japiim'),
        ('Jorge Teixeira', 'Jorge Teixeira'),
        ('Lago Azul', 'Lago Azul'),
        ('Lírio do Vale', 'Lírio do Vale'),
        ('Mauazinho', 'Mauazinho'),
        ('Monte das Oliveiras', 'Monte das Oliveiras'),
        ('Morro da Liberdade', 'Morro da Liberdade'),
        ('Nossa Senhora Aparecida', 'Nossa Senhora Aparecida'),
        ('Nossa Senhora das Graças', 'Nossa Senhora das Graças'),
        ('Nova Cidade', 'Nova Cidade'),
        ('Nova Esperança', 'Nova Esperança'),
        ('Novo Aleixo', 'Novo Aleixo'),
        ('Novo Israel', 'Novo Israel'),
        ('Parque 10 de Novembro', 'Parque 10 de Novembro'),
        ('Petrópolis', 'Petrópolis'),
        ('Planalto', 'Planalto'),
        ('Ponta Negra', 'Ponta Negra'),
        ('Praça 14 de Janeiro', 'Praça 14 de Janeiro'),
        ('Presidente Vargas', 'Presidente Vargas'),
        ('Puraquequara', 'Puraquequara'),
        ('Raiz', 'Raiz'),
        ('Redenção', 'Redenção'),
        ('Santa Etelvina', 'Santa Etelvina'),
        ('Santa Luzia', 'Santa Luzia'),
        ('Santo Agostinho', 'Santo Agostinho'),
        ('Santo Antônio', 'Santo Antônio'),
        ('São Francisco', 'São Francisco'),
        ('São Geraldo', 'São Geraldo'),
        ('São Jorge', 'São Jorge'),
        ('São José Operário', 'São José Operário'),
        ('São Lázaro', 'São Lázaro'),
        ('São Raimundo', 'São Raimundo'),
        ('Tancredo Neves', 'Tancredo Neves'),
        ('Tarumã', 'Tarumã'),
        ('Tarumã-Açu', 'Tarumã-Açu'),
        ('Vila Buriti', 'Vila Buriti'),
        ('Vila da Prata', 'Vila da Prata'),
        ('Zumbi dos Palmares', 'Zumbi dos Palmares'),
    ]

    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)  # Relaciona a rota ao caminhão
    route_id = models.CharField(max_length=50, unique=True)  # ID único para a rota
    route_neighborhood = models.CharField(
        max_length=50,
        choices=ROUTE_NEIGHBORHOODS,
        default='default',  # Valor padrão
    )
    start_address = models.CharField(max_length=255)  # Endereço inicial da rota
    start_postcode = models.CharField(max_length=10, blank=True, null=True)  # CEP do endereço inicial
    end_address = models.CharField(max_length=255)  # Endereço final da rota
    end_postcode = models.CharField(max_length=10, blank=True, null=True)  # CEP do endereço final
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação da rota
    updated_at = models.DateTimeField(auto_now=True)  # Data de atualização

    def __str__(self):
        return f"Route {self.route_id} for Truck {self.truck.truck_id}"


class RouteLocation(models.Model):
    route = models.ForeignKey(Route, related_name='locations', on_delete=models.CASCADE)  # Relaciona com a rota
    address = models.CharField(max_length=255)  # Endereço associado ao ponto
    postcode = models.CharField(max_length=10, blank=True, null=True)  # CEP do ponto
    latitude = models.FloatField(blank=True, null=True)  # Latitude do ponto (opcional)
    longitude = models.FloatField(blank=True, null=True)  # Longitude do ponto (opcional)
    order = models.IntegerField()  # A ordem dos pontos na rota
    passage_time = models.TimeField(default=timezone.now, blank=False)  # Horário de passagem obrigatório

    def __str__(self):
        return f"Location {self.order} of Route {self.route.route_id}"

## Refatorar para modular esse código em um módulo chamado 
class DiscardLocation(models.Model):
    LOCATION_CONTENT_TYPES = [
    ('organic', 'Orgânicos'),  # Restos de alimentos, folhas, e resíduos biodegradáveis.
    ('recyclables', 'Recicláveis'),  # Inclui plásticos, papéis, metais e vidros.
    ('electronics', 'Eletrônicos'),  # Aparelhos eletrônicos, baterias e dispositivos.
    ('hazardous', 'Perigosos'),  # Produtos químicos, pilhas, medicamentos vencidos.
    ('construction', 'Resíduos de Construção e Demolição'),  # Tijolos, cimento, madeira.
    ('textile', 'Têxteis'),  # Roupas, tecidos e retalhos.
    ('green', 'Resíduos Verdes'),  # Podas, folhas e resíduos de jardinagem.
    ('non_recyclable', 'Não Recicláveis'),  # Fraldas, absorventes e papéis engordurados.
    ('oil', 'Óleo e Gorduras'),  # Óleo de cozinha usado e gorduras.
    ('other', 'Outros'),  # Tipos não categorizados.
    ]

    DISCARDLOCATIONS_NEIGHBORHOODS = [
        ('Adrianópolis', 'Adrianópolis'),
        ('Aleixo', 'Aleixo'),
        ('Alvorada', 'Alvorada'),
        ('Armando Mendes', 'Armando Mendes'),
        ('Betânia', 'Betânia'),
        ('Cachoeirinha', 'Cachoeirinha'),
        ('Centro', 'Centro'),
        ('Chapada', 'Chapada'),
        ('Cidade de Deus', 'Cidade de Deus'),
        ('Cidade Nova', 'Cidade Nova'),
        ('Colônia Antônio Aleixo', 'Colônia Antônio Aleixo'),
        ('Colônia Oliveira Machado', 'Colônia Oliveira Machado'),
        ('Colônia Santo Antônio', 'Colônia Santo Antônio'),
        ('Colônia Terra Nova', 'Colônia Terra Nova'),
        ('Compensa', 'Compensa'),
        ('Coroado', 'Coroado'),
        ('Crespo', 'Crespo'),
        ('Da Paz', 'Da Paz'),
        ('Distrito Industrial I', 'Distrito Industrial I'),
        ('Distrito Industrial II', 'Distrito Industrial II'),
        ('Dom Pedro', 'Dom Pedro'),
        ('Educandos', 'Educandos'),
        ('Flores', 'Flores'),
        ('Gilberto Mestrinho', 'Gilberto Mestrinho'),
        ('Glória', 'Glória'),
        ('Japiim', 'Japiim'),
        ('Jorge Teixeira', 'Jorge Teixeira'),
        ('Lago Azul', 'Lago Azul'),
        ('Lírio do Vale', 'Lírio do Vale'),
        ('Mauazinho', 'Mauazinho'),
        ('Monte das Oliveiras', 'Monte das Oliveiras'),
        ('Morro da Liberdade', 'Morro da Liberdade'),
        ('Nossa Senhora Aparecida', 'Nossa Senhora Aparecida'),
        ('Nossa Senhora das Graças', 'Nossa Senhora das Graças'),
        ('Nova Cidade', 'Nova Cidade'),
        ('Nova Esperança', 'Nova Esperança'),
        ('Novo Aleixo', 'Novo Aleixo'),
        ('Novo Israel', 'Novo Israel'),
        ('Parque 10 de Novembro', 'Parque 10 de Novembro'),
        ('Petrópolis', 'Petrópolis'),
        ('Planalto', 'Planalto'),
        ('Ponta Negra', 'Ponta Negra'),
        ('Praça 14 de Janeiro', 'Praça 14 de Janeiro'),
        ('Presidente Vargas', 'Presidente Vargas'),
        ('Puraquequara', 'Puraquequara'),
        ('Raiz', 'Raiz'),
        ('Redenção', 'Redenção'),
        ('Santa Etelvina', 'Santa Etelvina'),
        ('Santa Luzia', 'Santa Luzia'),
        ('Santo Agostinho', 'Santo Agostinho'),
        ('Santo Antônio', 'Santo Antônio'),
        ('São Francisco', 'São Francisco'),
        ('São Geraldo', 'São Geraldo'),
        ('São Jorge', 'São Jorge'),
        ('São José Operário', 'São José Operário'),
        ('São Lázaro', 'São Lázaro'),
        ('São Raimundo', 'São Raimundo'),
        ('Tancredo Neves', 'Tancredo Neves'),
        ('Tarumã', 'Tarumã'),
        ('Tarumã-Açu', 'Tarumã-Açu'),
        ('Vila Buriti', 'Vila Buriti'),
        ('Vila da Prata', 'Vila da Prata'),
        ('Zumbi dos Palmares', 'Zumbi dos Palmares'),
    ]
    
    name = models.CharField(max_length=100, help_text="Nome do local de descarte")  # Nome do local de descarte
    latitude = models.CharField(max_length=100, help_text="Latitude do local de descarte")  # Coordenada de latitude
    longitude = models.CharField(max_length=100, help_text="Longitude do local de descarte")  # Coordenada de longitude
    address = models.CharField(max_length=255, help_text="Endereço do local de descarte")  # Endereço completo
    neighborhood = models.CharField(
        max_length=50,
        choices= DISCARDLOCATIONS_NEIGHBORHOODS,
        default='default',  # Valor padrão
    )
    content_types = models.CharField(
        max_length=50,
        choices= LOCATION_CONTENT_TYPES,
        default='default',  # Valor padrão
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data de criação do local de descarte")  # Data de criação
    updated_at = models.DateTimeField(auto_now=True, help_text="Data de última atualização do local de descarte")  # Data de última atualização

    class Meta:
        verbose_name = "Discard Location"
        verbose_name_plural = "Discard Locations"
        ordering = ['neighborhood', 'name']  # Ordenação padrão por bairro e nome

    def __str__(self):
        return f"{self.name} - {self.neighborhood}"
