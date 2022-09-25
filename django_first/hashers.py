from django.contrib.auth.hashers import PBKDF2PasswordHasher
import hashlib



class MyPBKDF2SHA256PasswordHasher(PBKDF2PasswordHasher):
    algorithm = "pbkdf2_sha256"
    digest = hashlib.sha256
    iterations = PBKDF2PasswordHasher.iterations * 5
