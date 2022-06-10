from geojson_pydantic import Feature, Point, Polygon
from pydantic import BaseModel
from typing import Dict

PointFeatureModel = Feature[Point, Dict]
PolygonFeatureModel = Feature[Polygon, Dict]
class MdsStop(BaseModel):
    stop_id: str
    name: str
    last_reported: int
    location: PointFeatureModel
    status: Dict[str, bool]
    capacity: Dict[str, int]
    num_vehicles_available: Dict[str, int] = {}
    num_vehicles_disabled: Dict[str, int] = {}
    num_places_available: Dict[str, int] = {}
    geography_id: str
    area: PolygonFeatureModel
    municipality: str

    class Config:
        fields = {
            'area': {
                'exclude': True,
            },
            'municipality': {
                'exclude': True,
            }
        }

