import json
import pytest
from app.api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


class TestHealthEndpoint:
    def test_health_status_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_success_true(self, client):
        data = r = client.get("/health").get_json()
        assert data["success"] is True

    def test_health_has_uptime(self, client):
        data = client.get("/health").get_json()
        assert "uptime_seconds" in data["data"]

    def test_health_has_version(self, client):
        data = client.get("/health").get_json()
        assert "version" in data["data"]

    def test_health_has_timestamp(self, client):
        data = client.get("/health").get_json()
        assert "timestamp" in data["data"]

    def test_health_has_requests_served(self, client):
        data = client.get("/health").get_json()
        assert "requests_served" in data["data"]


class TestStatusEndpoint:
    def test_status_200(self, client):
        assert client.get("/status").status_code == 200

    def test_status_api_online(self, client):
        data = client.get("/status").get_json()
        assert data["data"]["api"] == "online"

    def test_status_calculator_ready(self, client):
        data = client.get("/status").get_json()
        assert data["data"]["calculator"] == "ready"


class TestVersionEndpoint:
    def test_version_200(self, client):
        assert client.get("/version").status_code == 200

    def test_version_has_version(self, client):
        data = client.get("/version").get_json()
        assert "version" in data["data"]

    def test_version_has_build(self, client):
        data = client.get("/version").get_json()
        assert "build" in data["data"]


class TestAddEndpoint:
    def test_add_basic(self, client):
        r = post_json(client, "/api/calculate/add", {"a": 5, "b": 3})
        assert r.status_code == 200
        assert r.get_json()["data"]["result"] == 8

    def test_add_negative(self, client):
        r = post_json(client, "/api/calculate/add", {"a": -3, "b": -7})
        assert r.get_json()["data"]["result"] == -10

    def test_add_floats(self, client):
        r = post_json(client, "/api/calculate/add", {"a": 1.5, "b": 2.5})
        assert r.get_json()["data"]["result"] == pytest.approx(4.0)

    def test_add_missing_field(self, client):
        r = post_json(client, "/api/calculate/add", {"a": 5})
        assert r.status_code == 400

    def test_add_string_input(self, client):
        r = post_json(client, "/api/calculate/add", {"a": "x", "b": 3})
        assert r.status_code == 400

    def test_add_returns_operation(self, client):
        r = post_json(client, "/api/calculate/add", {"a": 1, "b": 2})
        assert r.get_json()["data"]["operation"] == "add"


class TestSubtractEndpoint:
    def test_subtract_basic(self, client):
        r = post_json(client, "/api/calculate/subtract", {"a": 10, "b": 4})
        assert r.get_json()["data"]["result"] == 6

    def test_subtract_missing(self, client):
        r = post_json(client, "/api/calculate/subtract", {"a": 5})
        assert r.status_code == 400


class TestMultiplyEndpoint:
    def test_multiply_basic(self, client):
        r = post_json(client, "/api/calculate/multiply", {"a": 6, "b": 7})
        assert r.get_json()["data"]["result"] == 42

    def test_multiply_zero(self, client):
        r = post_json(client, "/api/calculate/multiply", {"a": 100, "b": 0})
        assert r.get_json()["data"]["result"] == 0

    def test_multiply_string_input(self, client):
        r = post_json(client, "/api/calculate/multiply", {"a": "bad", "b": 2})
        assert r.status_code == 400


class TestDivideEndpoint:
    def test_divide_basic(self, client):
        r = post_json(client, "/api/calculate/divide", {"a": 10, "b": 2})
        assert r.get_json()["data"]["result"] == pytest.approx(5.0)

    def test_divide_by_zero(self, client):
        r = post_json(client, "/api/calculate/divide", {"a": 5, "b": 0})
        assert r.status_code == 400

    def test_divide_float(self, client):
        r = post_json(client, "/api/calculate/divide", {"a": 7, "b": 2})
        assert r.get_json()["data"]["result"] == pytest.approx(3.5)

    def test_divide_invalid(self, client):
        r = post_json(client, "/api/calculate/divide", {"a": "x", "b": 2})
        assert r.status_code == 400


class TestPowerEndpoint:
    def test_power_basic(self, client):
        r = post_json(client, "/api/calculate/power", {"base": 2, "exp": 8})
        assert r.get_json()["data"]["result"] == 256

    def test_power_zero_exp(self, client):
        r = post_json(client, "/api/calculate/power", {"base": 99, "exp": 0})
        assert r.get_json()["data"]["result"] == 1

    def test_power_missing(self, client):
        r = post_json(client, "/api/calculate/power", {"base": 2})
        assert r.status_code == 400


class TestSqrtEndpoint:
    def test_sqrt_basic(self, client):
        r = post_json(client, "/api/calculate/sqrt", {"n": 81})
        assert r.get_json()["data"]["result"] == pytest.approx(9.0)

    def test_sqrt_negative(self, client):
        r = post_json(client, "/api/calculate/sqrt", {"n": -4})
        assert r.status_code == 400

    def test_sqrt_zero(self, client):
        r = post_json(client, "/api/calculate/sqrt", {"n": 0})
        assert r.get_json()["data"]["result"] == pytest.approx(0.0)


class TestStatsEndpoint:
    def test_stats_basic(self, client):
        r = post_json(client, "/api/calculate/stats", {"values": [1, 2, 3, 4, 5]})
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["mean"] == pytest.approx(3.0)
        assert data["min"] == 1
        assert data["max"] == 5

    def test_stats_empty(self, client):
        r = post_json(client, "/api/calculate/stats", {"values": []})
        assert r.status_code == 400

    def test_stats_non_numeric(self, client):
        r = post_json(client, "/api/calculate/stats", {"values": ["a", "b"]})
        assert r.status_code == 400

    def test_stats_single_no_stdev(self, client):
        r = post_json(client, "/api/calculate/stats", {"values": [42]})
        assert r.status_code == 200
        assert "std_dev" not in r.get_json()["data"]

    def test_stats_missing_field(self, client):
        r = post_json(client, "/api/calculate/stats", {})
        assert r.status_code == 400


class TestBatchEndpoint:
    def test_batch_basic(self, client):
        ops = [
            {"operation": "add", "a": 1, "b": 2},
            {"operation": "multiply", "a": 3, "b": 4},
        ]
        r = post_json(client, "/api/calculate/batch", {"operations": ops})
        assert r.status_code == 200
        results = r.get_json()["data"]["results"]
        assert results[0]["result"] == 3
        assert results[1]["result"] == 12

    def test_batch_invalid_op(self, client):
        ops = [{"operation": "hacked", "a": 1, "b": 2}]
        r = post_json(client, "/api/calculate/batch", {"operations": ops})
        assert r.status_code == 200
        assert r.get_json()["data"]["results"][0]["success"] is False

    def test_batch_too_many(self, client):
        ops = [{"operation": "add", "a": 1, "b": 2}] * 51
        r = post_json(client, "/api/calculate/batch", {"operations": ops})
        assert r.status_code == 400

    def test_batch_divide_by_zero(self, client):
        ops = [{"operation": "divide", "a": 5, "b": 0}]
        r = post_json(client, "/api/calculate/batch", {"operations": ops})
        assert r.status_code == 200
        assert r.get_json()["data"]["results"][0]["success"] is False


class TestErrorHandling:
    def test_404_not_found(self, client):
        r = client.get("/nonexistent")
        assert r.status_code == 404

    def test_405_method_not_allowed(self, client):
        r = client.get("/api/calculate/add")
        assert r.status_code == 405
