from fastapi import FastAPI, APIRouter


class App:
    def __init__(self):
        self.app = FastAPI()
        self.router = APIRouter()
