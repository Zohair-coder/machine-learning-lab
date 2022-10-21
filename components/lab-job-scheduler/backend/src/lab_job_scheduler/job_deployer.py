from datetime import datetime
from croniter import croniter
from contaxy.operations.components import ComponentOperations
from typing import List, Dict
from lab_job_scheduler.schema import ScheduledJob
import json
from loguru import logger
from typing import Optional


def run_scheduled_jobs(cached_scheduled_jobs: Dict[str, Dict[str, ScheduledJob]], component_manager: ComponentOperations):
    """Runs all scheduled jobs."""
    for project_id, jobs in cached_scheduled_jobs.items():
        for job_id, job in jobs.items():
            if is_due(job):
                logger.info(f"Deploying job {job_id}")
                deploy_job(job, component_manager, project_id)
                update_last_run(job, component_manager,
                                project_id, cached_scheduled_jobs)
                update_next_run(job, component_manager,
                                project_id, cached_scheduled_jobs)


def is_due(job: ScheduledJob, reference_time: Optional[datetime] = None) -> bool:
    """Checks if a job is due."""
    if not reference_time:
        reference_time = datetime.now()
    next_run_time = get_next_run_time(job)
    return next_run_time <= reference_time


def get_next_run_time(job: ScheduledJob) -> datetime:
    """Returns the next run time of a job."""
    if job.last_run:
        base = datetime.fromisoformat(job.last_run)
    else:
        base = datetime.fromisoformat(job.created)
    cron = croniter(job.cron_string, base)
    return cron.get_next(datetime)


def deploy_job(job: ScheduledJob, component_manager: ComponentOperations, project_id: str):
    """Executes a job."""
    component_manager.get_job_manager().deploy_job(
        project_id=project_id, job_input=job.job_input)


def update_last_run(job: ScheduledJob, component_manager: ComponentOperations, project_id: str, cached_scheduled_jobs: Dict[str, Dict[str, ScheduledJob]]):
    """Updates the last run of a job."""
    job.last_run = datetime.now().isoformat()
    db = component_manager.get_json_db_manager()
    db.update_json_document(
        project_id=project_id,
        collection_id="schedules",
        key=job.job_id,
        json_document=json.dumps(job.dict()),
    )
    cached_scheduled_jobs[project_id][job.job_id].last_run = job.last_run


def update_next_run(job: ScheduledJob, component_manager: ComponentOperations, project_id: str, cached_scheduled_jobs: Dict[str, Dict[str, ScheduledJob]]):
    """Updates the next run of a job."""
    job.next_run = get_next_run_time(job).isoformat()
    db = component_manager.get_json_db_manager()
    db.update_json_document(
        project_id=project_id,
        collection_id="schedules",
        key=job.job_id,
        json_document=json.dumps(job.dict()),
    )
    cached_scheduled_jobs[project_id][job.job_id].next_run = job.next_run
