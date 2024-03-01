# import pytest
# import yaml
# from pathlib import Path
#
# from cryton.hive.utility import creator
# from cryton.hive.cryton_app.models import StepModel, StageModel, DependencyModel, SuccessorModel
#
#
# BASE_DIR = Path(__file__).resolve().parent.parent.parent
#
#
# @pytest.mark.django_db
# class TestCreator:
#     def test_create_plan(self):
#         stage_count = 3
#         step_count = 6
#         dependency_count = 2
#         successor_count = 3
#
#         with open(str(BASE_DIR) + '/template.yml') as plan_yaml:
#             plan_dict = yaml.safe_load(plan_yaml)
#         plan_obj_id = creator.create_plan(plan_dict)
#         assert plan_obj_id == 1
#         assert stage_count == StageModel.objects.filter(plan_model_id=plan_obj_id).count()
#         assert step_count == StepModel.objects.filter(stage_model__plan_model_id=plan_obj_id).count()
#         assert dependency_count == DependencyModel.objects.filter(stage_model__plan_model_id=plan_obj_id).count()
#         assert successor_count == SuccessorModel.objects.\
#             filter(parent__stage_model__plan_model_id=plan_obj_id).count()
