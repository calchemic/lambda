from lambda_function import logger, tracer, app

def allow(event, context):
    # parse event data for source IP and user agent
    event_source_ip = event['requestContext']['identity']['sourceIp']
    event_user_agent = event['requestContext']['identity']['userAgent']
    # IP Allow List
    if event_source_ip not in ['136.62.54.200']:
        return False, event_source_ip + ' is not in the allow list.'
    elif event_user_agent not in ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36']:
        return False, event_user_agent + ' is not in the allow list.'
    else:
        return True, event_source_ip + " and " + event_user_agent + ' is in the allow list.'