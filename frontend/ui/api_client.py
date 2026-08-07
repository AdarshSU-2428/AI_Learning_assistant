import os
import requests


class APIClientError(Exception):
    """Base exception for API client errors."""
    pass


class BackendConnectionError(APIClientError):
    """Raised when the frontend cannot connect to FastAPI."""
    pass


class BackendTimeoutError(APIClientError):
    """Raised when FastAPI takes too long to respond."""
    pass


class BackendResponseError(APIClientError):
    """Raised when FastAPI returns a 4xx or 5xx response."""
    pass


class InvalidBackendResponseError(APIClientError):
    """Raised when FastAPI returns an unexpected response structure."""
    pass


class APIClient:
    def __init__(self, base_url=None, timeout=60):
        self.base_url = (
            base_url
            or os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
        ).rstrip("/")

        self.timeout = timeout

    def send_message(self, query, subject=None):
        try:
            payload = {"query": query}
            if subject:
                payload["subject"] = subject

            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.timeout,
            )

        except requests.exceptions.Timeout as exc:
            raise BackendTimeoutError("The AI backend took too long to respond.") from exc

        except requests.exceptions.ConnectionError as exc:
            raise BackendConnectionError("Unable to connect to the AI backend.") from exc

        except requests.exceptions.RequestException as exc:
            raise APIClientError("An error occurred while communicating with the AI backend.") from exc

        if not response.ok:
            message = self._extract_error_message(response)
            raise BackendResponseError(message)

        try:
            data = response.json()

        except requests.exceptions.JSONDecodeError as exc:
            raise InvalidBackendResponseError(
                "Backend returned an invalid JSON response."
            ) from exc

        return self._validate_response(data)

    def _validate_response(self, data):
        if not isinstance(data, dict):
            raise InvalidBackendResponseError("Backend response must be a JSON object.")

        required_fields = {
            "query": str,
            "answer": str,
            "sources": list,
        }

        for field, expected_type in required_fields.items():

            if field not in data:
                raise InvalidBackendResponseError(f"Backend response is missing required field: '{field}'.")

            if not isinstance(data[field], expected_type):
                raise InvalidBackendResponseError(f"Backend field '{field}' has an invalid type.")

        if not data["answer"].strip():
            raise InvalidBackendResponseError("Backend returned an empty answer.")

        return data

    def _extract_error_message(self, response):
        try:
            data = response.json()

            detail = data.get("detail")

            if isinstance(detail, str) and detail.strip():
                return detail

        except (requests.exceptions.JSONDecodeError, ValueError):
            pass

        return f"Backend returned HTTP {response.status_code}."
