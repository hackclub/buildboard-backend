"""
Job Scheduler

Runs all background jobs on a schedule using APScheduler.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from jobs.idv_sync import run_idv_sync


def create_scheduler() -> BlockingScheduler:
    """Create and configure the scheduler with all jobs."""
    scheduler = BlockingScheduler()
    
    # IDV Sync - runs every hour
    scheduler.add_job(
        run_idv_sync,
        trigger=IntervalTrigger(hours=1),
        id="idv_sync",
        name="IDV Sync Job",
        replace_existing=True,
        next_run_time=datetime.now()  # Run immediately on startup
    )
    
    # Add more jobs here as needed:
    # scheduler.add_job(
    #     some_other_job,
    #     trigger=IntervalTrigger(minutes=30),
    #     id="other_job",
    #     name="Other Job",
    #     replace_existing=True
    # )
    
    return scheduler


def main():
    print(" Starting Job Scheduler")
    print("=" * 50)
    
    scheduler = create_scheduler()
    
    # Print registered jobs
    print("\n Registered Jobs:")
    for job in scheduler.get_jobs():
        print(f"   • {job.name} (ID: {job.id})")
        print(f"     Next run: {job.next_run_time}")
    
    print("\n" + "=" * 50)
    print(" Scheduler running. Press Ctrl+C to exit.\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n️ Scheduler stopped.")


if __name__ == "__main__":
    main()
