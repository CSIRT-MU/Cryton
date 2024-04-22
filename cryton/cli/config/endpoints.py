class Run:
    LIST = "runs/"
    CREATE = "runs/"
    READ = "runs/{}/"
    DELETE = "runs/{}/"
    EXECUTE = "runs/{}/execute/"
    PAUSE = "runs/{}/pause/"
    POSTPONE = "runs/{}/postpone/"
    REPORT = "runs/{}/report/"
    RESCHEDULE = "runs/{}/reschedule/"
    SCHEDULE = "runs/{}/schedule/"
    UNPAUSE = "runs/{}/unpause/"
    UNSCHEDULE = "runs/{}/unschedule/"
    KILL = "runs/{}/kill/"
    HEALTH_CHECK_WORKERS = "runs/{}/healthcheck_workers/"
    VALIDATE_MODULES = "runs/{}/validate_modules/"
    GET_PLAN = "runs/{}/get_plan/"


class Plan:
    LIST = "plans/"
    CREATE = "plans/"
    VALIDATE = "plans/validate/"
    READ = "plans/{}/"
    DELETE = "plans/{}/"
    EXECUTE = "plans/{}/execute/"
    GET_PLAN = "plans/{}/get_plan/"


class PlanExecution:
    LIST = "plan_executions/"
    READ = "plan_executions/{}/"
    DELETE = "plan_executions/{}/"
    PAUSE = "plan_executions/{}/pause/"
    REPORT = "plan_executions/{}/report/"
    UNPAUSE = "plan_executions/{}/unpause/"
    VALIDATE_MODULES = "plan_executions/{}/validate_modules/"
    KILL = "plan_executions/{}/kill/"


class Stage:
    LIST = "stages/"
    CREATE = "stages/"
    VALIDATE = "stages/validate/"
    READ = "stages/{}/"
    DELETE = "stages/{}/"
    START_TRIGGER = "stages/{}/start_trigger/"


class StageExecution:
    LIST = "stage_executions/"
    READ = "stage_executions/{}/"
    DELETE = "stage_executions/{}/"
    REPORT = "stage_executions/{}/report/"
    KILL = "stage_executions/{}/kill/"
    RE_EXECUTE = "stage_executions/{}/re_execute/"


class Step:
    LIST = "steps/"
    CREATE = "steps/"
    VALIDATE = "steps/validate/"
    READ = "steps/{}/"
    DELETE = "steps/{}/"
    EXECUTE = "steps/{}/execute/"


class StepExecution:
    LIST = "step_executions/"
    READ = "step_executions/{}/"
    DELETE = "step_executions/{}/"
    REPORT = "step_executions/{}/report/"
    KILL = "step_executions/{}/kill/"
    RE_EXECUTE = "step_executions/{}/re_execute/"


class Worker:
    LIST = "workers/"
    CREATE = "workers/"
    READ = "workers/{}/"
    DELETE = "workers/{}/"
    HEALTH_CHECK = "workers/{}/healthcheck/"


class Template:
    LIST = "templates/"
    CREATE = "templates/"
    READ = "templates/{}/"
    DELETE = "templates/{}/"
    GET_TEMPLATE = "templates/{}/get_template/"


class ExecutionVariable:
    LIST = "execution_variables/"
    CREATE = "execution_variables/"
    READ = "execution_variables/{}/"
    DELETE = "execution_variables/{}/"


class Log:
    LIST = "logs/"
