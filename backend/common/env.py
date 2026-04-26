import os
import environ
from pathlib import Path

BASE_DIR= Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)

# load env once
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))