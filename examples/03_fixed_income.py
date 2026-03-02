import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quantcore.instruments.fixed_income.bonds.fixed_rate import FixedRateBond
from quantcore.core.time.date import Date
from quantcore.core.time.calendar import Calendar
from quantcore.core.time.daycount import Actual365

def main():
    print("Exemplo 3: Renda Fixa e Títulos de Dívida (Bonds)")
    print("-" * 60)

    # Criação de um título prefixado (Fixed Rate Bond)
    # Título que paga 8% a.a. semestralmente (frequência 2)
    bond = FixedRateBond(
        face_value=1000.0,
        coupon_rate=0.08,
        maturity_date=Date(2035, 12, 31),
        frequency=2,
    )

    print(f"Tipo de Instrumento: {bond.instrument_type}")
    print(f"Moeda: {bond.currency}")
    
    # Exibir metadados e características
    meta = bond.get_metadata()
    print("\nCaracterísticas do Título:")
    for key, value in meta.items():
        print(f"- {key}: {value}")

    print("\nCriação de Zero-Coupon Bond:")
    # Um título "Zero Coupon" tem taxa de cupom zero
    zero_coupon = FixedRateBond(
        face_value=1000.0,
        coupon_rate=0.0,
        maturity_date=Date(2028, 6, 15),
        frequency=0,
    )
    
    meta_zero = zero_coupon.get_metadata()
    for key, value in meta_zero.items():
        print(f"- {key}: {value}")

    print("-" * 60)

if __name__ == "__main__":
    main()
