"""Unit tests of Wallet."""
import unittest
from wallet import Wallet
from cash import *
# do we need to import Money?  It should be imported in cash.py.

# Include tests for withdraw method?
TEST_WITHDRAW = True
# Test that withdraw uses Greedy Algorithm?
TEST_GREEDY_WITHDRAW = True

# default currency
CURRENCY = "Baht"
CURRENCY2 = "Ringgit"


class BogusCash(Money):
    """Bogus Cash allows value to be zero or negative."""
    def __init__(self, value, currency):
        self._value = value
        self._currency = currency

    @property
    def value(self):
        return self._value

    @property
    def currency(self):
        return self._currency


class WalletTest(unittest.TestCase):

    def setUp(self):
        self.wallet = Wallet()

    def test_wallet_constructor(self):
        """A new Wallet should be empty."""
        self.assertTrue(self.wallet.is_empty())
        self.assertListEqual([], self.wallet.get_items())
    
    def test_new_wallet_value_is_zero(self):
        """Value of a new wallet should be Money(0,currency), not 0 (float)."""
        self.assertEqual(Money(0, CURRENCY), self.wallet.balance(CURRENCY))

    def test_deposit(self):
        """Can deposit a single item."""
        coin = Coin(5, CURRENCY)
        self.wallet.deposit(coin)
        self.assertFalse(self.wallet.is_empty())
        items = self.wallet.get_items()
        self.assertListEqual([coin], items)

    def test_deposit_decimal_values(self):
        """Can deposit a single item."""
        coin1 = Coin(0.25, CURRENCY)
        coin2 = Coin(0.50, CURRENCY)
        self.wallet.deposit(coin1)
        self.wallet.deposit(coin2)
        self.assertEqual(0.75, self.wallet.balance(CURRENCY).value)
        self.wallet.deposit(Banknote(1000, CURRENCY))
        self.assertEqual(1000.75, self.wallet.balance(CURRENCY).value)

    def test_deposit_multiple_items(self):
        """Can deposit multiple items. All succeed or all fail."""
        item1 = Coin(5, CURRENCY)
        item2 = Coin(10, CURRENCY2)
        item3 = Banknote(100, CURRENCY)
        # valid deposit
        self.assertListEqual([], self.wallet.get_items())
        self.wallet.deposit(item1, item2, item3)
        # order of items is not specified, so cannot use assertListEqual
        self.assertItemsEqual([item1, item2, item3], self.wallet.get_items())

        wallet = Wallet()
        baditem = Money(-1, CURRENCY)
        with self.assertRaises((ValueError,TypeError)):
            wallet.deposit(baditem, item1, item2)
        # should not deposit any of them
        self.assertEqual([], wallet.get_items())

        wallet = Wallet()
        with self.assertRaises((ValueError,TypeError)):
            wallet.deposit(item1, item2, item3, baditem)
        # should not deposit any of them
        self.assertEqual([], wallet.get_items())

        wallet = Wallet()
        with self.assertRaises((ValueError,TypeError)):
            wallet.deposit(item1, baditem, item2)
        # should not deposit any of them
        self.assertEqual([], wallet.get_items())

    def test_cannot_deposit_zero_value(self):
        """Should not be able to deposit Cash with zero value."""
        wallet = Wallet()
        with self.assertRaises(ValueError):
            bogus = BogusCash(0, "Baht")
            wallet.deposit(bogus)

    def test_can_deposit_new_kind_of_cash(self):
        """Wallet should accept any kind of cash, not just Coin and Banknote."""
        wallet = Wallet()
        bogo = BogusCash(1, "Baht")
        wallet.deposit(bogo)

    def test_balance_one_currency(self):
        """Test balance after deposits of a single currency."""
        self.wallet.deposit(Coin(10, CURRENCY))
        self.assertEqual(Money(10, CURRENCY), self.wallet.balance(CURRENCY))
        self.wallet.deposit(Coin(5, CURRENCY))
        self.assertEqual(Money(15, CURRENCY), self.wallet.balance(CURRENCY))
        self.wallet.deposit(Coin(5, CURRENCY))
        self.assertEqual(Money(20, CURRENCY), self.wallet.balance(CURRENCY))
        self.wallet.deposit(Banknote(100, CURRENCY))
        self.assertEqual(Money(120, CURRENCY), self.wallet.balance(CURRENCY))

    def test_balance_two_currencies(self):
        """Wallet accepts deposits of different currencies and balance computed for each currency."""
        self.wallet.deposit(Coin(10, CURRENCY))
        self.assertEqual(Money(10, CURRENCY), self.wallet.balance(CURRENCY))

        self.wallet.deposit(Coin(5, CURRENCY2))
        self.assertEqual(Money(10, CURRENCY), self.wallet.balance(CURRENCY))
        self.assertEqual(Money(5, CURRENCY2), self.wallet.balance(CURRENCY2))

        self.wallet.deposit(Coin(20, CURRENCY))
        self.assertEqual(Money(30, CURRENCY), self.wallet.balance(CURRENCY))

        self.wallet.deposit(Banknote(100, CURRENCY2))
        self.assertEqual(Money(105, CURRENCY2), self.wallet.balance(CURRENCY2))
        self.assertEqual(Money(30, CURRENCY), self.wallet.balance(CURRENCY))

    @unittest.skipIf(not TEST_WITHDRAW, "Skip tests of withdraw")
    def test_withdraw_single_currency(self):
        """withdraw when all items have same currency."""
        coin = Coin(5, CURRENCY)
        self.wallet.deposit(coin)
        withdrawn = self.wallet.withdraw(Money(5, CURRENCY))
        self.assertIsNotNone(withdrawn)
        self.assertListEqual([coin], withdrawn)
        self.assertIs(coin, withdrawn[0])  # should be exactly the same object
        self.assertEqual(0, self.wallet.balance(CURRENCY).value)
        self.assertTrue(self.wallet.is_empty())

        # deposit 3 items and then withdraw everything
        self.deposit_and_withdraw([5, 10, 20], 35, succeeds=True)
        self.assertTrue(self.wallet.is_empty())
        # deposit several items, withdraw all except the first one
        # choose values where greedy withdraw won't work
        self.wallet = Wallet()
        self.deposit_and_withdraw([1, 5, 10, 10], 25, succeeds=True)
        # withdraw all except the last one
        self.wallet = Wallet()
        self.deposit_and_withdraw([1, 25, 10, 5], 36, succeeds=True)

    @unittest.skipIf(not TEST_WITHDRAW, "Skip tests of withdraw")
    def test_withdraw_decimal_values(self):
        """Can deposit and withdraw fractional values."""
        self.wallet.deposit(Coin(0.25, CURRENCY))
        self.wallet.deposit(Coin(0.50, CURRENCY))
        self.wallet.deposit(Coin(0.50, CURRENCY))
        self.wallet.deposit(Banknote(100, CURRENCY))
        self.assertEqual(101.25, self.wallet.balance(CURRENCY).value)
        withdrawn = self.wallet.withdraw(Money(0.25, CURRENCY))
        value = sum(m.value for m in withdrawn)
        self.assertEqual(0.25, value)
        # check remaining balance in wallet
        self.assertEqual(101.0, self.wallet.balance(CURRENCY).value)
        # can withdraw 100 Baht + 0.50 Baht
        withdrawn = self.wallet.withdraw(Money(100.50, CURRENCY))
        value = sum(m.value for m in withdrawn)
        self.assertEqual(100.50, value)
        self.assertEqual(0.50, self.wallet.balance(CURRENCY).value)

    @unittest.skipIf(not TEST_WITHDRAW, "Skip tests of withdraw")
    def test_impossible_withdraw_single_currency(self):
        """Withdraw some values that are not possible, using single currency."""
        self.wallet = Wallet()
        self.assertIsNone(self.wallet.withdraw(Money(1, CURRENCY)), 
                          f"withdraw 1 {CURRENCY} from empty wallet" )
        self.deposit_and_withdraw([10,10,10], 25, succeeds=False)
        # wallet already contains [10,10,10]
        self.deposit_and_withdraw([2,2,2], 35, succeeds=False)

    @unittest.skipIf(not TEST_GREEDY_WITHDRAW, "Skip test for greedy withdraw algorithm")
    def test_withdraw_fails_using_greedy_algorithm(self):
        """Withdraw an amount that causes greedy algorithm to fail."""
        self.wallet = Wallet()
        self.deposit_and_withdraw([10, 2, 5, 2, 5, 2, 10], 11, succeeds=False)

    @unittest.skipIf(not TEST_WITHDRAW, "Skip tests of withdraw")
    def test_withdraw_multiple_currency(self):
        """withdraw when items have different currencies."""
        # pre-load items with alternate currency
        for value in [5, 10, 10, 100]:
            self.wallet.deposit(make_cash(value, CURRENCY2))
        # deposit in default currency, then withdraw a valid amount
        # this also tests the remaining value in wallet for the default current
        self.deposit_and_withdraw([10, 5, 5], 20, succeeds=True)

        # an amount that cannot be withdrawn in default currency
        self.deposit_and_withdraw([], 100, succeeds=False)
        self.deposit_and_withdraw([10], 20, succeeds=False)

    def deposit_and_withdraw(self, deposit_amounts, withdraw_amount, succeeds=True):
        """Utility function to perform tests involving deposit and withdraw.
           Raises an AssertionError if the status of withdraw does not match 
           the `succeeds` parameter value (withdraw succeeds or fails).
        
           :param deposit_amounts: list of values to deposit. Money instances are
                   created using the CURRENCY and deposited in wallet.
           :param withdraw_amount: value (number) to withdraw.
           :param succeeds:  whether the withdraw should succeed or fail.
        """
        # save the value of wallet for later comparison
        balance_value = self.wallet.balance(CURRENCY).value
        for amount in deposit_amounts:
            # arg is a number, create money with the default currency
            self.wallet.deposit(make_cash(amount, CURRENCY))
        balance_value += sum(deposit_amounts)
        # withdraw something and verify the remainder in wallet
        withdraw_money = Money(withdraw_amount, CURRENCY)
        withdrawn = self.wallet.withdraw(Money(withdraw_amount, CURRENCY))
        newbalance = self.wallet.balance(CURRENCY)
        if succeeds:
            self.assertIsNotNone(withdrawn)
            actual_amount = sum(item.value for item in withdrawn)
            self.assertEqual(withdraw_amount, actual_amount,
                             f"Withdrew {withdraw_money} but got "+str(withdrawn))
            for item in withdrawn:
                self.assertEqual(CURRENCY, item.currency,
                        f"Withdrew {withdraw_money} but got {item} (wrong currency)")
            # balance should be reduced by the amount withdrawn, of course
            # compare the value (instead of compare as Money) to avoid depending
            # on Money.__add__
            self.assertEqual(balance_value-withdraw_amount, newbalance.value)
        else:
            self.assertIsNone(withdrawn, f"withdraw({withdraw_money} should have failed")
            # balance should not change
            self.assertEqual(balance_value, newbalance.value)
        return withdrawn

    def assertItemsEqual(self, list1: list, list2: list):
        """Test that 2 lists contain the same items, not necessarily in same order.

        :raises AssertionError: if any items in one collection not in the other
        """
        # quick check
        if len(list1) != len(list2):
            raise AssertionError(f"{list1} != {list2}")
        list2copy = list2.copy()
        for item in list1:
            try:
                list2copy.remove(item)  # removes only first occurence of item
            except ValueError:
                # raised when item not in list2
                raise AssertionError(f"{item} not in {list2}")
        # Should not have any items remaining!
        if len(list2copy) > 0:
            raise AssertionError(f"Items not in first list: {list2copy}")


def make_cash(amount, currency):
    """Utility function to create various money objects."""
    if (amount >= 100 and amount%100 == 0) or (amount == 50):
        return Banknote(amount, currency)
    else:
        return Coin(amount, currency)


if __name__ == '__main__':
    unittest.main(verbosity=1)