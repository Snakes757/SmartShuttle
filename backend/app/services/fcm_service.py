from firebase_admin import messaging

def send_push_notification(device_token: str, title: str, body: str, data: dict = None):
    """
    Uses Firebase Cloud Messaging (FCM) to send real-time updates to users.
    Requirement: "All users should get relevant pop up notifications on their devices."
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data if data else {},
            token=device_token,
        )
        # Send a message to the device corresponding to the provided registration token.
        response = messaging.send(message)
        print(f"Successfully sent FCM message: {response}")
        return True
    except Exception as e:
        print(f"Error sending FCM message: {e}")
        return False

def notify_trip_update(device_token: str, trip_id: str, status: str):
    """Helper to send AI real-time tracking/arrival updates."""
    send_push_notification(
        device_token=device_token,
        title="Trip Update 🚐",
        body=f"Your trip status has been updated to: {status}",
        data={"trip_id": trip_id, "type": "TRIP_UPDATE"}
    )