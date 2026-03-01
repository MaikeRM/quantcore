"""
Tests for quantcore.core.time module.

Covers:
  - Date: construction, arithmetic, comparison, hashing, string repr
  - Calendar: abstract contract + concrete WeekendCalendar helper
  - DayCounter: Actual365 and Bus252 conventions
"""

import datetime as dt
import pytest
from quantcore.core.time.date import Date
from quantcore.core.time.calendar import Calendar
from quantcore.core.time.daycount import DayCounter, Actual365, Bus252


# ── Concrete Calendar for testing ────────────────────────────────────

class WeekendOnlyCalendar(Calendar):
    """Calendar where weekends are the only non-business days."""

    def is_business_day(self, date: Date) -> bool:
        return not self.is_weekend(date)

    def is_holiday(self, date: Date) -> bool:
        return False  # no holidays, only weekends


class BrazilSimpleCalendar(Calendar):
    """Calendar with weekends + a fixed holiday for testing."""

    HOLIDAYS = {
        dt.date(2024, 1, 1),   # Ano Novo
        dt.date(2024, 9, 7),   # Independência
        dt.date(2024, 12, 25), # Natal
    }

    def is_business_day(self, date: Date) -> bool:
        return not self.is_holiday_or_weekend(date)

    def is_holiday(self, date: Date) -> bool:
        return date.to_datetime() in self.HOLIDAYS


# ═══════════════════════════════════════════════════════════════════════
# Date tests
# ═══════════════════════════════════════════════════════════════════════

class TestDate:
    """Tests for quantcore.core.time.date.Date."""

    def test_construction(self):
        d = Date(2024, 3, 15)
        assert d.year == 2024
        assert d.month == 3
        assert d.day == 15

    def test_from_datetime(self):
        py_date = dt.date(2024, 6, 1)
        d = Date.from_datetime(py_date)
        assert d.year == 2024
        assert d.month == 6
        assert d.day == 1

    def test_to_datetime(self):
        d = Date(2024, 6, 1)
        assert d.to_datetime() == dt.date(2024, 6, 1)

    def test_subtraction_positive(self):
        d1 = Date(2024, 1, 1)
        d2 = Date(2024, 1, 31)
        assert d2 - d1 == 30

    def test_subtraction_negative(self):
        d1 = Date(2024, 1, 31)
        d2 = Date(2024, 1, 1)
        assert d2 - d1 == -30

    def test_subtraction_same_date(self):
        d = Date(2024, 6, 15)
        assert d - d == 0

    def test_addition(self):
        d = Date(2024, 1, 1)
        result = d + 10
        assert result == Date(2024, 1, 11)

    def test_addition_cross_month(self):
        d = Date(2024, 1, 30)
        result = d + 5
        assert result == Date(2024, 2, 4)

    def test_addition_leap_year(self):
        d = Date(2024, 2, 28)
        result = d + 1
        assert result == Date(2024, 2, 29)  # 2024 is leap year

    def test_addition_non_leap_year(self):
        d = Date(2023, 2, 28)
        result = d + 1
        assert result == Date(2023, 3, 1)  # 2023 is NOT leap year

    def test_less_than(self):
        d1 = Date(2024, 1, 1)
        d2 = Date(2024, 1, 2)
        assert d1 < d2
        assert not d2 < d1

    def test_less_than_equal_dates(self):
        d = Date(2024, 6, 15)
        assert not d < d

    def test_equality(self):
        d1 = Date(2024, 3, 15)
        d2 = Date(2024, 3, 15)
        assert d1 == d2

    def test_inequality(self):
        assert Date(2024, 1, 1) != Date(2024, 1, 2)

    def test_equality_with_non_date(self):
        d = Date(2024, 1, 1)
        assert d != "2024-01-01"
        assert d != 42
        assert d != None

    def test_hash_consistency(self):
        d1 = Date(2024, 3, 15)
        d2 = Date(2024, 3, 15)
        assert hash(d1) == hash(d2)
        # Can be used as dict key
        mapping = {d1: "test"}
        assert mapping[d2] == "test"

    def test_hash_uniqueness(self):
        d1 = Date(2024, 1, 1)
        d2 = Date(2024, 1, 2)
        assert hash(d1) != hash(d2)

    def test_str(self):
        d = Date(2024, 3, 15)
        assert str(d) == "2024-03-15"

    def test_repr(self):
        d = Date(2024, 3, 15)
        assert repr(d) == "Date(2024, 3, 15)"

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            Date(2024, 2, 30)  # Feb 30 doesn't exist

    def test_invalid_month_raises(self):
        with pytest.raises(ValueError):
            Date(2024, 13, 1)

    def test_set_membership(self):
        """Dates should work in sets via __hash__ and __eq__."""
        s = {Date(2024, 1, 1), Date(2024, 1, 1), Date(2024, 1, 2)}
        assert len(s) == 2


