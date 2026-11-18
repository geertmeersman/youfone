"""Youfone API Client."""

from datetime import datetime, timedelta
import logging

import httpx

from .exceptions import BadCredentialsException, YoufoneServiceException

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://my.youfone.nl/api/prov"
API_HEADERS = {
    "authority": "my.youfone.nl",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://my.youfone.nl",
    "referer": "https://my.youfone.nl/inloggen",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


class YoufoneClient:
    """Class to communicate with the Youfone API."""

    def __init__(self, email, password, custom_headers=None, debug=False):
        """Initialize the API to get data."""
        self.email = email
        self.password = password
        self.client = None
        self.customer = None
        self.customer_id = None
        self.security_key = None
        self.custom_headers = custom_headers or {}
        self.debug = debug

    async def start_session(self):
        """Start the httpx session."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers=self.custom_headers,
                http2=True,
                verify=True,
                timeout=httpx.Timeout(20.0, read=10.0),
            )

    async def close_session(self):
        """Close the session."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self):
        """Async context manager enter method."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Async context manager exit method."""
        await self.close_session()

    async def request(
        self, method, path, data=None, return_json=True, expected_status=200
    ):
        """Send a request to the Youfone API."""
        if self.client is None:
            await self.start_session()

        endpoint_path = f"{API_BASE_URL}/{path}"
        headers = {**API_HEADERS, **self.custom_headers}

        if self.security_key:
            headers["securitykey"] = self.security_key

        response = None
        try:
            if method.lower() == "get":
                response = await self.client.get(endpoint_path, headers=headers)
            else:
                response = await self.client.post(
                    endpoint_path, json=data, headers=headers
                )

            if self.debug:
                _LOGGER.debug(
                    f"HTTP {method} {endpoint_path} - Status: {response.status_code}"
                )
                _LOGGER.debug(f"Request Headers: {headers}")
                _LOGGER.debug(f"Response Headers: {response.headers}")
                _LOGGER.debug(f"Response Content: {response.content}")

            if response.status_code == expected_status:
                if "securitykey" in response.headers:
                    self.security_key = response.headers["securitykey"]
                return response.json() if return_json else response.text()
            else:
                raise YoufoneServiceException(
                    f"Request to {endpoint_path} failed with status code {response.status_code}"
                )
        finally:
            if response:
                await response.aclose()

    async def login(self):
        """Log in to the Youfone API."""
        data = {"email": self.email, "password": self.password}
        result = await self.request("POST", "authentication/login", data)
        if result is False:
            raise BadCredentialsException("Login failed")
        return result

    async def get_available_cards(self):
        """Retrieve available cards for the Youfone customer."""
        return await self.request(
            "POST", "Card/GetAvailableCards", {"customerId": self.customer_id}
        )

    async def get_sim_only(self, data):
        """Retrieve SIM-only usage from the Youfone API."""
        return await self.request("POST", "Card/GetSimOnly", data)

    async def get_sim_only_roaming(self, data):
        """Retrieve SIM roaming bundle information from the Youfone API."""
        return await self.request("POST", "Card/GetSimOnlyRoaming", data)

    async def get_abonnement(self, data):
        """Retrieve SIM-only abonnement information from the Youfone API."""
        return await self.request("POST", "Products/SimOnly/GetAbonnement", data)

    def convert_camel_to_snake(self, name):
        """Convert a camelCase string to snake_case."""
        s1 = name[0].lower()
        for c in name[1:]:
            if c.isupper():
                s1 += "_" + c.lower()
            else:
                s1 += c
        return s1

    def percentage_elapsed(self, remaining_days):
        """Calculate the percentage elapsed in the current billing period."""
        current_datetime = datetime.now()
        end_datetime = datetime(
            current_datetime.year, current_datetime.month, current_datetime.day
        ) + timedelta(days=remaining_days)
        start_datetime = end_datetime - timedelta(days=30)
        period_length_seconds = (end_datetime - start_datetime).total_seconds()
        elapsed_time_seconds = (current_datetime - start_datetime).total_seconds()
        return round((elapsed_time_seconds / period_length_seconds) * 100, 2)

    def transform_sim_only_usage(self, json_data):
        """Transform SIM-only usage JSON into a typed dict per progress bar."""
        transformed_data = {}
        for progress_bar in json_data.get("progressBars", []):
            remaining_days = json_data.get("remainingDays", 0)
            period_percentage = self.percentage_elapsed(remaining_days)
            current = progress_bar.get("leftSideData", 0)
            max_value = progress_bar.get("rightSideData", 0)
            calculated_percentage = (
                round((current / max_value) * 100, 2) if max_value else 0.00
            )
            progress_bar_type = progress_bar.get("type", "").lower()
            if progress_bar_type:
                transformed_bar = {
                    "is_unlimited": progress_bar.get("isUnlimited", False),
                    "current": current,
                    "max": max_value,
                    "percentage": progress_bar.get("percentage", 0),
                    "calculated_percentage": calculated_percentage,
                    "remaining_days": remaining_days,
                    "period_percentage": period_percentage,
                    "alert": period_percentage < calculated_percentage,
                    "type": progress_bar_type,
                    "units": progress_bar.get("units", ""),
                }
                transformed_data[progress_bar_type] = {
                    self.convert_camel_to_snake(k): v
                    for k, v in transformed_bar.items()
                }
        return transformed_data

    def transform_roaming_usage(self, json_data):
        """Transform roaming usage JSON into a list of bundle dicts per section."""
        result = []
        for section in json_data.get("sections", []):
            for bar in section.get("progressBars", []):
                current = bar.get("leftSideData", 0)
                max_value = bar.get("rightSideData", 0)
                calculated_percentage = (
                    round((current / max_value) * 100, 2) if max_value else 0.00
                )
                due_date = bar.get("dueDate")
                remaining_days = (
                    (datetime.fromisoformat(due_date) - datetime.now()).days
                    if due_date
                    else None
                )
                result.append(
                    {
                        "name": section.get("name", ""),
                        "title": section.get("title", ""),
                        "is_unlimited": bar.get("isUnlimited", False),
                        "current": current,
                        "max": max_value,
                        "percentage": bar.get("percentage", 0),
                        "calculated_percentage": calculated_percentage,
                        "units": bar.get("units", ""),
                        "due_date": due_date,
                        "remaining_days": remaining_days,
                    }
                )
        return result

    async def fetch_data(self):
        """Get the customer data from the Youfone API."""
        try:
            self.customer = {
                self.convert_camel_to_snake(k): v
                for k, v in (await self.login()).items()
            }
            self.customer_id = self.customer.get("customer_id")
            sim_only = []
            sim_roaming = []
            if self.customer.get("has_simonly"):
                for card in await self.get_available_cards():
                    card_type = card.get("cardType")
                    if card_type == "SIM_ONLY":
                        for options in card.get("options"):
                            usage = await self.get_sim_only(options)
                            if usage:
                                subscription_info = await self.get_abonnement(options)
                                if subscription_info:
                                    sim_only.append(
                                        {
                                            "msisdn": options.get("msisdn", ""),
                                            "usage": self.transform_sim_only_usage(
                                                usage
                                            ),
                                            "subscription_info": {
                                                self.convert_camel_to_snake(k): v
                                                for k, v in subscription_info.get(
                                                    "generalInfo", ""
                                                ).items()
                                            },
                                        }
                                    )
                    elif card_type == "SIM_ROAMING":
                        for options in card.get("options"):
                            roaming = await self.get_sim_only_roaming(options)
                            if roaming:
                                sim_roaming.append(
                                    {
                                        "msisdn": options.get("msisdn", ""),
                                        "bundles": self.transform_roaming_usage(
                                            roaming
                                        ),
                                    }
                                )
        except Exception as e:
            error_message = e.args[0] if e.args else str(e)
            return {"error": error_message}
        return {
            "customer": self.customer,
            "sim_only": sim_only,
            "sim_roaming": sim_roaming,
        }
