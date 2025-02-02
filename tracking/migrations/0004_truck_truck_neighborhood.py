# Generated by Django 5.1.3 on 2024-11-23 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0003_rename_truck_id_driver_truck_route_end_postcode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='truck',
            name='truck_neighborhood',
            field=models.CharField(choices=[('Adrianópolis', 'Adrianópolis'), ('Aleixo', 'Aleixo'), ('Alvorada', 'Alvorada'), ('Armando Mendes', 'Armando Mendes'), ('Betânia', 'Betânia'), ('Cachoeirinha', 'Cachoeirinha'), ('Centro', 'Centro'), ('Chapada', 'Chapada'), ('Cidade de Deus', 'Cidade de Deus'), ('Cidade Nova', 'Cidade Nova'), ('Colônia Antônio Aleixo', 'Colônia Antônio Aleixo'), ('Colônia Oliveira Machado', 'Colônia Oliveira Machado'), ('Colônia Santo Antônio', 'Colônia Santo Antônio'), ('Colônia Terra Nova', 'Colônia Terra Nova'), ('Compensa', 'Compensa'), ('Coroado', 'Coroado'), ('Crespo', 'Crespo'), ('Da Paz', 'Da Paz'), ('Distrito Industrial I', 'Distrito Industrial I'), ('Distrito Industrial II', 'Distrito Industrial II'), ('Dom Pedro', 'Dom Pedro'), ('Educandos', 'Educandos'), ('Flores', 'Flores'), ('Gilberto Mestrinho', 'Gilberto Mestrinho'), ('Glória', 'Glória'), ('Japiim', 'Japiim'), ('Jorge Teixeira', 'Jorge Teixeira'), ('Lago Azul', 'Lago Azul'), ('Lírio do Vale', 'Lírio do Vale'), ('Mauazinho', 'Mauazinho'), ('Monte das Oliveiras', 'Monte das Oliveiras'), ('Morro da Liberdade', 'Morro da Liberdade'), ('Nossa Senhora Aparecida', 'Nossa Senhora Aparecida'), ('Nossa Senhora das Graças', 'Nossa Senhora das Graças'), ('Nova Cidade', 'Nova Cidade'), ('Nova Esperança', 'Nova Esperança'), ('Novo Aleixo', 'Novo Aleixo'), ('Novo Israel', 'Novo Israel'), ('Parque 10 de Novembro', 'Parque 10 de Novembro'), ('Petrópolis', 'Petrópolis'), ('Planalto', 'Planalto'), ('Ponta Negra', 'Ponta Negra'), ('Praça 14 de Janeiro', 'Praça 14 de Janeiro'), ('Presidente Vargas', 'Presidente Vargas'), ('Puraquequara', 'Puraquequara'), ('Raiz', 'Raiz'), ('Redenção', 'Redenção'), ('Santa Etelvina', 'Santa Etelvina'), ('Santa Luzia', 'Santa Luzia'), ('Santo Agostinho', 'Santo Agostinho'), ('Santo Antônio', 'Santo Antônio'), ('São Francisco', 'São Francisco'), ('São Geraldo', 'São Geraldo'), ('São Jorge', 'São Jorge'), ('São José Operário', 'São José Operário'), ('São Lázaro', 'São Lázaro'), ('São Raimundo', 'São Raimundo'), ('Tancredo Neves', 'Tancredo Neves'), ('Tarumã', 'Tarumã'), ('Tarumã-Açu', 'Tarumã-Açu'), ('Vila Buriti', 'Vila Buriti'), ('Vila da Prata', 'Vila da Prata'), ('Zumbi dos Palmares', 'Zumbi dos Palmares')], default='default', max_length=50),
        ),
    ]
