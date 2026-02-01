import logging


def get_logger(request_id=None,user_id=None,role=None):


    logger=logging.getLogger("app")


    extra={}

    if request_id:
        extra["request_id"]=request_id
    if user_id:
        extra["user_id"]=user_id
    if role:
        extra["role"]=role
    
    return logging.LoggerAdapter(logger,extra)