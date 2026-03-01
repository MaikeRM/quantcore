"""
Tests for quantcore.core.math.calculus module.

Covers:
  - FiniteDifference.gradient_1d: central difference first derivative
  - FiniteDifference.hessian_1d: second derivative approximation
  - Known mathematical functions for verification
"""

import pytest
import numpy as np
from quantcore.core.math.calculus.differentiation import FiniteDifference


class TestGradient1D:
    """Tests for FiniteDifference.gradient_1d (first derivative)."""

    def test_linear_function(self):
        """f(x) = 3x + 2 → f'(x) = 3."""
        f = lambda x: 3 * x + 2
        result = FiniteDifference.gradient_1d(f, 5.0)
        assert pytest.approx(result, abs=1e-8) == 3.0

    def test_quadratic_function(self):
        """f(x) = x² → f'(x) = 2x."""
        f = lambda x: x ** 2
        result = FiniteDifference.gradient_1d(f, 3.0)
        assert pytest.approx(result, abs=1e-6) == 6.0

    def test_cubic_function(self):
        """f(x) = x³ → f'(x) = 3x²."""
        f = lambda x: x ** 3
        result = FiniteDifference.gradient_1d(f, 2.0)
        assert pytest.approx(result, abs=1e-4) == 12.0

    def test_sine_function(self):
        """f(x) = sin(x) → f'(x) = cos(x)."""
        result = FiniteDifference.gradient_1d(np.sin, np.pi / 4)
        expected = np.cos(np.pi / 4)
        assert pytest.approx(result, abs=1e-6) == expected

    def test_exponential_function(self):
        """f(x) = e^x → f'(x) = e^x."""
        result = FiniteDifference.gradient_1d(np.exp, 1.0)
        assert pytest.approx(result, abs=1e-6) == np.exp(1.0)

    def test_constant_function(self):
        """f(x) = 7 → f'(x) = 0."""
        f = lambda x: 7.0
        result = FiniteDifference.gradient_1d(f, 42.0)
        assert pytest.approx(result, abs=1e-10) == 0.0

    def test_at_origin(self):
        """f(x) = x² → f'(0) = 0."""
        f = lambda x: x ** 2
        result = FiniteDifference.gradient_1d(f, 0.0)
        assert pytest.approx(result, abs=1e-8) == 0.0

    def test_negative_x(self):
        """f(x) = x² → f'(-3) = -6."""
        f = lambda x: x ** 2
        result = FiniteDifference.gradient_1d(f, -3.0)
        assert pytest.approx(result, abs=1e-6) == -6.0

    def test_custom_step_size(self):
        """Custom h parameter should still yield correct results."""
        f = lambda x: x ** 2
        result = FiniteDifference.gradient_1d(f, 3.0, h=1e-3)
        assert pytest.approx(result, abs=1e-3) == 6.0


class TestHessian1D:
    """Tests for FiniteDifference.hessian_1d (second derivative)."""

    def test_quadratic_function(self):
        """f(x) = x² → f''(x) = 2."""
        f = lambda x: x ** 2
        result = FiniteDifference.hessian_1d(f, 3.0)
        assert pytest.approx(result, abs=1e-4) == 2.0

    def test_cubic_function(self):
        """f(x) = x³ → f''(x) = 6x."""
        f = lambda x: x ** 3
        result = FiniteDifference.hessian_1d(f, 2.0)
        assert pytest.approx(result, abs=1e-3) == 12.0

    def test_sine_function(self):
        """f(x) = sin(x) → f''(x) = -sin(x)."""
        result = FiniteDifference.hessian_1d(np.sin, np.pi / 4)
        expected = -np.sin(np.pi / 4)
        assert pytest.approx(result, abs=1e-4) == expected

    def test_linear_function(self):
        """f(x) = 3x + 2 → f''(x) = 0."""
        f = lambda x: 3 * x + 2
        result = FiniteDifference.hessian_1d(f, 5.0)
        assert pytest.approx(result, abs=1e-6) == 0.0

    def test_exponential_function(self):
        """f(x) = e^x → f''(x) = e^x."""
        result = FiniteDifference.hessian_1d(np.exp, 1.0)
        assert pytest.approx(result, abs=1e-3) == np.exp(1.0)

    def test_at_origin(self):
        """f(x) = x² → f''(0) = 2."""
        f = lambda x: x ** 2
        result = FiniteDifference.hessian_1d(f, 0.0)
        assert pytest.approx(result, abs=1e-4) == 2.0

    def test_custom_step_size(self):
        """Custom h parameter should still yield correct results."""
        f = lambda x: x ** 2
        result = FiniteDifference.hessian_1d(f, 3.0, h=1e-3)
        assert pytest.approx(result, abs=1e-2) == 2.0
