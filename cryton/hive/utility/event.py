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
        stage_ex = stage.StageExecution(stage_ex_id)

        # Validate if the Stage can be triggered
        states.StageStateMachine.validate_state(stage_ex.state, [states.AWAITING])
        stage_ex.serialized_output = self.event_details.get("parameters", {})

        # Stop the trigger and start the Stage execution
        stage_ex.trigger.stop(trigger_id=trigger_id, queue=stage_ex.control_queue)
        stage_ex.execute()

    def handle_finished_step(self) -> None:
        """
        Check for FINISHED states.
        :return: None
        """
        logger.logger.debug("Handling finished Step", step_execution_id=self.event_details["step_execution_id"])
        step_ex_obj = step.StepExecution(self.event_details["step_execution_id"])

        if step_ex_obj.model.step.stage.plan.dynamic:
            return

        stage_ex_obj = stage.StageExecution(step_ex_obj.model.stage_execution_id)
        if stage_ex_obj.all_steps_finished and stage_ex_obj.state not in states.STAGE_FINAL_STATES:
            stage_ex_obj.finish()

            plan_ex_obj = plan.PlanExecution(stage_ex_obj.model.plan_execution_id)
            if plan_ex_obj.all_stages_finished and plan_ex_obj.state not in states.PLAN_FINAL_STATES:
                plan_ex_obj.finish()

                run_obj = run.Run(plan_ex_obj.model.run_id)
                if run_obj.all_plans_finished and run_obj.state not in states.RUN_FINAL_STATES:
                    run_obj.finish()
