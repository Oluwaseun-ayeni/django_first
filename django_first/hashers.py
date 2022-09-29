from django.contrib.auth.hashers import PBKDF2PasswordHasher
import hashlib



# class MyPBKDF2SHA256PasswordHasher(PBKDF2PasswordHasher):
#     algorithm = "pbkdf2_sha256"
#     digest = hashlib.sha256
#     iterations = PBKDF2PasswordHasher.iterations * 5

from django.contrib.auth.hashers import (
    PBKDF2PasswordHasher, SHA1PasswordHasher,
)


class PBKDF2WrappedSHA1PasswordHasher(PBKDF2PasswordHasher):
    algorithm = 'pbkdf2_wrapped_sha1'

    def encode_sha1_hash(self, sha1_hash, salt, iterations=None):
        return super().encode(sha1_hash, salt, iterations)

    def encode(self, password, salt, iterations=None):
        _, _, sha1_hash = SHA1PasswordHasher().encode(password, salt).split('$', 2)
        return self.encode_sha1_hash(sha1_hash, salt, iterations)

