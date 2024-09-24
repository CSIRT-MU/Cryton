import requests
import yaml
import time

WORKER_ID = 0

TEMPLATE = {"name": "example", "dynamic": True, "stages": {}}
STAGE = {"no-delay-stage-{{ id }}": {"steps": {}}}
STEP = {"initial-step": {"is_init": True, "module": "command", "arguments": {"command": "whoami"}}}
STEP_REUSABLE = {"reusable-step-{{ id }}": {"module": "command", "arguments": {"cmd": "{{ command }}"}}}


def get_api_root():
    api_address = "localhost"
    api_port = 8000
    return f"http://{api_address}:{api_port}/api/"


if __name__ == "__main__":
    # Check if the Worker is specified
    if WORKER_ID < 1:
        raise Exception("Please specify a correct Worker ID at the top of the file.")
    print(f"Worker id: {WORKER_ID}")

    # Get api root
    api_root = get_api_root()

    # 1. Create a template
    r_create_template = requests.post(f"{api_root}templates/", files={"file": yaml.dump(TEMPLATE)})
    template_id = r_create_template.json()["id"]
    print(f"Template id: {template_id}")

    # 2. Create a Plan
    r_create_plan = requests.post(f"{api_root}plans/", data={"template_id": template_id})
    plan_id = r_create_plan.json()["id"]
    print(f"Plan id: {plan_id}")

    # 3. Add a Stage
    stage_inventory = {"id": 1}
    r_create_stage = requests.post(
        f"{api_root}stages/",
        data={"plan_id": plan_id},
        files={"file": yaml.dump(STAGE), "inventory_file": yaml.dump(stage_inventory)},
    )
    stage_id = r_create_stage.json()["id"]
    print(f"Stage id: {stage_id}")

    # 4. Add a Step
    r_create_step = requests.post(f"{api_root}steps/", data={"stage_id": stage_id}, files={"file": yaml.dump(STEP)})
    step_id = r_create_step.json()["id"]
    print(f"Step id: {step_id}")

    # 5. Create a new Run
    r_create_run = requests.post(f"{api_root}runs/", data={"plan_id": plan_id, "worker_ids": [WORKER_ID]})
    run_id = r_create_run.json()["id"]
    print(f"Run id: {run_id}")

    # 6. Execute the Run
    r_execute_run = requests.post(f"{api_root}runs/{run_id}/execute/", data={"run_id": run_id})
    print(f"Run response: {r_execute_run.text}")

    # 7. Create a new Step
    step_inventory = {"id": 1, "command": "echo test"}
    r_create_step2 = requests.post(
        f"{api_root}steps/",
        data={"stage_id": stage_id},
        files={"file": yaml.dump(STEP_REUSABLE), "inventory_file": yaml.dump(step_inventory)},
    )
    step_id2 = r_create_step2.json()["id"]
    print(f"Second step id: {step_id2}")

    # 8. Execute the new Step (First, get Stage execution's id)
    stage_execution_id = requests.get(f"{api_root}runs/{run_id}/report/").json()["detail"]["plan_executions"][0][
        "stage_executions"
    ][0]["id"]
    r_execute_step = requests.post(
        f"{api_root}steps/{step_id2}/execute/", data={"stage_execution_id": stage_execution_id}
    )
    print(f"Second Step response: {r_execute_step.text}")

    # 9. Get Run report
    for i in range(5):
        time.sleep(3)
        current_state = requests.get(f"{api_root}runs/{run_id}/").json()["state"]
        if current_state == "FINISHED":
            break
        print(f"Waiting for a final state. Current state: {current_state}")

    print()
    print("Report: ")
    print(yaml.dump(requests.get(f"{api_root}runs/{run_id}/report/").json()["detail"]))