# ═══════════════════════════════════════════════════════════════════════
# Calendar tests
# ═══════════════════════════════════════════════════════════════════════

class TestCalendar:
    """Tests for quantcore.core.time.calendar.Calendar."""

    @pytest.fixture
    def cal(self):
        return WeekendOnlyCalendar()

    @pytest.fixture
    def br_cal(self):
        return BrazilSimpleCalendar()

    # ── is_weekend ────────────────────────────────────────────────────

    def test_is_weekend_saturday(self, cal):
        saturday = Date(2024, 3, 16)  # Saturday
        assert cal.is_weekend(saturday)

    def test_is_weekend_sunday(self, cal):
        sunday = Date(2024, 3, 17)  # Sunday
        assert cal.is_weekend(sunday)

    def test_is_weekend_weekday(self, cal):
        monday = Date(2024, 3, 18)  # Monday
        assert not cal.is_weekend(monday)

    # ── is_business_day ───────────────────────────────────────────────

    def test_is_business_day_weekday(self, cal):
        assert cal.is_business_day(Date(2024, 3, 18))  # Monday

    def test_is_business_day_weekend(self, cal):
        assert not cal.is_business_day(Date(2024, 3, 16))  # Saturday

    # ── is_holiday_or_weekend ─────────────────────────────────────────

    def test_is_holiday_or_weekend_weekend(self, br_cal):
        assert br_cal.is_holiday_or_weekend(Date(2024, 3, 16))  # Saturday

    def test_is_holiday_or_weekend_holiday(self, br_cal):
        assert br_cal.is_holiday_or_weekend(Date(2024, 1, 1))  # Ano Novo (Monday)

    def test_is_holiday_or_weekend_weekday(self, br_cal):
        assert not br_cal.is_holiday_or_weekend(Date(2024, 3, 18))  # Normal Monday

    # ── add_business_days ─────────────────────────────────────────────

    def test_add_business_days_within_week(self, cal):
        monday = Date(2024, 3, 18)
        result = cal.add_business_days(monday, 3)
        assert result == Date(2024, 3, 21)  # Thursday

    def test_add_business_days_crosses_weekend(self, cal):
        friday = Date(2024, 3, 15)
        result = cal.add_business_days(friday, 1)
        assert result == Date(2024, 3, 18)  # Monday

    def test_add_business_days_multiple_weeks(self, cal):
        monday = Date(2024, 3, 18)
        result = cal.add_business_days(monday, 10)
        # 10 biz days = 2 weeks → April 1
        assert result == Date(2024, 4, 1)

    def test_add_business_days_negative(self, cal):
        friday = Date(2024, 3, 22)
        result = cal.add_business_days(friday, -5)
        assert result == Date(2024, 3, 15)  # Previous Friday

    def test_add_business_days_zero(self, cal):
        monday = Date(2024, 3, 18)
        result = cal.add_business_days(monday, 0)
        assert result == monday

    def test_add_business_days_skips_holiday(self, br_cal):
        # Sep 6, 2024 is Friday; Sep 7 is holiday (Saturday), Sep 9 Monday
        fri = Date(2024, 9, 6)
        result = br_cal.add_business_days(fri, 1)
        assert result == Date(2024, 9, 9)  # Monday

    # ── business_days_between ─────────────────────────────────────────

    def test_business_days_between_same_week(self, cal):
        monday = Date(2024, 3, 18)
        friday = Date(2024, 3, 22)
        assert cal.business_days_between(monday, friday) == 4

    def test_business_days_between_with_weekend(self, cal):
        # Friday → Monday → 1 biz day (only Monday)
        friday = Date(2024, 3, 15)
        monday = Date(2024, 3, 18)
        assert cal.business_days_between(friday, monday) == 1

    def test_business_days_between_full_week(self, cal):
        monday_1 = Date(2024, 3, 18)
        monday_2 = Date(2024, 3, 25)
        assert cal.business_days_between(monday_1, monday_2) == 5

    def test_business_days_between_reversed(self, cal):
        monday = Date(2024, 3, 18)
        friday = Date(2024, 3, 22)
        assert cal.business_days_between(friday, monday) == -4

    def test_business_days_between_same_date(self, cal):
        d = Date(2024, 3, 18)
        assert cal.business_days_between(d, d) == 0


