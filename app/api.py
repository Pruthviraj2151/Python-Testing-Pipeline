import os
import time
import logging
from datetime import datetime
from flask import Flask, jsonify, request, Response
from app.calculator import Calculator, CalculatorError, DivisionByZeroError, InvalidInputError
from app.utils import setup_logging, build_response

APP_VERSION = "1.0.0"
BUILD_NUMBER = os.getenv("BUILD_NUMBER", "local")
ENV = os.getenv("APP_ENV", "development")

logger = setup_logging("api", logging.INFO)
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

_start_time = time.time()
_request_count = 0


def get_calculator() -> Calculator:
    return Calculator()


@app.before_request
def count_requests():
    global _request_count
    _request_count += 1


@app.errorhandler(404)
def not_found(e) -> tuple[Response, int]:
    return jsonify(build_response(False, message="Endpoint not found", code=404)), 404


@app.errorhandler(405)
def method_not_allowed(e) -> tuple[Response, int]:
    return jsonify(build_response(False, message="Method not allowed", code=405)), 405


@app.errorhandler(500)
def internal_error(e) -> tuple[Response, int]:
    logger.error(f"Internal server error: {e}")
    return jsonify(build_response(False, message="Internal server error", code=500)), 500


@app.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    uptime = round(time.time() - _start_time, 2)
    data = {
        "status": "healthy",
        "uptime_seconds": uptime,
        "version": APP_VERSION,
        "build": BUILD_NUMBER,
        "environment": ENV,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "requests_served": _request_count
    }
    logger.info("Health check passed")
    return jsonify(build_response(True, data=data, message="Service is healthy")), 200


@app.route("/status", methods=["GET"])
def status() -> tuple[Response, int]:
    data = {
        "api": "online",
        "calculator": "ready",
        "version": APP_VERSION,
        "build": BUILD_NUMBER,
        "environment": ENV
    }
    return jsonify(build_response(True, data=data, message="All systems operational")), 200


@app.route("/version", methods=["GET"])
def version() -> tuple[Response, int]:
    data = {
        "version": APP_VERSION,
        "build": BUILD_NUMBER,
        "released": "2024-01-01",
        "environment": ENV
    }
    return jsonify(build_response(True, data=data)), 200


def _extract_numbers(req_json: dict, keys: list[str]) -> list[float]:
    values = []
    for key in keys:
        val = req_json.get(key)
        if val is None:
            raise ValueError(f"Missing required field: '{key}'")
        if not isinstance(val, (int, float)):
            raise ValueError(f"Field '{key}' must be numeric, got {type(val).__name__}")
        values.append(val)
    return values


@app.route("/api/calculate/add", methods=["POST"])
def api_add() -> tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        a, b = _extract_numbers(data, ["a", "b"])
        result = get_calculator().add(a, b)
        return jsonify(build_response(True, data={"result": result, "operation": "add", "a": a, "b": b})), 200
    except (ValueError, InvalidInputError) as e:
        return jsonify(build_response(False, message=str(e), code=400)), 400
    except Exception as e:
        logger.error(f"Add error: {e}")
        return jsonify(build_response(False, message="Unexpected error", code=500)), 500


@app.route("/api/calculate/subtract", methods=["POST"])
def api_subtract() -> tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        a, b = _extract_numbers(data, ["a", "b"])
        result = get_calculator().subtract(a, b)
        return jsonify(build_response(True, data={"result": result, "operation": "subtract", "a": a, "b": b})), 200
    except (ValueError, InvalidInputError) as e:
        return jsonify(build_response(False, message=str(e), code=400)), 400
    except Exception as e:
        logger.error(f"Subtract error: {e}")
        return jsonify(build_response(False, message="Unexpected error", code=500)), 500


@app.route("/api/calculate/multiply", methods=["POST"])
def api_multiply() -> tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        a, b = _extract_numbers(data, ["a", "b"])
        result = get_calculator().multiply(a, b)
        return jsonify(build_response(True, data={"result": result, "operation": "multiply", "a": a, "b": b})), 200
    except (ValueError, InvalidInputError) as e:
        return jsonify(build_response(False, message=str(e), code=400)), 400
    except Exception as e:
        logger.error(f"Multiply error: {e}")
        return jsonify(build_response(False, message="Unexpected error", code=500)), 500


