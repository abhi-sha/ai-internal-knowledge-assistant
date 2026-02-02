import logging
import json
import sys
from datetime import datetime,timezone

STANDARD_ATTRS = {
    "name", "msg", "args", "levelname", "levelno",
    "pathname", "filename", "module", "exc_info",
    "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated",
    "thread", "threadName", "processName", "process",
}


class JsonFormatter(logging.Formatter):
    def format(self,record:logging.LogRecord)->str:

        log_record={
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "level":record.levelname,
        "message":record.getMessage(),
        "logger":record.name
        }

        if hasattr(record,"request_id"):
            log_record["request_id"]=record.request_id
        
        if hasattr(record,"user_id"):
            log_record["user_id"]=record.user_id
        
        if hasattr(record,"role"):
            log_record["role"]=record.role
        
        for key, value in record.__dict__.items():
            if key not in STANDARD_ATTRS and key not in log_record:
                log_record[key] = value

        if record.exc_info:
            log_record["exception"]=self.formatException(record.exc_info)

        return json.dumps(log_record)
    

def configure_logging():

    handler=logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root=logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers=[handler]