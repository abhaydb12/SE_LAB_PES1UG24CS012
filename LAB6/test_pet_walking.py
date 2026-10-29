import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars


def test_single_standard_30_walk():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "is_weekend": False,
        "walks": [{
            "num_pets": 1,
            "aggression_alert": False,
            "needs_meds": False
        }]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 27.0
    assert result["status"] == "COMPLETED"


def test_invalid_routes_type():
    with pytest.raises(ValueError):
        process_walking_routes("not a list", 5.0)


def test_negative_transport_fee():
    with pytest.raises(ValueError):
        process_walking_routes([], -1.0)


def test_unconfirmed_route_is_skipped():
    result = process_walking_routes(
        [{"route_confirmed": False}], 5.0
    )
    assert result == {
        "total_revenue": 0.0,
        "status": "ZERO_EARNINGS"
    }


def test_standard_60_with_medication_and_weekend():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_60",
        "is_weekend": True,
        "walks": [{
            "num_pets": 2,
            "aggression_alert": False,
            "needs_meds": True
        }]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result == {
        "total_revenue": 56.0,
        "status": "COMPLETED"
    }


def test_express_15_with_more_than_three_pets():
    routes = [{
        "route_confirmed": True,
        "session_type": "express_15",
        "walks": [{"num_pets": 4}]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 41.4


def test_unknown_session_type_counts_incident():
    routes = [{
        "route_confirmed": True,
        "session_type": "unknown",
        "walks": [{"num_pets": 1}]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


def test_zero_pets_counts_incident():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{"num_pets": 0}]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


def test_aggression_on_standard_30():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{
            "num_pets": 1,
            "aggression_alert": True,
            "needs_meds": True
        }]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 6.0


def test_aggression_on_standard_60_stops_route_earnings():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_60",
        "walks": [
            {"num_pets": 1, "aggression_alert": True},
            {"num_pets": 2}
        ]
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_EARNINGS"


def test_incident_audit_status():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "invalid",
            "walks": []
        }
        for _ in range(5)
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "INCIDENT_AUDIT"


def test_empty_gps_data():
    assert inspect_gps_collars([]) == "NO_DATA"


def test_gps_signal_stays_online():
    assert inspect_gps_collars([[10, 25, 10], [30, 40]]) == "ONLINE"


def test_gps_lost_signal_after_two_weak_readings():
    assert inspect_gps_collars([[10, 15]]) == "LOST_SIGNAL_ALERT"


def test_gps_weak_readings_must_be_consecutive():
    assert inspect_gps_collars([[10, 25, 15]]) == "ONLINE"


def test_gps_empty_collar_logs():
    assert inspect_gps_collars([[]]) == "ONLINE"
