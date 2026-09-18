from typing import cast

from decouple import config


DATABASE_URL = cast(str, config("DATABASE_URL"))
TEST_DATABASE_URL = cast(str, config("TEST_DATABASE_URL"))

SECRET_KEY = cast(str, config("SECRET_KEY"))