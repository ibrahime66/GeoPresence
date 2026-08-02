from django.contrib.auth.hashers import Argon2PasswordHasher


class PresenceArgon2PasswordHasher(Argon2PasswordHasher):
    """Paramètres imposés par le CDC §13.2.2 : time_cost=2, memory_cost=65536 KB, parallelism=2."""

    time_cost = 2
    memory_cost = 65536
    parallelism = 2
