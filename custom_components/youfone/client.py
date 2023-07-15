"""Youfone API Client."""
from __future__ import annotations

from calendar import monthrange
from datetime import datetime
import logging

import httpx

from .const import (
    BASE_HEADERS,
    CONNECTION_RETRY,
    DEFAULT_COUNTRY,
    DEFAULT_YOUFONE_ENVIRONMENT,
)
from .exceptions import BadCredentialsException, YoufoneServiceException
from .models import YoufoneEnvironment, YoufoneItem
from .utils import format_entity_name, str_to_float

_LOGGER = logging.getLogger(__name__)


class YoufoneClient:
    """Youfone client."""

    environment: YoufoneEnvironment

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        country: str | None = None,
        headers: dict | None = BASE_HEADERS,
        environment: YoufoneEnvironment = DEFAULT_YOUFONE_ENVIRONMENT,
    ) -> None:
        """Initialize YoufoneClient."""
        self.username = username
        self.password = password
        self.environment = environment
        self.country = country
        self._headers = headers
        self.securitykey = None
        self.user_details = None
        self.request_error = {}
        if country != DEFAULT_COUNTRY:
            self.environment.api_endpoint = self.environment.api_endpoint.replace(
                "youfone.be", f"youfone.{country}"
            )

    def request(
        self,
        url,
        caller="Not set",
        data=None,
        expected="200",
        log=False,
        retrying=False,
        connection_retry_left=CONNECTION_RETRY,
    ) -> dict:
        """Send a request to Youfone."""
        headers = self._headers
        headers.update(
            {
                "referer": f"https://my.youfone.{self.country}/login",
            }
        )
        if self.securitykey is not None:
            headers.update(
                {
                    "securitykey": self.securitykey,
                }
            )

        client = httpx.Client(http2=True)
        if data is None:
            _LOGGER.debug(f"{caller} Calling GET {url}")
            response = client.get(url, headers=headers)
        else:
            _LOGGER.debug(f"{caller} Calling POST {url} with {data}")
            response = client.post(url, data=data, headers=headers)
        _LOGGER.debug(
            f"{caller} http status code = {response.status_code} (expecting {expected})"
        )
        _LOGGER.debug(f"{caller} Response:\n{response.text}")
        if expected is not None and response.status_code != expected:
            if response.status_code == 404:
                self.request_error = response.json()
                return False
            if (
                response.status_code != 403
                and response.status_code != 401
                and response.status_code != 500
                and connection_retry_left > 0
                and not retrying
            ):
                raise YoufoneServiceException(
                    f"[{caller}] Expecting HTTP {expected} | Response HTTP {response.status_code}, Response: {response.text}, Url: {response.url}"
                )
            _LOGGER.debug(
                f"[YoufoneClient|request] Received a HTTP {response.status_code}, nothing to worry about! We give it another try :-)"
            )
            self.login()
            response = self.request(
                url, caller, data, expected, log, True, connection_retry_left - 1
            )
        return response

    def login(self) -> dict:
        """Start a new Youfone session with a user & password."""
        _LOGGER.debug("[YoufoneClient|login|start]")
        """Login process"""
        if self.username is None or self.password is None:
            raise BadCredentialsException("Username or Password cannot be empty")
        response = self.request(
            f"{self.environment.api_endpoint}/login",
            "[YoufoneClient|login|authenticate]",
            '{"request": {"Login": "'
            + self.username
            + '", "Password": "'
            + self.password
            + '"}}',
            None,
        )
        result = response.json()
        if result.get("ResultCode") != 0:
            raise BadCredentialsException(response.text)
        self.user_details = result.get("Object")
        self.securitykey = response.headers.get("securitykey")
        return True

    def fetch_data(self):
        """Fetch Youfone data."""
        data = {}

        now = datetime.now()
        if not self.login():
            return False

        customer = self.user_details.get("Customer")
        customers = self.user_details.get("Customers")
        user_id = customer.get("Id")
        personal_info = self.personal_info(user_id)
        if not personal_info:
            return data

        device_key = format_entity_name(f"{user_id} user")
        device_name = f"{customer.get('FirstName')} {customer.get('LastName')} Account"
        device_model = "Useraccount"
        key = format_entity_name(f"{user_id} user")
        data[key] = YoufoneItem(
            country=self.country,
            name=device_name,
            key=key,
            type="profile",
            device_key=device_key,
            device_name=device_name,
            device_model=device_model,
            state=user_id,
            extra_attributes=personal_info,
        )

        device_key = format_entity_name(f"{user_id} youcoins")
        device_name = f"{customer.get('FirstName')} {customer.get('LastName')} Youcoins"
        device_model = "Youcoins"

        youcoins_token = self.youcoins_token(user_id)
        if youcoins_token:
            balance = self.youcoins_balance(youcoins_token)
            if balance is not False:
                key = format_entity_name(f"{user_id} youcoins")
                data[key] = YoufoneItem(
                    country=self.country,
                    name="Youcoins",
                    key=key,
                    type="coins",
                    device_key=device_key,
                    device_name=device_name,
                    device_model=device_model,
                    state=balance.get("Current"),
                    extra_attributes=balance,
                )
                key = format_entity_name(f"{user_id} youcoins pending")
                data[key] = YoufoneItem(
                    country=self.country,
                    name="Youcoins pending",
                    key=key,
                    type="coins_pending",
                    device_key=device_key,
                    device_name=device_name,
                    device_model=device_model,
                    state=balance.get("Pending"),
                    extra_attributes=balance,
                )
                propositions = self.youcoins_propositions(youcoins_token)
                if propositions:
                    for proposition in propositions:
                        key = format_entity_name(
                            f"{user_id} youcoins proposition {proposition.get('Id')}"
                        )
                        data[key] = YoufoneItem(
                            country=self.country,
                            name=f"{proposition.get('DisplayName')}",
                            key=key,
                            type="coins_proposition",
                            device_key=device_key,
                            device_name=device_name,
                            device_model=device_model,
                            state=proposition.get("Price"),
                            extra_attributes=proposition,
                        )

        device_key = format_entity_name(f"{user_id} invoices")
        device_name = f"{customer.get('FirstName')} {customer.get('LastName')} Invoices"
        device_model = "Invoices"

        invoices = self.invoices(user_id)
        if not invoices:
            return data
        for invoice in invoices.get("Invoices"):
            key = format_entity_name(
                f"{user_id} invoice {invoice.get('InvoiceNumber')}"
            )
            data[key] = YoufoneItem(
                country=self.country,
                name=f"{invoice.get('InvoiceDateFormatted')} - {invoice.get('Status')}",
                key=key,
                type="euro",
                device_key=device_key,
                device_name=device_name,
                device_model=device_model,
                state=str_to_float(
                    invoice.get("InvoiceAmountFormatted").replace("€ ", "")
                ),
                extra_attributes=invoice,
            )

        for customer_a in customers:
            msisdn = customer_a.get("Msisdn")
            msisdn_info = self.msisdn_info(msisdn)
            if not msisdn_info:
                return data
            abonnement_msisdn_info = self.abonnement_msisdn_info(msisdn)
            if not abonnement_msisdn_info:
                return data
            device_key = format_entity_name(f"msisdn {msisdn}")
            device_name = (
                f"{customer.get('FirstName')} {customer.get('LastName')} {msisdn}"
            )
            device_model = "Msisdn"

            for property in abonnement_msisdn_info + msisdn_info:
                properties = {}
                for property_list in property.get("Properties"):
                    properties.update(
                        {property_list.get("Key"): property_list.get("Value")}
                    )
                if property.get("SectionId") == 1:
                    key = format_entity_name(f"{msisdn} data")
                    if (
                        "_isUnlimited" in properties
                        and properties.get("_isUnlimited") == "1"
                    ):
                        state = 0
                    else:
                        state = (
                            100
                            * str_to_float(properties.get("UsedAmount"))
                            / str_to_float(properties.get("BundleDurationWithUnits"))
                        )

                    data[key] = YoufoneItem(
                        country=self.country,
                        name="Data",
                        key=key,
                        type="usage_percentage_data",
                        device_key=device_key,
                        device_name=device_name,
                        device_model=device_model,
                        state=state,
                        extra_attributes=properties,
                    )
                elif property.get("SectionId") == 2:
                    key = format_entity_name(f"{msisdn} voice sms")
                    if (
                        "_isUnlimited" in properties
                        and properties.get("_isUnlimited") == "1"
                    ):
                        state = 0
                    else:
                        state = (
                            100
                            * str_to_float(properties.get("UsedAmount"))
                            / str_to_float(properties.get("BundleDurationWithUnits"))
                        )
                    data[key] = YoufoneItem(
                        country=self.country,
                        name="Voice Sms",
                        key=key,
                        type="usage_percentage_voice_sms",
                        device_key=device_key,
                        device_name=device_name,
                        device_model=device_model,
                        state=state,
                        extra_attributes=properties,
                    )
                elif property.get("SectionId") == 3:
                    key = format_entity_name(f"{msisdn} remaining days")
                    days_in_month = monthrange(now.year, now.month)[1]
                    first_of_month = datetime(now.year, now.month, 1)
                    seconds_in_month = days_in_month * 86400
                    seconds_completed = (now - first_of_month).total_seconds()
                    period_percentage_completed = round(
                        100 * seconds_completed / seconds_in_month, 1
                    )
                    period_percentage_remaining = 100 - period_percentage_completed
                    _LOGGER.debug(f"days_in_month: {days_in_month}")
                    data[key] = YoufoneItem(
                        country=self.country,
                        name="Remaining days",
                        key=key,
                        type="remaining_days",
                        device_key=device_key,
                        device_name=device_name,
                        device_model=device_model,
                        state=properties.get("NumberOfRemainingDays"),
                        extra_attributes=properties
                        | {
                            "period_percentage_completed": period_percentage_completed,
                            "period_percentage_remaining": period_percentage_remaining,
                            "days_in_period": days_in_month,
                        },
                    )
                elif property.get("SectionId") == 21:
                    key = format_entity_name(f"{msisdn} abonnement type")
                    data[key] = YoufoneItem(
                        country=self.country,
                        name=properties.get("AbonnementType").replace("<br/>", " - "),
                        key=key,
                        type="euro",
                        device_key=device_key,
                        device_name=device_name,
                        device_model=device_model,
                        state=properties.get("Price").replace(",-", ""),
                        extra_attributes=properties,
                    )
                elif property.get("SectionId") == 23:
                    key = format_entity_name(f"{msisdn} sim info")
                    data[key] = YoufoneItem(
                        country=self.country,
                        name=properties.get("Msisdn"),
                        key=key,
                        type="sim",
                        device_key=device_key,
                        device_name=device_name,
                        device_model=device_model,
                        state=properties.get("MsisdnStatus"),
                        extra_attributes=properties,
                    )
                elif property.get("SectionId") == 24:
                    key = format_entity_name(f"{msisdn} data subscription")
                    data[key] = YoufoneItem(
                        country=self.country,
                        name="Data subscription",
                        key=key,
                        type="data",
                        device_key=device_key,
                        device_name=device_name,
                        device_model=device_model,
                        state=properties.get("DataSubscription"),
                    )
                elif property.get("SectionId") == 26:
                    key = format_entity_name(f"{msisdn} voice sms subscription")
                    data[key] = YoufoneItem(
                        country=self.country,
                        name="Voice Sms subscription",
                        key=key,
                        type="voice_sms",
                        device_key=device_key,
                        device_name=device_name,
                        device_model=device_model,
                        state=properties.get("VoiceSmsSubscription"),
                    )
        return data

    def personal_info(self, customer_id):
        """Get personal info."""
        response = self.request(
            f"{self.environment.api_endpoint}/GetCustomerPersonalInfo",
            "personal_info",
            '{"request":{"CustomerId":' + str(customer_id) + "}}",
            200,
        )
        result = response.json()
        if result.get("ResultCode") != 0:
            return False
        return result.get("Object")

    def msisdn_info(self, msisdn):
        """Get personal info."""
        response = self.request(
            f"{self.environment.api_endpoint}/GetOverviewMsisdnInfo",
            "msisdn_info",
            '{"request":{"Msisdn":' + str(msisdn) + "}}",
            200,
        )
        result = response.json()
        if result.get("ResultCode") != 0:
            return False
        return result.get("Object")

    def abonnement_msisdn_info(self, msisdn):
        """Get personal info."""
        response = self.request(
            f"{self.environment.api_endpoint}/GetAbonnementMsisdnInfo",
            "abonnement_msisdn_info",
            '{"request":{"Msisdn":' + str(msisdn) + "}}",
            200,
        )
        result = response.json()
        if result.get("ResultCode") != 0:
            return False
        return result.get("Object")

    def invoices(self, customer_id):
        """Get personal info."""
        response = self.request(
            f"{self.environment.api_endpoint}/GetInvoicesByCustomerId",
            "invoices",
            '{"request":{"CustomerId":' + str(customer_id) + "}}",
            200,
        )
        result = response.json()
        if result.get("ResultCode") != 0:
            return False
        return result.get("Object")

    def youcoins_token(self, customer_id):
        """Get YouCoins Token."""
        response = self.request(
            f"{self.environment.api_endpoint}/GetYoucoinsToken",
            "youcoins",
            '{"request":{"CustomerId":' + str(customer_id) + "}}",
            200,
        )
        result = response.json()
        if result.get("ResultCode") != 0:
            return False
        return result.get("Object")

    def youcoins_balance(self, token):
        """Get Youcoins balance."""
        response = self.request(
            f"https://my.youfone.be/prov/PartnerAPI/CustomerService.svc/customer?data={token}&connectId=1",
            "youcoins",
            None,
            None,
        )
        if response.status_code != 200:
            return False
        result = response.json()
        if result.get("Balance") is not None:
            return result.get("Balance")
        return False

    def youcoins_propositions(self, token):
        """Get Youcoins Propositions."""
        response = self.request(
            f"https://my.youfone.be/prov/PartnerAPI/CustomerService.svc/propositions?data={token}&connectId=1",
            "youcoins",
            None,
            200,
        )
        result = response.json()
        if len(result):
            return result
        return False
