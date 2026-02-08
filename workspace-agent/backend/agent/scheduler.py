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
        self.eod_hour = config.EOD_REPORT_HOUR
        self.eod_minute = config.EOD_REPORT_MINUTE
        print("[SCHEDULER] Initialized")
    
    def start(self):
        """Start scheduler with multiple jobs"""
        # EOD report at configured time (default 6 PM)
        self.scheduler.add_job(
            self._trigger_eod_report,
            trigger=CronTrigger(hour=self.eod_hour, minute=self.eod_minute),
            id='eod_report',
            name='Daily EOD Report'
        )
        
        # Data refresh every 30 minutes
        self.scheduler.add_job(
            self._refresh_data,
            trigger='interval',
            minutes=30,
            id='data_refresh',
            name='Data Refresh'
        )
        
        self.scheduler.start()
        print(f"[SCHEDULER] Started! EOD at {self.eod_hour}:{self.eod_minute:02d}, Data refresh every 30min")
    
    async def _trigger_eod_report(self):
        """Run the EOD report generation"""
        print("[SCHEDULER] Running scheduled EOD report...")
        try:
            await self.agent.autonomous_observation_cycle()
            print("[SCHEDULER] EOD report completed successfully")
        except Exception as e:
            print(f"[SCHEDULER ERROR] EOD report failed: {e}")
    
    async def _refresh_data(self):
        """Background data refresh"""
        print("[SCHEDULER] Refreshing workspace data...")
        try:
            observations = await self.agent._observe_workspace()
            
            # Store the refreshed data
            insights = await self.agent._reason_over_observations(observations)
            await self.agent._store_observations_and_insights(observations, insights)
            
            print("[SCHEDULER] Data refreshed successfully")
        except Exception as e:
            print(f"[SCHEDULER ERROR] Data refresh failed: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("[SCHEDULER] Stopped")