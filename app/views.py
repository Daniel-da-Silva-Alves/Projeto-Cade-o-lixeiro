from .models import Driver, Truck, TruckLocation, Route, RouteLocation, DiscardLocation
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Max
import json
import requests
import time



#Url para a api do Nominatim
NOMINATIM_URL_REVERSE = "https://nominatim.openstreetmap.org/reverse"
NOMINATIM_URL_SEARCH = "https://nominatim.openstreetmap.org/search"

# Lógica de autenticação do Motorista
def login_view(request):
    if request.method == 'POST':
        # Obter dados enviados pelo frontend via AJAX
        try:
            data = json.loads(request.body)
            truck_id = data.get('truck_id')
            username = data.get('username')
            password = data.get('password')
        except KeyError:
            return JsonResponse({'success': False, 'message': 'Dados inválidos.'}, status=400)

        # Verificar se o motorista com o truck_id e username existe
        try:
            driver = Driver.objects.get(name=username, truck_id__truck_id=truck_id)
        except Driver.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Motorista ou caminhão não encontrados.'}, status=404)

        # Verificar se a senha está correta (comparando senha criptografada)
        if driver.password == password:  # Alterar para o uso de senha criptografada
            # Usando Django's check_password() para validar a senha
            if driver.user.check_password(password):  # Se a senha estiver correta
                # Autenticar o motorista no Django
                login(request, driver.user)

                return JsonResponse({'success': True, 'message': 'Login bem-sucedido!'}, status=200)
            else:
                return JsonResponse({'success': False, 'message': 'Credenciais inválidas.'}, status=401)

        else:
            return JsonResponse({'success': False, 'message': 'Credenciais inválidas.'}, status=401)

    return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

# Lógica de logout do usuário
def logout_view(request):
    logout(request)
    return redirect('home')

# Renderiza a página inicial do sistema
def home(request):
    return render(request, 'index.html')

# Função que busca o bairro a partir das coordenadas
def get_neighborhood_from_coordinates(latitude, longitude):
    try:
        # Espera de 1 segundo entre as requisições (para não sobrecarregar a API)
        time.sleep(1)

        # Cabeçalhos personalizados para identificar a aplicação
        headers = {'User-Agent': 'Cadê o Lixeiro/1.0 (domhnalprofissional@gmail.com)'}
        
        # Requisição para a API Nominatim para obter o endereço completo
        response = requests.get(
            NOMINATIM_URL_REVERSE,
            headers=headers,  # Incluindo o cabeçalho com o User-Agent
            params={'lat': latitude, 'lon': longitude, 'format': 'json'}
        )
        
        response.raise_for_status()  # Garante que a requisição foi bem-sucedida
        
        # Obter os dados da resposta
        data = response.json()
        
        # Tentar extrair o bairro da resposta, que geralmente está no campo 'suburb'
        address = data.get('address', {})
        neighborhood = address.get('suburb', None)
        
        # Caso o bairro não seja encontrado, retornar None
        if not neighborhood:
            return None
        return neighborhood
    except requests.RequestException as e:
        # Se houver um erro na requisição, logar o erro e retornar None
        print(f"Erro na requisição Nominatim: {e}")
        return None

# Função que busca os caminhões por bairro
def get_truck_locations(request):
    # Obter o bairro selecionado
    neighborhood = request.GET.get('neighborhood', 'todos')

    # Filtrar os caminhões com base no bairro
    if neighborhood != 'todos':
        trucks = Truck.objects.filter(truck_neighborhood=neighborhood)
    else:
        trucks = Truck.objects.all()

    # Obter a última localização de cada caminhão
    truck_locations = []
    for truck in trucks:
        last_location = TruckLocation.objects.filter(truck=truck).order_by('-updated_at').first()
        if last_location:
            truck_locations.append({
                'truck_id': truck.truck_id,
                'latitude': last_location.latitude,
                'longitude': last_location.longitude,
                'address': last_location.address,
                'last_updated': last_location.updated_at.strftime('%Y-%m-%d %H:%M:%S')  # Formato de data de atualização
            })

    return JsonResponse(truck_locations, safe=False)
