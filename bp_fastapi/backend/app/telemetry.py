import os
import logging

INSTR_KEY = os.getenv("APPLICATION_INSIGHTS_INSTRUMENTATION_KEY", "").strip()

try:
    if INSTR_KEY:
        from applicationinsights import TelemetryClient
        _client = TelemetryClient(INSTR_KEY)
    else:
        _client = None
except Exception:
    _client = None

logger = logging.getLogger("bp_telemetry")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

def track_event(name: str, properties: dict = None, measurements: dict = None):
    """
    Tracks an event to Application Insights if key present, otherwise logs to console.
    """
    props = properties or {}
    meas = measurements or {}
    if _client:
        try:
            _client.track_event(name, props, meas)
            _client.flush()
        except Exception as e:
            logger.exception("Failed to send telemetry: %s", e)
    else:
        logger.info("Telemetry Event: %s | props=%s meas=%s", name, props, meas)

def track_metric(name: str, value: float, properties: dict = None):
    if _client:
        try:
            _client.track_metric(name, value, properties or {})
            _client.flush()
        except Exception as e:
            logger.exception("Failed to send telemetry metric: %s", e)
    else:
        logger.info("Telemetry Metric: %s = %s | props=%s", name, value, properties)
