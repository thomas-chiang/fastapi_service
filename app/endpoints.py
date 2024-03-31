"""Endpoints module."""

from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide
from typing import Optional, List


from .containers import Container
from .services import UserService, BitService, TimeService, ComparisonBitService, ScoreService, PiNotationScoreService
from .repositories import NotFoundError
from .models import ReportRequestBody, ReportInfo, Bit, Score

from google.cloud import firestore

router = APIRouter()

@router.get("/fs")
@inject
async def poc(
    firestore_db: firestore.AsyncClient = Depends(Provide[Container.firestore_db])
):
    await firestore_db.collection("poc").document("poc").set({"s": "s", "t": 10, "v": 15, "r" : 1})
    await firestore_db.collection("poc").document("poc1").set({"s": "s", "t": 11, "v": 14, "r" : 2})
    await firestore_db.collection("poc").document("poc2").set({"s": "s", "t": 12, "v": 13, "r" : 3})
    await firestore_db.collection("poc").document("poc3").set({"s": "s", "t": 13, "v": 12, "r" : 4})
    await firestore_db.collection("poc").document("poc4").set({"s": "s", "t": 14, "v": 10, "r" : 5})
    snapshot = await firestore_db.collection("poc").document("poc").get()
    snapshots = await  firestore_db.collection("poc").where("s", "==", "s").order_by("v", direction=firestore.Query.DESCENDING).order_by("s", direction=firestore.Query.DESCENDING).limit(10).get()
    for ss in snapshots:
        print(ss.to_dict())
    snapshots = await  firestore_db.collection("poc").where("s", "==", "s").where("t", "==", 13).where("r", ">", 3).get()
    for ss in snapshots:
        print(ss.to_dict())
    # return snapshot.to_dict()
    # class City:
    #     def __init__(self, name, state, country, capital=False, population=0, regions=[]):
    #         self.name = name
    #         self.state = state
    #         self.country = country
    #         self.capital = capital
    #         self.population = population
    #         self.regions = regions

    #     @staticmethod
    #     def from_dict(source):
    #         # [START_EXCLUDE]
    #         city = City(source["name"], source["state"], source["country"])

    #         if "capital" in source:
    #             city.capital = source["capital"]

    #         if "population" in source:
    #             city.population = source["population"]

    #         if "regions" in source:
    #             city.regions = source["regions"]

    #         return city
    #         # [END_EXCLUDE]

    #     def to_dict(self):
    #         # [START_EXCLUDE]
    #         dest = {"name": self.name, "state": self.state, "country": self.country}

    #         if self.capital:
    #             dest["capital"] = self.capital

    #         if self.population:
    #             dest["population"] = self.population

    #         if self.regions:
    #             dest["regions"] = self.regions

    #         return dest
    #         # [END_EXCLUDE]

    #     def __repr__(self):
    #         return f"City(\
    #                 name={self.name}, \
    #                 country={self.country}, \
    #                 population={self.population}, \
    #                 capital={self.capital}, \
    #                 regions={self.regions}\
    #             )"

    # cities_ref = db.collection("cities")
    # await cities_ref.document("BJ").set(
    #     City("Beijing", None, "China", True, 21500000, ["hebei"]).to_dict()
    # )
    # await cities_ref.document("SF").set(
    #     City(
    #         "San Francisco", "CA", "USA", False, 860000, ["west_coast", "norcal"]
    #     ).to_dict()
    # )
    # await cities_ref.document("LA").set(
    #     City(
    #         "Los Angeles", "CA", "USA", False, 3900000, ["west_coast", "socal"]
    #     ).to_dict()
    # )
    # await cities_ref.document("DC").set(
    #     City("Washington D.C.", None, "USA", True, 680000, ["east_coast"]).to_dict()
    # )
    # await cities_ref.document("TOK").set(
    #     City("Tokyo", None, "Japan", True, 9000000, ["kanto", "honshu"]).to_dict()
    # )

    # cities_ref = db.collection("cities")
    # from google.cloud.firestore_v1.base_query import FieldFilter
    # denver_query = cities_ref.where(filter=FieldFilter("state", "==", "CO")).where(
    #     filter=FieldFilter("name", "==", "Denver")
    # )
    # large_us_cities_query = cities_ref.where(
    #     filter=FieldFilter("state", "==", "CA")
    # ).where(filter=FieldFilter("population", ">", 1000000))

    # sss = await large_us_cities_query.get()

    # for ss in sss:
    #     print(ss.to_dict())

    return "poc"

@router.post("/report")
@inject
async def report_match_times(
    request_body: ReportRequestBody,
    time_service: TimeService = Depends(Provide[Container.time_service]),
    bit_service: BitService = Depends(Provide[Container.bit_service]),
    comparison_bit_service: ComparisonBitService = Depends(Provide[Container.comparison_bit_service]),
    score_service: ScoreService = Depends(Provide[Container.score_service]),
    pi_notation_score_service: PiNotationScoreService  = Depends(Provide[Container.pi_notation_score_service])
    
):

    current_timestamp: int = await time_service.get_current_timestamp()
    previous_day_timestamp: int = await time_service.get_previous_day_timestamp()
    current_bytes: bytes = await bit_service.get_current_bytes(request_body.url)
    current_bit: Bit = await bit_service.save_bit(current_bytes, current_timestamp, request_body.source)
    current_comparison_bit: Optional[Bit] = None
    current_score: Optional[Score] = None

    await pi_notation_score_service.remove_expired_pi_notation_scores(request_body.source, previous_day_timestamp)

    if await bit_service.previous_bit_exists(current_bit): 
        previous_bit: Bit = await bit_service.get_previous_bit(current_bit) # Bit of 1s before
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
    
    
    match_times = await pi_notation_score_service.get_match_times(request_body.threshold, request_body.source)
    print(match_times)  

    return ReportInfo(
        channel = request_body.source,
        time = current_timestamp,
        match_times= match_times
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
