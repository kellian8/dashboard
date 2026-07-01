from types import SimpleNamespace
from datetime import datetime, time, timedelta

from .constants import GUI_HOST, GUI_PORT


class _(SimpleNamespace):
    """
    Read-only SimpleNamespace. Prevents accidental mutation of config values.
    Also allows for dot notation access to config values.
    Raises AttributeError on mutation.
    """

    def __setattr__(self, name, value):
        raise AttributeError("Config namespace is read-only")

    def __delattr__(self, name):
        raise AttributeError("Config namespace is read-only")


# _____________________ TASK CONFIGURATIONS _____________________
TaskConfigs = {
    "FETCH_SUMMARY": _(
        name="fetch_investment_summary",
        schedules=[
            # Fetch summary on application start _____________
            _(
                type="one_time",
                execution_time=datetime.now() + timedelta(seconds=5)
            ),

            # Recurring schedules ____________________________

            _( # Just before LDN market open
                type="recurring_time",
                time=time(hour=7, minute=30, second=0)
            ),
            _( # Just after LDN market open
                type="recurring_time",
                time=time(hour=8, minute=30, second=0)
            ),
            _( # LDN market close
                type="recurring_time",
                time=time(hour=16, minute=30, second=0)
            ),
            _( # NY market open
                type="recurring_time",
                time=time(hour=14, minute=0, second=0)
            ),
            _( # NY market close
                type="recurring_time",
                time=time(hour=21, minute=30, second=0)
            ),
        ],
        callback="update_gui_summary",
    ),
    "UPDATE_GUI_SUMMARY": _(
        name="update_gui_summary",
        schedules=[],
        callback=None,
    ),
}

# _______________ URL & ENDPOINT CONFIGURATIONS ________________
URLs = {
    "T212": _(
        base_url="https://live.trading212.com/api/v0",
        endpoints=_(
            summary="/equity/account/summary"
        )
    ),
    "DASH_GUI": _(
        base_url=f"http://{GUI_HOST}:{GUI_PORT}",
        endpoints=_(
            push_summary="/ingest/summary"
        )
    ),
}