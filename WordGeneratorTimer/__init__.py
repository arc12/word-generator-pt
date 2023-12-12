import azure.functions as func
from pg_shared.azure_utils import timer_main
from word_generator import PLAYTHING_NAME, core

def main(mytimer: func.TimerRequest) -> None:
    timer_main(mytimer, core, plaything_name=PLAYTHING_NAME)
