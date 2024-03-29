"""Endpoints module."""

from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide

from .containers import Container
from .services import UserService, BitService, TimeService, ComparisonBitService
from .repositories import NotFoundError
from .models import ReportRequestBody, ReportInfo, Bit

router = APIRouter()

@router.post("/report")
@inject
async def report_match_times(
    requestBody: ReportRequestBody,
    time_service: TimeService = Depends(Provide[Container.time_service]),
    bit_service: BitService = Depends(Provide[Container.bit_service]),
    comparison_bit_service: ComparisonBitService = Depends(Provide[Container.comparison_bit_service]),
    # score_service: ScoreService = Depends(Provide[Container.score_service])
    
):

    current_timestamp: int = await time_service.get_current_timestamp()
    current_bytes: bytes = await bit_service.get_current_bytes(requestBody.end_point)
    
    current_bit: Bit = await bit_service.save_bit(current_bytes, current_timestamp, requestBody.source)
    if await bit_service.previous_bit_exists(current_bit): 
        previous_bit: Bit = await bit_service.get_previous_bit(current_bit) # Bit of 1s before
        comparison_value: bytes = await comparison_bit_service.compute_comparison_value(current_bit, previous_bit)
        current_comparison_bit: Bit = await comparison_bit_service.save_bit(comparison_value, current_timestamp, requestBody.source)
        if await comparison_bit_service.previous_bit_exists(current_comparison_bit):
            previous_comparison_bit: Bit = await comparison_bit_service.get_previous_bit(current_comparison_bit)
            # score_value: Score = score_service.compute_score(current_comparison_bit, previous_comparison_bit)




    return ReportInfo(
        channel = requestBody.source,
        time = current_timestamp,
        match_times= []
    )










@router.get("/users")
@inject
def get_list(
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    return user_service.get_users()


@router.get("/users/{user_id}")
@inject
def get_by_id(
        user_id: int,
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        return user_service.get_user_by_id(user_id)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/users", status_code=status.HTTP_201_CREATED)
@inject
def add(
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    return user_service.create_user()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def remove(
        user_id: int,
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    try:
        user_service.delete_user_by_id(user_id)
    except NotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/status")
def get_status():
    return {"status": "OK"}
