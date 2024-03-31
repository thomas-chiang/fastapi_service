"""Endpoints module."""
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from typing import Optional, List


from .container import Container
from .service.external_request_service import ExternalRequestService
from .service.bit_service import BitService
from .service.time_service import TimeService
from .service.comparison_bit_service import ComparisonBitService
from .service.score_service import ScoreService
from .service.pi_notation_score_service import PiNotationScoreService
from .models import ReportRequestBody, ReportInfo, Bit, Score

import asyncio


router = APIRouter()

@router.post("/report")
@inject
async def report_match_times(
    request_body: ReportRequestBody,
    time_service: TimeService = Depends(Provide[Container.time_service]),
    external_request_service: ExternalRequestService = Depends(Provide[Container.external_request_service]),
    bit_service: BitService = Depends(Provide[Container.bit_service]),
    comparison_bit_service: ComparisonBitService = Depends(Provide[Container.comparison_bit_service]),
    score_service: ScoreService = Depends(Provide[Container.score_service]),
    pi_notation_score_service: PiNotationScoreService  = Depends(Provide[Container.pi_notation_score_service])
    
) -> ReportInfo:

    current_timestamp: int
    previous_day_timestamp: int
    current_timestamp, previous_day_timestamp = await asyncio.gather(time_service.get_current_timestamp(), time_service.get_previous_day_timestamp())

    await asyncio.gather(
        pi_notation_score_service.remove_expired_pi_notation_scores(request_body.source, previous_day_timestamp),
        handle_bits_and_scores(
            current_timestamp= current_timestamp,  
            request_body= request_body,
            external_request_service=external_request_service,
            bit_service=bit_service,
            comparison_bit_service=comparison_bit_service,
            score_service=score_service,
            pi_notation_score_service=pi_notation_score_service
        )
    )

    match_times = await pi_notation_score_service.get_match_times(request_body.threshold, request_body.source)
    print(match_times)
    report_info = ReportInfo(channel = request_body.source,time = current_timestamp,match_times= match_times)
    await external_request_service.send_report(request_body.report_url, report_info)

    return report_info


async def handle_bits_and_scores(
    current_timestamp: int,  
    request_body: ReportRequestBody,
    external_request_service: ExternalRequestService,
    bit_service: BitService,
    comparison_bit_service: ComparisonBitService,
    score_service: ScoreService,
    pi_notation_score_service: PiNotationScoreService
):
    current_bit: Optional[Bit] = None
    current_comparison_bit: Optional[Bit] = None
    current_score: Optional[Score] = None
    current_bytes_value: Optional[bytes] = await external_request_service.fetch_current_bytes(request_body.url)
    if current_bytes_value:
        current_bit: Bit = await bit_service.save_bit(current_bytes_value, current_timestamp, request_body.source)

    if current_bit and await bit_service.previous_bit_exists(current_bit): 
        previous_bit: Bit = await bit_service.get_previous_bit(current_bit) 
        comparison_value: bytes = await comparison_bit_service.compute_comparison_value(current_bit, previous_bit)
        current_comparison_bit: Bit = await comparison_bit_service.save_bit(comparison_value, current_timestamp, request_body.source)

    if current_comparison_bit and await comparison_bit_service.previous_bit_exists(current_comparison_bit):
        previous_comparison_bit: Bit = await comparison_bit_service.get_previous_bit(current_comparison_bit)
        score_value: float = await score_service.compute_score(current_comparison_bit, previous_comparison_bit)
        current_score: Score = await score_service.save_score(score_value, current_timestamp, request_body.source)
    
    if current_score and await score_service.previous_4_scores_exists(current_score):
        previous_n_scores: List[Score] = await score_service.get_previous_4_scores(current_score)
        pi_notation_score_value: float = await pi_notation_score_service.compute_pi_notation_score([current_score]+previous_n_scores)
        await pi_notation_score_service.save_score(pi_notation_score_value, current_timestamp, request_body.source)




