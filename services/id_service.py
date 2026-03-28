import random
import string


def generate_student_id():
    nums = "".join(random.choices(string.digits, k=4))
    return f"STU-{nums}-{random.randint(10, 99)}"


def generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))

