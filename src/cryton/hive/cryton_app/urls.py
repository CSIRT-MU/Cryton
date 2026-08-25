from django.urls import include, path
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from cryton.hive.cryton_app.views import (
    plan_views,
    stage_views,
    step_views,
    run_views,
    plan_execution_views,
    stage_execution_views,
    step_execution_views,
    execution_variable_views,
    worker_views,
    log_views,
    plan_template_views,
)  # , dynamic_run_views

router = routers.DefaultRouter()
router.register(r"runs", run_views.RunViewSet)
router.register(r"plans", plan_views.PlanViewSet)
router.register(r"plan_executions", plan_execution_views.PlanExecutionViewSet)
router.register(r"stages", stage_views.StageViewSet)
router.register(r"stage_executions", stage_execution_views.StageExecutionViewSet)
router.register(r"steps", step_views.StepViewSet)
router.register(r"step_executions", step_execution_views.StepExecutionViewSet)
router.register(r"workers", worker_views.WorkerViewSet)
router.register(r"templates", plan_template_views.PlanTemplateViewSet)
router.register(r"execution_variables", execution_variable_views.ExecutionVariableViewSet)
router.register(r"logs", log_views.LogViewSet, "log")

urlpatterns = [
    path("", router.get_api_root_view()),
    path("", include(router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc-ui"),
]
