import logging

class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        merged = {**extra, **self.extra}
        kwargs["extra"] = merged
        return msg, kwargs
    

def get_logger(request_id=None,user_id=None,role=None):


    logger=logging.getLogger("app")


    extra={}

    if request_id:
        extra["request_id"]=request_id
    if user_id:
        extra["user_id"]=user_id
    if role:
        extra["role"]=role
    
    return ContextLoggerAdapter(logger,extra)