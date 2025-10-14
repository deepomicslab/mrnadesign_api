"""Phage_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers

from antigen.views import antigenViewSet
from tantigen.views import tantigenViewSet
from three_utr.views import three_utrViewSet
from mirtarbase_db.views import mirtarbaseViewSet
from gtrnadb.views import gtrnadbViewSet, gtrnadbDetailViewSet, gtrnadbDetailCommonViewSet
from tsnadb.views import tsnadb2ValidatedViewSet, tsnadb2NeoantigenViewSet
from rebase_db.views import rebaseDataViewSet, rebaseLinkViewSet
from utrdb.views import utrdbViewSet
from isoform_datasets.views import isoformdbDatasetsViewSet
from isoform_samples.views import isoformdbSamplesViewSet, isoformdbSamplesDetailViewSet
from isoform_sequences.views import (
    isoformdbIsoformsViewSet, 
    isoformdbIsoformsSequencesViewSet, 
    isoformdbIsoformsDetailViewSet, 
    isoformdbGenesViewSet, 
    FileTrackView
)
from transcripthub.views import (
    transcripthubAssemblyViewSet,
    transcripthubAnnotationViewSet,
)
from tcrabpairing.views import tcrabpairingView

import mrna_task.views
import taskresult.views
import antigen.views
import tantigen.views
import three_utr.views
import utrdb.views
import codon.views
import transcripthub.views

from django.urls import include, re_path

router = routers.DefaultRouter()

# router.register('analysis', analysisViewSet)
# router.register('task', taskViewSet)
# router.register('phage_lifestyle', phage_lifestyleViewSet)


urlpatterns = [
    path('', include(router.urls)),

    re_path('database/', include('database.urls')),  # api/database/xxx
    re_path('analysis/', include('analysis.urls')),  # api/analysis/xxx

    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls')),

    path('antigen/', antigenViewSet.as_view()),
    path('tantigen/', tantigenViewSet.as_view()),
    path('three_utr/', three_utrViewSet.as_view()),
    path('mirtarbase/', mirtarbaseViewSet.as_view()),
    path('gtrnadb/', gtrnadbViewSet.as_view()),
    path('gtrnadb/detail/', gtrnadbDetailViewSet.as_view()),
    path('gtrnadb/detail/common/', gtrnadbDetailCommonViewSet.as_view()),
    path('tsnadb2/validated/', tsnadb2ValidatedViewSet.as_view()),
    path('tsnadb2/neoantigen/', tsnadb2NeoantigenViewSet.as_view()),
    path('rebase/data/', rebaseDataViewSet.as_view()),
    path('rebase/link/', rebaseLinkViewSet.as_view()),
    path('utrdb/', utrdbViewSet.as_view()),
    path('isoformdb/datasets/', isoformdbDatasetsViewSet.as_view({'get': 'list'})),
    path('isoformdb/samples/', isoformdbSamplesViewSet.as_view()),
    path('isoformdb/samples/detail/', isoformdbSamplesDetailViewSet.as_view()),
    path('isoformdb/isoforms/', isoformdbIsoformsViewSet.as_view()),
    path('isoformdb/isoforms/sequences/', isoformdbIsoformsSequencesViewSet.as_view()),
    path('isoformdb/isoforms/detail/', isoformdbIsoformsDetailViewSet.as_view()),
    path('isoformdb/genes/', isoformdbGenesViewSet.as_view()),
    path('isoformdb/jbrowser/<path:file_path>', FileTrackView.as_view()),
    path('codon_pair/', codon.views.codonpairViewSet.as_view()),
    path('codon_pair/heatmap/', codon.views.codonpairHeatmapViewSet),
    path('codon_pair/download/', codon.views.codonpairDownloadViewSet),
    path('transcripthub/assembly/', transcripthubAssemblyViewSet.as_view()),
    path('transcripthub/annotation/', transcripthubAnnotationViewSet.as_view()),
    path('transcripthub/annotation/sequence/', transcripthub.views.transcripthubAnnotationSequenceView),
    path('tcrabpairing/', tcrabpairingView.as_view()),

    path('overview/antigensourceorganism/', antigen.views.getsourceorganism),
    path('overview/stats/antigen/', antigen.views.getstats),
    path('overview/stats/tantigen/', tantigen.views.getstats),
    path('overview/stats/threeutr/', three_utr.views.getstats),

    path('analyze/linear_design/', mrna_task.views.lineardesignView.as_view()),
    path('analyze/linear_design_inputcheck/',
         mrna_task.views.lineardesigninputcheckView.as_view()),
    path('analyze/prediction/', mrna_task.views.predictionView.as_view()),
    path('analyze/str_similarity/', mrna_task.views.strSimilarityView),
    path('analyze/get_str_similarity/', mrna_task.views.getStrSimilarityView),path('analyze/safety/', mrna_task.views.safetyView.as_view()),
    path('analyze/sequence_align/', mrna_task.views.sequencealignView.as_view()),
    path('analyze/antigen_screening/', mrna_task.views.antigenscreeningView.as_view()),
    path('analyze/tsa/', mrna_task.views.tsaView.as_view()),
    path('analyze/tsa/hla_types', mrna_task.views.tsaHLATypesView),
    path('analyze/tcranno/', mrna_task.views.tcrannoView.as_view()),
    path('analyze/tcrabpairing/', mrna_task.views.tcrabpairingView.as_view()),

    path('tasks/parameter/lineardesign/', mrna_task.views.viewlineardesignparamdetail),
    path('tasks/detail/', mrna_task.views.viewtaskdetail),
    path('tasks/detail/log/', mrna_task.views.viewtasklog),
    path('tasks/list/', mrna_task.views.viewtask),
    path('tasks/tsa_result/', taskresult.views.tsaresultView),
    path('tasks/safety_result/', taskresult.views.safetyresultView),
    path('tasks/sequencealign_result/', taskresult.views.sequencealignresultView),
    path('tasks/antigenscreening_result/', taskresult.views.antigenscreeningresultView),
    path('tasks/lineardesign_result/', taskresult.views.lineardesignresultView),
    path('tasks/prediction_result/', taskresult.views.predictionresultView),
    path('tasks/tcranno_result/', taskresult.views.tcrannoresultView),
    path('tasks/tcrabpairing_result/', taskresult.views.tcrabpairingresultView),
    path('tasks/proteinstructure/', taskresult.views.viewproteinstructure),
    path('tasks/secondarystructure/', taskresult.views.viewsecondarystructure),
    path('tasks/zip/', taskresult.views.getZipData),
    path('tasks/image/serve_image/', taskresult.views.serve_image, name='serve_image'),

    path('task/result/sequencemarker/', taskresult.views.sequencemarker),
    path('task/result/primarystructure_mainregion/',
         taskresult.views.viewprimarystructuremainregion),
    path('task/result/primarystructure_uORF/',
         taskresult.views.viewprimarystructureuorf),
    path('task/result/primarystructure_res/',
         taskresult.views.viewprimarystructureres),
    path('task/result/scoringheatmap/', taskresult.views.viewscoring),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