@app.route("/api/calculate/divide", methods=["POST"])
def api_divide() -> tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        a, b = _extract_numbers(data, ["a", "b"])
        result = get_calculator().divide(a, b)
        return jsonify(build_response(True, data={"result": result, "operation": "divide", "a": a, "b": b})), 200
    except DivisionByZeroError as e:
        return jsonify(build_response(False, message=str(e), code=400)), 400
    except (ValueError, InvalidInputError) as e:
        return jsonify(build_response(False, message=str(e), code=400)), 400
    except Exception as e:
        logger.error(f"Divide error: {e}")
        return jsonify(build_response(False, message="Unexpected error", code=500)), 500


@app.route("/api/calculate/power", methods=["POST"])
def api_power() -> tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        base, exp = _extract_numbers(data, ["base", "exp"])
        result = get_calculator().power(base, exp)
        return jsonify(build_response(True, data={"result": result, "operation": "power", "base": base, "exp": exp})), 200
    except (ValueError, InvalidInputError) as e:
        return jsonify(build_response(False, message=str(e), code=400)), 400
    except Exception as e:
        logger.error(f"Power error: {e}")
        return jsonify(build_response(False, message="Unexpected error", code=500)), 500


@app.route("/api/calculate/sqrt", methods=["POST"])
def api_sqrt() -> tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        n, = _extract_numbers(data, ["n"])
        result = get_calculator().sqrt(n)
        return jsonify(build_response(True, data={"result": result, "operation": "sqrt", "n": n})), 200
    except (ValueError, InvalidInputError) as e:
        return jsonify(build_response(False, message=str(e), code=400)), 400
    except Exception as e:
        logger.error(f"Sqrt error: {e}")
        return jsonify(build_response(False, message="Unexpected error", code=500)), 500


@app.route("/api/calculate/stats", methods=["POST"])
def api_stats() -> tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        values = data.get("values")
        if not isinstance(values, list) or not values:
            return jsonify(build_response(False, message="'values' must be a non-empty list", code=400)), 400
        for v in values:
            if not isinstance(v, (int, float)):
                return jsonify(build_response(False, message="All values must be numeric", code=400)), 400
        calc = get_calculator()
        result = {
            "mean": calc.mean(values),
            "median": calc.median(values),
            "count": len(values),
            "min": min(values),
            "max": max(values),
        }
        if len(values) >= 2:
            result["std_dev"] = calc.std_dev(values)
            result["variance"] = calc.variance(values)
        return jsonify(build_response(True, data=result)), 200
    except (ValueError, CalculatorError) as e:
        return jsonify(build_response(False, message=str(e), code=400)), 400
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify(build_response(False, message="Unexpected error", code=500)), 500


@app.route("/api/calculate/batch", methods=["POST"])
def api_batch() -> tuple[Response, int]:
    try:
        data = request.get_json(force=True) or {}
        operations = data.get("operations")
        if not isinstance(operations, list):
            return jsonify(build_response(False, message="'operations' must be a list", code=400)), 400
        if len(operations) > 50:
            return jsonify(build_response(False, message="Batch size cannot exceed 50 operations", code=400)), 400

        calc = get_calculator()
        results = []
        ALLOWED = {"add", "subtract", "multiply", "divide", "power", "sqrt", "modulo"}

        for i, op in enumerate(operations):
            op_name = op.get("operation")
            if op_name not in ALLOWED:
                results.append({"index": i, "success": False, "message": f"Unknown operation: {op_name}"})
                continue
            try:
                fn = getattr(calc, op_name)
                params = {k: v for k, v in op.items() if k != "operation"}
                result = fn(**params)
                results.append({"index": i, "operation": op_name, "result": result, "success": True})
            except CalculatorError as e:
                results.append({"index": i, "operation": op_name, "success": False, "message": str(e)})

        return jsonify(build_response(True, data={"results": results, "total": len(results)})), 200
    except Exception as e:
        logger.error(f"Batch error: {e}")
        return jsonify(build_response(False, message="Unexpected error", code=500)), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = ENV == "development"
    logger.info(f"Starting API v{APP_VERSION} on port {port} [{ENV}]")
    app.run(host="0.0.0.0", port=port, debug=debug)
