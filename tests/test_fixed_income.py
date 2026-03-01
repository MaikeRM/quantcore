"""
Tests for quantcore.instruments.fixed_income module.

Covers:
  - FixedRateBond: construction, properties, metadata, abstract contract
"""

import pytest
from quantcore.instruments.fixed_income.bonds.fixed_rate import FixedRateBond, BaseBond
from quantcore.core.base.abc.instrument import FinancialInstrument
from quantcore.core.time.date import Date


class TestFixedRateBond:
    """Tests for quantcore.instruments.fixed_income.bonds.fixed_rate.FixedRateBond."""

    @pytest.fixture
    def bond(self):
        return FixedRateBond(
            face_value=1000.0,
            coupon_rate=0.06,
            maturity_date=Date(2030, 6, 15),
            frequency=2,
        )

    # ── Construction ──────────────────────────────────────────────────

    def test_construction(self, bond):
        assert bond.face_value == 1000.0
        assert bond.coupon_rate == 0.06
        assert bond.maturity_date == Date(2030, 6, 15)
        assert bond.frequency == 2

    # ── Abstract contract compliance ──────────────────────────────────

    def test_is_financial_instrument(self, bond):
        assert isinstance(bond, FinancialInstrument)

    def test_is_base_bond(self, bond):
        assert isinstance(bond, BaseBond)

    # ── instrument_type ───────────────────────────────────────────────

    def test_instrument_type(self, bond):
        assert bond.instrument_type == "Fixed Rate Bond"

    # ── currency ──────────────────────────────────────────────────────

    def test_currency_default(self, bond):
        assert bond.currency == "USD"

    # ── get_metadata ──────────────────────────────────────────────────

    def test_metadata_keys(self, bond):
        meta = bond.get_metadata()
        expected_keys = {"Face Value", "Coupon Rate", "Maturity Date", "Payment Frequency"}
        assert set(meta.keys()) == expected_keys

    def test_metadata_values(self, bond):
        meta = bond.get_metadata()
        assert meta["Face Value"] == 1000.0
        assert meta["Coupon Rate"] == 0.06
        assert meta["Payment Frequency"] == 2

    def test_metadata_maturity_is_string(self, bond):
        meta = bond.get_metadata()
        assert isinstance(meta["Maturity Date"], str)
        assert meta["Maturity Date"] == "2030-06-15"

    # ── Various parameter scenarios ───────────────────────────────────

    def test_zero_coupon_bond(self):
        """A zero-coupon bond has coupon_rate=0."""
        zcb = FixedRateBond(
            face_value=1000.0,
            coupon_rate=0.0,
            maturity_date=Date(2025, 12, 31),
            frequency=0,
        )
        assert zcb.coupon_rate == 0.0
        assert zcb.instrument_type == "Fixed Rate Bond"

    def test_high_frequency_bond(self):
        """Monthly coupon payment."""
        bond = FixedRateBond(
            face_value=500.0,
            coupon_rate=0.12,
            maturity_date=Date(2026, 1, 1),
            frequency=12,
        )
        meta = bond.get_metadata()
        assert meta["Payment Frequency"] == 12