@csrf_protect
def locate_trucks_in_neighborhood(request):
    if request.method == 'POST':
        # Parse os dados do corpo da requisição
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Obter o bairro a partir das coordenadas
        neighborhood = get_neighborhood_from_coordinates(latitude, longitude)

        if not neighborhood:
            return JsonResponse({
                'success': False,
                'message': 'Unable to determine the neighborhood from the provided coordinates.'
            })
        
        # Filtrar caminhões que atendem ao bairro identificado
        trucks_in_neighborhood = Truck.objects.filter(truck_neighborhood=neighborhood)
        
        if not trucks_in_neighborhood.exists():
            return JsonResponse({
                'success': False,
                'message': 'No trucks found in your neighborhood.'
            })

        # Obter apenas a última localização enviada por cada caminhão
        latest_locations = (
            TruckLocation.objects.filter(truck__in=trucks_in_neighborhood)
            .values('truck_id')  # Agrupar por caminhão
            .annotate(last_updated=Max('updated_at'))  # Obter a última atualização por caminhão
            .order_by('-last_updated')  # Ordenar pelas localizações mais recentes
        )

        # Preparar a resposta
        trucks = []
        for location in latest_locations:
            truck_location = TruckLocation.objects.get(
                truck_id=location['truck_id'], 
                updated_at=location['last_updated']
            )
            trucks.append({
                "truck_id": truck_location.truck.truck_id,
                "latitude": truck_location.latitude,
                "longitude": truck_location.longitude,
                "last_updated": truck_location.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                "address": truck_location.address,
            })

        return JsonResponse({
            'success': True,
            'trucks': trucks
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=400)


# Renderiza a página principal do sistema de rastreamento
@login_required
def tracking_interface(request):
    return render(request, "tracking.html")

# Função auxiliar que converte coordenadas em endereço
@csrf_exempt
def get_address_from_coordinates(latitude, longitude):
    time.sleep(1)  # Aguarda 1 segundo entre requisições
    headers = {'User-Agent': 'Cadê o Lixeiro/1.0 (domhnalprofissional@gmail.com)'}
    params = {'lat': latitude, 'lon': longitude, 'format': 'json'}
    response = requests.get(NOMINATIM_URL_REVERSE, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json().get('display_name', 'Endereço não disponível')
    else:
        return 'Erro ao buscar endereço'

# Função auxiliar que converte endereço em cep
@csrf_exempt
def get_postcode_from_address(address):
    """
    Utiliza a API do Nominatim para buscar o código postal (postcode) a partir de um endereço.
    """
    try:
        # Define os parâmetros da consulta
        params = {
            'q': address,  # Endereço para consulta
            'format': 'json',  # Retorno no formato JSON
            'addressdetails': 1  # Inclui detalhes do endereço
        }
        
        # Define o cabeçalho com o identificador da aplicação
        headers = {
            'User-Agent': 'SeuApp/1.0 (seuemail@exemplo.com)'  # Substitua pelo nome e contato da sua aplicação
        }
        
        # Faz a requisição
        response = requests.get(NOMINATIM_URL_SEARCH, params=params, headers=headers)
        
        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            results = response.json()
            if results:  # Verifica se há resultados
                # Tenta acessar o postcode no primeiro resultado
                return results[0].get('address', {}).get('postcode', "Código postal não disponível")
            else:
                return "Nenhum resultado encontrado"
        else:
            return f"Erro ao buscar código postal: {response.status_code}"
    
    except Exception as e:
        return f"Erro ao conectar à API: {e}"

# Função que atualiza os dados de localização do veículo no banco de dados
@login_required # Garante que o motorista esteja autenticado
def update_truck_location(request):
    """Atualiza a localização de um caminhão, associando-a ao motorista logado"""
    if request.method == 'POST':
        # Dados recebidos do front-end
        dados = json.loads(request.body)
        latitude = dados.get('latitude')
        longitude = dados.get('longitude')

        if not latitude or not longitude:
            return JsonResponse({'status': 'erro', 'mensagem': 'Coordenadas não fornecidas'}, status=400)

        # Obtém o motorista logado
        driver = request.user.driver  # Supondo que o usuário logado seja um Driver

        # Verifica se o motorista tem um caminhão associado
        try:
            truck = driver.truck
        except Truck.DoesNotExist:
            return JsonResponse({'status': 'erro', 'mensagem': 'Caminhão não encontrado'}, status=404)

        # Converte as coordenadas em um endereço completo
        address = get_address_from_coordinates(latitude, longitude)
        postcode = get_postcode_from_address(address)

        # Armazena a localização no banco de dados
        truck_location = TruckLocation.objects.create(
            truck=truck,  # Associa a localização ao caminhão
            latitude=latitude,
            longitude=longitude,
            address=address,
            postcode=postcode
        )

        return JsonResponse({'status': 'sucesso', 'latitude': latitude, 'longitude': longitude, 'address': address})

    return JsonResponse({'status': 'erro', 'mensagem': 'Método não permitido'}, status=405)

# Função que envia dados para o front para atualizar a Legend de Informações de Rastreamento
@login_required
def get_tracking_info_for_user(request):
    user = request.user

    try:
        # Obtenha o driver e o caminhão associado ao usuário autenticado
        driver = Driver.objects.get(user=user)
        truck = driver.truck

        if not truck:
            return JsonResponse({'success': False, 'message': 'O motorista não tem caminhão associado.'})

        # Obtenha a última localização do caminhão
        last_location = TruckLocation.objects.filter(truck=truck).order_by('-updated_at').first()

        if not last_location:
            return JsonResponse({'success': False, 'message': 'Nenhuma localização disponível para o caminhão.'})

        # Retorne os dados como JSON
        return JsonResponse({
            'success': True,
            'data': {
                'driver_name': driver.name,
                'truck_id': truck.truck_id,
                'timestamp': last_location.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        })
    except Driver.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Motorista não encontrado para o usuário.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro interno: {str(e)}'})


# Envia as rotas do Caminhão para o motorista
@login_required
def get_route_locations(request):
    # Obtém o motorista logado
    driver = Driver.objects.get(user=request.user)
    
    # Obtém o caminhão associado ao motorista
    truck = driver.truck

    try:
        # Busca a rota associada ao caminhão
        route = Route.objects.get(truck=truck)
    except Route.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No route found for this truck.'})

    # Obtém as localizações da rota
    route_locations = RouteLocation.objects.filter(route=route).order_by('order')

    # Serializa os dados das localizações
    locations_data = [
        {
            'order': location.order,
            'address': location.address,
            'latitude': location.latitude,
            'longitude': location.longitude
        }
        for location in route_locations
    ]

    # Retorna os dados como JSON
    return JsonResponse({'status': 'success', 'locations': locations_data})


# Renderiza a página de horários de passagem
def passage_times(request):
    return render(request, 'passage_times.html')


def fetch_routes_by_neighborhood(request):
    if request.method == 'POST':
        try:
            # Carrega os bairros enviados no corpo da requisição
            data = json.loads(request.body)
            bairros = data.get('bairros', [])

            # Verifica se a lista de bairros foi enviada
            if not bairros:
                return JsonResponse({'error': 'Nenhum bairro selecionado'}, status=400)

            # Filtra as rotas com base nos bairros fornecidos
            routes = Route.objects.filter(route_neighborhood__in=bairros)

            
            # Cria a lista com os dados das rotas
            routes_data = [{
                'route_id': route.id,
                'start_address': route.start_address,
                'end_address': route.end_address,
                'created_at': route.created_at,
                'updated_at': route.updated_at
            } for route in routes]

            return JsonResponse({'routes': routes_data})
        
        except Exception as e:
            # Retorna erro caso algo dê errado
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)


# Renderiza a página de horários de passagem
def discard_locations(request):
    return render(request, 'discardLocations.html')

def get_discard_locations(request):
    # Obter o bairro da requisição (por exemplo, de um parâmetro GET)
    neighborhood = request.GET.get('neighborhood', None)
    
    if neighborhood:
        # Filtrar os locais de descarte pelo bairro
        locations = DiscardLocation.objects.filter(neighborhood=neighborhood)
    else:
        # Caso não seja especificado um bairro, retornar um erro
        return JsonResponse({'error': 'Bairro não fornecido'}, status=400)
    
    # Criar uma lista de resultados com os dados dos locais de descarte
    location_data = list(locations.values('name', 'latitude', 'longitude', 'address', 'content_types'))

    # Retornar os dados em formato JSON
    return JsonResponse({'locations': location_data})