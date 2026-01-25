from typing import Protocol

class NotificationService(Protocol):
    async def notify_action_required(self, customer_id: str, case_id: str, message: str):
        ...
