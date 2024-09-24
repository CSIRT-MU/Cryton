from cryton.hive.utility import constants, logger, states
from cryton.hive.models import stage, step, plan, run


class Event:
    def __init__(self, event_details: dict):
        """
        Class containing possible events.
        :param event_details: Received event details
        """
        self.event_details = event_details

    def trigger_stage(self) -> None:
        """
        Process trigger trying to start Stage execution.
        :return: None
        """
        logger.logger.debug("Processing trigger", event_v=self.event_details)

        # Get Stage execution
        trigger_id = self.event_details.get(constants.TRIGGER_ID)
        stage_ex_id = stage.StageExecutionModel.objects.get(trigger_id=trigger_id).id
        stage_ex = stage.StageExecution(stage_execution_id=stage_ex_id)

        # Validate if the Stage can be triggered
        states.StageStateMachine(stage_ex_id).validate_state(stage_ex.state, [states.AWAITING])
        stage_ex.serialized_output = self.event_details.get("parameters", {})

        # Stop the trigger and start the Stage execution
        stage_ex.trigger.stop()
        stage_ex.execute()

    def handle_finished_step(self) -> None:
        """
        Check for FINISHED states.
        :return: None
        """
        step_ex_obj = step.StepExecution(step_execution_id=self.event_details["step_execution_id"])
        logger.logger.debug("Handling finished Step", step_execution_id=step_ex_obj.model.id)

        stage_ex_obj = stage.StageExecution(stage_execution_id=step_ex_obj.model.stage_execution_id)
        is_plan_dynamic = stage_ex_obj.model.stage.plan.dynamic
        if stage_ex_obj.all_steps_finished and not (is_plan_dynamic and stage_ex_obj.state == states.FINISHED):
            stage_ex_obj.finish()

            plan_ex_obj = plan.PlanExecution(plan_execution_id=stage_ex_obj.model.plan_execution_id)
            if plan_ex_obj.all_stages_finished and not (is_plan_dynamic and plan_ex_obj.state == states.FINISHED):
                plan_ex_obj.finish()

                run_obj = run.Run(run_model_id=plan_ex_obj.model.run_id)
                if run_obj.all_plans_finished and not (is_plan_dynamic and run_obj.state == states.FINISHED):
                    run_obj.finish()
