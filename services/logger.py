from os import environ

PROJECT_ID_SB = environ.get('PROJECT_ID_SB')


def generate_log_message(error):
    trace = []
    tb = error.__traceback__
    # Generate the source of error
    while tb is not None:
        trace.append({
            "filename": tb.tb_frame.f_code.co_filename,
            "name": tb.tb_frame.f_code.co_name,
            "line": tb.tb_lineno
        })
        tb = tb.tb_next

    return (str({
        'type': type(error).__name__,
        'message': str(error),
        'project_id': PROJECT_ID_SB,
        'trace': trace
    }))


def generate_log_message_handled(level, message, current_file, function):
    return (str({
        'type': level,
        'message': message,
        'project_id': PROJECT_ID_SB,
        'trace': [
            {
                'filename': current_file,
                'name': function,
            }
        ]
    }))
