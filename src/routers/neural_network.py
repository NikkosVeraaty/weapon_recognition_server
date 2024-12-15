from fastapi import APIRouter, Header
from fastapi.responses import Response, JSONResponse
from src.schemas import NeuralNetworkParams
from src.inspector import check_role_from_db
from typing import Annotated
import logging
import yaml
import json


network = APIRouter(prefix='/nn', tags=['Neural Network'])


@network.post("/parameters/change")
async def change_nn_params(parameters: NeuralNetworkParams, token: Annotated[str, Header()]):
    logging.info(f"Start changing nn params")

    res = check_role_from_db(token)

    if res == "admin":
        logging.info(f"Write new parameters")

        with open('data/config_nn.yaml', 'w') as yaml_file:
            yaml_file.write(yaml.dump({"parameters": parameters.model_dump()}, default_flow_style=False))

        return Response("Successfully changing nn parameters", status_code=200)
    else:
        return Response("Don't have enough rights", status_code=403)


@network.get("/parameters/get")
async def get_parameters(token: Annotated[str, Header()]):
    logging.info(f"Get all parameters")

    res = check_role_from_db(token)

    if res == "admin":
        with open('data/config_nn.yaml', 'r') as yaml_file:
            params = yaml.safe_load(yaml_file)

            params_json = json.dumps(params)

        return JSONResponse(json.loads(params_json), status_code=200)
    else:
        return Response("Don't have enough rights", status_code=403)

