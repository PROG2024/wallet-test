"""Tests of Coin and Banknote"""
import unittest
import datetime
from cash import Coin, Banknote
# Money should already be imported (from cash), but protect against unusual code
from money import Money


class CoinTest(unittest.TestCase):

    def test_coin_is_money(self):
        """Coin is a kind of Money, but not a Banknote."""
        c = Coin(1, "Baht")
        self.assertIsInstance(c, Money)
        self.assertNotIsInstance(c, Banknote)

    def test_coin_with_fractional_value(self):
        """Coin may have a value less than one, e.g. 0.01, 0.25, or 2.5."""
        c = Coin(0.01, "Baht")
        self.assertEqual(0.01, c.value)
        # weird, but spec doesn't forbid this
        c = Coin(2.50, "Baht")
        self.assertEqual(2.50, c.value)
        # there should be no minimum
        c = Coin(0.000001, "Bitcoin")
        self.assertEqual(0.000001, c.value)

    def test_coin_has_year(self):
        """Coin has a year property that is the year minted (i.e. created)."""
        c = Coin(5, "Ringgit")
        year = datetime.date.today().year
        self.assertEqual(year, c.year)
    
    def test_coin_year_is_readonly(self):
        """Year should be a readonly property."""
        c = Coin(5, "Baht")
        with self.assertRaises(AttributeError):
            c.year = 2000

    def test_coin_has_positive_value(self):
        """Coin constructor should not allow non-positive values."""
        for value in [0, -0.5, -1, -10]:
            with self.assertRaises(ValueError):
                 c = Coin(value, "Ringgit",
                          f"Coin({value},'Ringgit') should raise ValueError")

    def test_add_returns_money(self):
        """You can add Coins, but the result is Money not Coin."""
        result = Coin(5, "Baht") + Coin(10, "Baht")
        self.assertIsInstance(result, Money)
        self.assertNotIsInstance(result, Coin, "Result of coin+coin should be Money")
        self.assertEqual(15, result.value)
        self.assertEqual("Baht", result.currency)

    def test_add_coin_and_money(self):
        """You can add coin and money. The result is Money (not Coin)."""
        for (value1, value2, sum_value) in [(1,-1,0), (5,0,5), (10,-4, 6)]:
            result = Coin(value1, "Baht") + Money(value2, "Baht")
            self.assertIsInstance(result, Money)
            self.assertNotIsInstance(result, Coin, "Result of cash+cash should be Money")
            self.assertEqual(sum_value, result.value)
            # try adding in opposite order
            result2 = Money(value2, "Baht") + Coin(value1, "Baht")
            self.assertIsInstance(result2, Money)
            self.assertEqual(result, result2)


class BanknoteTest(unittest.TestCase):

    def test_banknote_is_money(self):
        """Banknote is a kind of Money, but not a Coin."""
        c = Banknote(100, "Baht")
        self.assertIsInstance(c, Money)
        self.assertNotIsInstance(c, Coin)

    def test_banknote_has_year(self):
        """Banknote has a year property that is the year minted."""
        c = Banknote(100, "Ringgit")
        year = datetime.date.today().year
        self.assertEqual(year, c.year)
    
    def test_banknote_year_is_readonly(self):
        """Year should be a readonly property."""
        c = Banknote(100, "Baht")
        with self.assertRaises(AttributeError):
            c.year = 2000

    def test_banknote_has_positive_value(self):
        """Constructor should not allow non-positive values."""
        for value in [0, -10, -50, -100]:
            with self.assertRaises(ValueError):
                c = Banknote(value, "Ringgit",
                             f"Banknote({value},'Ringgit') should raise ValueError")

    def test_banknote_valid_values(self):
        """Value can by any 1, 2, or 5 x power of 10."""
        # these should all succeed
        for multiple in (1, 2, 5):
            for base in (1, 10, 100, 1000, 1000000):
                value = multiple*base
                note = Banknote(value, "Eth")
                self.assertEqual(value, note.value, 
                            f"Banknote({value},'Eth') has value {note.value}")

    def test_banknote_invalid_values(self):
        """Banknotes cannot have arbitrary values."""
        for value in [0.5, 3, 10.5, 4000, 9000000]:
            with self.assertRaises(ValueError):
                banknote = Banknote(value, "Ringgit")

    def test_banknote_must_have_currency(self):
        """Banknote must have a non-empty string currency."""
        with self.assertRaises(ValueError):
            c = Banknote(100, "")
    
    def test_add_returns_money(self):
        """You can add cash, but the result is Money not Cash."""
        result = Banknote(50, "Baht") + Banknote(10, "Baht")
        self.assertIsInstance(result, Money)
        self.assertNotIsInstance(result, Banknote, "Result of cash+cash should be Money")
        self.assertEqual(60, result.value)
        self.assertEqual("Baht", result.currency)

    def test_add_banknote_and_money(self):
        """You can add banknote and money. The result is Money (not Banknote)."""
        for (value1, value2, sum_value) in [(100,-100,0), (500,0,500), (100,-40, 60)]:
            result = Banknote(value1, "Baht") + Money(value2, "Baht")
            self.assertIsInstance(result, Money)
            self.assertNotIsInstance(result, Banknote, "Result of cash+cash should be Money")
            self.assertEqual(sum_value, result.value)
            # try adding in opposite order
            result2 = Money(value2, "Baht") + Banknote(value1, "Baht")
            self.assertIsInstance(result2, Money)
            self.assertEqual(result, result2)
