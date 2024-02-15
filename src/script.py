import datetime
import time


def check_token(expiration: datetime) -> bool:
    lifetime = datetime.timedelta(seconds=5)
    now = datetime.datetime.now()
    print(expiration)
    print(now)
    print(expiration - now)
    return expiration - now > datetime.timedelta()


expiration = datetime.datetime.now() + datetime.timedelta(seconds=5)
print(check_token(expiration))

time.sleep(10)

print(check_token(expiration))
