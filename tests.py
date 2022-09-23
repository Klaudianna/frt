import random
import string
from decimal import Decimal
from unittest import TestCase, mock

from .redemptions import (
    AccountNo,
    BaseUser,
    Cash50Eur,
    PaymentGateway,
    RedemptionService,
    UserInFrance,
    UserInGermany,
    Voucher,
    logger,
)


class UserFactory:
    @staticmethod
    def create(points=None, user_de=True) -> BaseUser:
        user_id = "".join(random.choices((string.ascii_letters + string.digits), k=5))
        account_no = "".join(random.choices(string.digits, k=20))
        _points = points or random.randint(100, 10000)
        user_class = UserInGermany if user_de else UserInFrance
        return user_class(id=user_id, account_no=AccountNo(account_no), points=_points)


class TestRedemptionService(TestCase):
    def setUp(self) -> None:
        self.payment_gateway = mock.create_autospec(PaymentGateway)
        self.redemption_service = RedemptionService(
            payment_gateway=self.payment_gateway,
        )

    def test_logs_user_redemption(self) -> None:
        user = UserFactory.create(points=3000)
        award = Cash50Eur()
        with self.assertLogs(logger=logger) as log:
            self.redemption_service.redeem(user, award)
        self.assertIn(f"Redeemed {award}, for a {user}", log.output[0])

    def test_uses_payment_gateway_to_transfer_money_to_user(self) -> None:
        user = UserFactory.create()
        award = Cash50Eur()
        self.redemption_service.redeem(user, award)
        self.payment_gateway.assert_called_once_with(user.account_no, award.amount)

    def test_user_in_de(self):
        user_in_de = UserFactory.create(points=5000)
        award = Cash50Eur()
        self.assertTrue(self.redemption_service.redeem(user_in_de, award))

    def test_negative_case(self):
        user_in_de = UserFactory.create(points=10)
        award = Cash50Eur()
        self.assertFalse(self.redemption_service.redeem(user_in_de, award))

    def test_negative_case_voucher(self):
        user_in_de = UserFactory.create(points=5000)
        self.assertFalse(self.redemption_service.redeem(user_in_de, Voucher()))

    def test_user_in_FR(self):
        user_in_fr = UserFactory.create(points=10000, user_de=False)
        self.assertTrue(self.redemption_service.redeem(user_in_fr, Voucher()))

    def test_user_in_FR_negative_cash(self):
        user_in_fr = UserFactory.create(points=10000, user_de=False)
        award = Cash50Eur()
        self.assertFalse(self.redemption_service.redeem(user_in_fr, award))


class TestPaymentGateway(TestCase):
    def test_has_transfer_method(self) -> None:
        account_no = UserFactory.create().account_no
        with self.assertLogs(logger) as log:
            PaymentGateway().transfer(account_no, Decimal(100))
        self.assertIn(
            f"Successfully transferred 100 to {account_no}",
            log.output[0],
        )
