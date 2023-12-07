"""earthquake URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path
import sys

from . import centrality_region_view, centrality_view, centrality_type_view, clustering_view, centrality_comp_view, mismatch_region_view

urlpatterns = [
    path('centrality/season', centrality_view.init_page_season),
    path('centrality-paint/season', centrality_view.init_page_paint_season),

    path('centrality-type-paint/all', centrality_type_view.init_page_paint_all),

    path('centrality-paint/all', centrality_view.init_page_paint_all),
    path('centrality/all', centrality_view.init_page_all),

    # path('clustering/season', clustering_view.init_page_season),
    # path('clustering-paint/season', clustering_view.init_page_paint_season),
    # path('clustering-paint-graph/season', clustering_view.init_page_paint_graph_season),

    path('clustering/all', clustering_view.init_page_all),
    path('clustering-paint/all', clustering_view.init_page_paint_all),
    path('clustering-paint-graph/all', clustering_view.init_page_paint_graph_all),

    path('centrality-comp-paint/season/ratio', centrality_comp_view.init_page_paint_season),
    path('centrality-comp-paint/season/estimate', centrality_comp_view.init_page_paint_season_estimate),

    path('centrality-region-paint/season', centrality_region_view.init_page_paint_season),

    path('mismatch-region-paint/season', mismatch_region_view.init_page_paint_season),
    path('mismatch-region-paint/month', mismatch_region_view.init_page_paint_month),

    path('centrality-region2/all', centrality_region_view.init_page_all_10125),

]

# urlpatterns = [
#     path('centrality-region/all', centrality_region_view.init_page_all)
# ]