class StubNotificationService:
    async def notify_action_required(self, customer_id: str, case_id: str, message: str):
        # Later: integrate with email/sms/in-app notifications
        return
