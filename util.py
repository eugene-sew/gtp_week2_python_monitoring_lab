import psutil

def secs_to_hours(secs):

    if secs == psutil.POWER_TIME_UNKNOWN or secs == psutil.POWER_TIME_UNLIMITED:
        return "N/A"
    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    return f"{int(hh)}:{int(mm):02}:{int(ss):02}"
