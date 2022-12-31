import redis


class AuthenticationRepository:
    def __init__(self, password, ttl):
        print(f"password: {password}")
        print(f"ttl: {ttl}")
        self.db = redis.Redis(
            host="redis-17318.c91.us-east-1-3.ec2.cloud.redislabs.com",
            port=17318,
            password=password,
        )
        self.ttl = ttl  # seconds

    def get(self, token):
        result = self.db.get(token)
        return result.decode() if result is not None else result

    def set(self, token):
        return self.db.set(token, "a", ex=self.ttl)

    def remove(self, token):
        return self.db.delete(token)
