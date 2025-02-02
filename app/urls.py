from django.urls import path
from . import views

urlpatterns = [
    
    # endpoint que retorna a página inicial
    path('', views.home, name='home'),

    # endpoint que busca os caminhões próximos ao morador de determinado bairro
    path('locate_trucks_in_neighborhood/', views.locate_trucks_in_neighborhood, name='locate_trucks_in_neighborhood'),

    # endpoint para buscar localizações dos caminhões por filtro de bairros
    path('api/locations', views.get_truck_locations, name='get_truck_locations'),

    # endpoint de login do motorista
    path('login/', views.login_view, name='login'),

    # endpoint de logout do motorista
    path('logout/', views.logout_view, name='logout'), 

    # endpoint que renderiza a interface de rastreamento 
    path('tracking-interface/', views.tracking_interface, name='tracking_interface'),

    # endpoint para atualizar a localização do caminhão de lixo
    path('api/update-truck-location', views.update_truck_location, name='update_truck_location'),

    # endpoint para enviar dados de rastreamento para a interface do motorista
    path('tracking-info-for-user/', views.get_tracking_info_for_user, name='tracking_info_for_user'),
    
    # endpoint para buscar rotas de coleta
    path('api/routes/locations/', views.get_route_locations, name='get_route_locations'),

    # endpoint que renderiza a interface de horários de passagem
    path('passage_times-interface/', views.passage_times, name='passage_times-interface'),

    # endpoint que busca as rotas de caminhões por bairros
    path('routes/neighborhood/', views.fetch_routes_by_neighborhood, name='fetch_routes_by_neighborhood'),

    # endpoint que renderiza a interface de locais de descarte
    path('discard_locations-interface/', views.discard_locations, name='discard_locations-interface'),

    path('get-discard-locations/', views.get_discard_locations, name='get_discard_locations'),

]