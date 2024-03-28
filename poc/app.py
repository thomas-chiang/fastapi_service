from fastapi import FastAPI, Depends
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject


class Service:
    async def process(self) -> str:
        return "OK"


class Container(containers.DeclarativeContainer):

    service = providers.Factory(Service)


app = FastAPI()


@app.api_route("/")
@inject
async def index(service: Service = Depends(Provide[Container.service])):
    result = await service.process()
    return {"result": result}


container = Container()
container.wire(modules=[__name__])