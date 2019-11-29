from functools import wraps

def show_call(func):
    """
    这个方法可以打印进入这个方法和结束这个方法的边界，使 debug 更清晰一点
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("=" * 30 + " enter " + func.__name__ + "=" * 30)
        func(*args, **kwargs)
        print("=" * 30 + " exit " + func.__name__ + "=" * 30)
    return wrapper
