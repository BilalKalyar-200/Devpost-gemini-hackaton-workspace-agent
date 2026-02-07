from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from agent.core import WorkspaceAgent
from config import config

class AgentScheduler:
    """
    Schedules autonomous agent runs
    """
    
    def __init__(self, agent: WorkspaceAgent):
        self.agent = agent
        self.scheduler = AsyncIOScheduler()
        print("[SCHEDULER] Initialized")
    
    def start(self):
        """Start the scheduler"""
        # EOD report daily at configured time
        self.scheduler.add_job(
            self.agent.autonomous_observation_cycle,
            trigger=CronTrigger(
                hour=config.EOD_REPORT_HOUR,
                minute=config.EOD_REPORT_MINUTE
            ),
            id="eod_report",
            name="Daily EOD Report",
            replace_existing=True
        )
        
        # For testing: run every 5 minutes (comment out for production)
        # self.scheduler.add_job(
        #     self.agent.autonomous_observation_cycle,
        #     trigger=CronTrigger(minute="*/5"),
        #     id="test_run",
        #     name="Test Run (Every 5 min)",
        #     replace_existing=True
        # )
        
        self.scheduler.start()
        print(f"[SCHEDULER] Started! EOD report will run daily at {config.EOD_REPORT_HOUR}:{config.EOD_REPORT_MINUTE:02d}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("[SCHEDULER] Stopped")