# ═══════════════════════════════════════════════════════════════════════
# DayCounter tests
# ═══════════════════════════════════════════════════════════════════════

class TestActual365:
    """Tests for Actual/365 day count convention."""

    @pytest.fixture
    def dc(self):
        return Actual365()

    def test_day_count_basic(self, dc):
        d1 = Date(2024, 1, 1)
        d2 = Date(2024, 7, 1)
        # Jan: 31, Feb: 29 (leap), Mar: 31, Apr: 30, May: 31, Jun: 30 = 182
        assert dc.day_count(d1, d2) == 182

    def test_day_count_same_date(self, dc):
        d = Date(2024, 6, 15)
        assert dc.day_count(d, d) == 0

    def test_year_fraction_full_year(self, dc):
        d1 = Date(2024, 1, 1)
        d2 = Date(2025, 1, 1)
        yf = dc.year_fraction(d1, d2)
        assert pytest.approx(yf, abs=0.01) == 1.0  # ~366/365

    def test_year_fraction_half_year(self, dc):
        d1 = Date(2024, 1, 1)
        d2 = Date(2024, 7, 1)  # 182 days
        yf = dc.year_fraction(d1, d2)
        assert pytest.approx(yf, abs=0.01) == 182 / 365.0

    def test_year_fraction_negative(self, dc):
        d1 = Date(2024, 7, 1)
        d2 = Date(2024, 1, 1)
        yf = dc.year_fraction(d1, d2)
        assert yf < 0


class TestBus252:
    """Tests for Business/252 day count convention (Brazilian market)."""

    @pytest.fixture
    def cal(self):
        return WeekendOnlyCalendar()

    @pytest.fixture
    def dc(self, cal):
        return Bus252(cal)

    def test_day_count_one_week(self, dc):
        mon = Date(2024, 3, 18)
        fri = Date(2024, 3, 22)
        assert dc.day_count(mon, fri) == 4

    def test_day_count_two_weeks(self, dc):
        mon1 = Date(2024, 3, 18)
        mon2 = Date(2024, 4, 1)
        assert dc.day_count(mon1, mon2) == 10

    def test_year_fraction_one_week(self, dc):
        mon = Date(2024, 3, 18)
        fri = Date(2024, 3, 22)
        yf = dc.year_fraction(mon, fri)
        assert pytest.approx(yf, abs=1e-6) == 4 / 252.0

    def test_day_count_same_date(self, dc):
        d = Date(2024, 3, 18)
        assert dc.day_count(d, d) == 0

    def test_year_fraction_same_date(self, dc):
        d = Date(2024, 3, 18)
        assert dc.year_fraction(d, d) == 0.0
