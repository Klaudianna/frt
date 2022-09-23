from dataclasses import dataclass
from decimal import Decimal
import logging
from enum import IntEnum
from typing import Any, NewType


logger = logging.getLogger(__name__)


AccountNo = NewType("AccountNo", str)


class CountryNotSupportedException(Exception):
    pass


class AwardType(IntEnum):
    CASH = 1
    VOUCHER = 2


@dataclass(frozen=True)
class Cash50Eur:
    type: AwardType = AwardType.CASH
    points: int = 1000
    amount: int = 50


@dataclass(frozen=True)
class Voucher:
    type: AwardType = AwardType.VOUCHER
    points: int = 2000
    amount: int = 100
    description: str = "Amazon Gift Card"


class AbstractClass(object):
    pass


class BaseUser(AbstractClass):
    def __init__(self, points, id, account_no):
        self._points = points
        self.id = id
        self.account_no = account_no

    @property
    def points(self):
        return self._points

    def get_name(self):
        raise NotImplementedError

    def get_number_of_points(self):
        raise NotImplementedError

    def transfer_money(self, amount):
        raise NotImplementedError


class UserInGermany(BaseUser):
    def get_number_of_points(self):
        return 0

    def transfer_money(self, amount):
        print(f"Transfering {amount} to the user")


class UserInFrance(BaseUser):
    def transfer_money(self, amount):
        raise NotImplementedError

    def redeem_voucher(self, award_id):
        RedemptionService().redeem_voucher(award_id)


class PaymentGateway:
    def transfer(self, account_no: AccountNo, amount: Decimal) -> None:
        logger.info(f"Successfully transferred {amount} to {account_no}")


class RedemptionService:
    def __init__(self, payment_gateway) -> None:
        self._payment_gateway = payment_gateway

    def redeem(self, user, award) -> Any:
        # Assumption: user will redeem `amount` of money.
        # We're not supporting other types of awards.
        try:
            if isinstance(user, UserInFrance):
                logger.info(f"Redeemed {award}, for a {user}")
                return self.redeem_voucher(user, award)
            else:
                if user.points > award.points:
                    if award.type is AwardType.CASH:
                        self._payment_gateway(user.account_no, award.amount)
                        logger.info(f"Redeemed {award}, for a {user}")
                        return True
        except CountryNotSupportedException:
            return False
        else:
            return False

    def redeem_voucher(self, user, award):
        if not isinstance(user, UserInFrance) or award.type == AwardType.CASH:
            raise CountryNotSupportedException()
        return f"Here is your {award.description}"
