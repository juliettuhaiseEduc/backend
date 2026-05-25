from datetime import datetime, timedelta
from .models import Notification


def _already_sent(user, title, within_minutes=10):
    """Prevent duplicate notifications within a time window."""
    cutoff = datetime.utcnow() - timedelta(minutes=within_minutes)
    from django.utils import timezone
    cutoff = timezone.now() - timedelta(minutes=within_minutes)
    return Notification.objects.filter(
        user=user, title=title, created_at__gte=cutoff
    ).exists()


def notify(user, type, title, message, device_name='', dedupe_minutes=10):
    if _already_sent(user, title, dedupe_minutes):
        return None
    return Notification.objects.create(
        user=user, type=type, title=title,
        message=message, device_name=device_name,
    )


# ── Specific notification helpers ─────────────────────────

def pump_starting_soon(user, pump_time, device_name=''):
    return notify(
        user, 'pump',
        '⏰ Pump Starting Soon',
        f'Irrigation pump is scheduled to start at {pump_time} — in about 4 minutes. Make sure the water supply is ready.',
        device_name, dedupe_minutes=5,
    )


def pump_failure(user, device_name=''):
    return notify(
        user, 'sensor',
        '🚨 Pump Failure Detected',
        'The irrigation pump failed to start or stopped unexpectedly. Check the pump connection and power supply.',
        device_name, dedupe_minutes=30,
    )


def no_water_in_tank(user, device_name=''):
    return notify(
        user, 'water',
        '💧 Water Tank Empty',
        'The water tank level is critically low or empty. Irrigation cannot proceed until the tank is refilled.',
        device_name, dedupe_minutes=60,
    )


def irrigation_skipped(user, reason='', device_name=''):
    return notify(
        user, 'pump',
        '⏭️ Irrigation Skipped',
        f"Today's irrigation was skipped. Reason: {reason or 'Weather conditions do not require irrigation.'}",
        device_name, dedupe_minutes=60,
    )


def pump_stopped_manually(user, device_name=''):
    return notify(
        user, 'pump',
        '🛑 Pump Stopped Manually',
        'The irrigation pump was manually stopped before completing the scheduled cycle.',
        device_name, dedupe_minutes=5,
    )


def irrigation_stopped(user, device_name=''):
    return notify(
        user, 'pump',
        '🔴 Irrigation Stopped',
        'Irrigation has been stopped. All scheduled pump cycles for today have been cancelled.',
        device_name, dedupe_minutes=5,
    )
