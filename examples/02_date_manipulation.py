import sys
import os
import datetime as dt

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quantcore.core.time.date import Date
from quantcore.core.time.calendar import Calendar
from quantcore.core.time.daycount import Actual365, Bus252

# Definimos um calendário simples para o exemplo
class BrazilSimpleCalendar(Calendar):
    """Calendário com fins de semana + feriados nacionais básicos."""
    
    HOLIDAYS = {
        dt.date(2024, 1, 1),   # Ano Novo
        dt.date(2024, 4, 21),  # Tiradentes
        dt.date(2024, 5, 1),   # Dia do Trabalhador
        dt.date(2024, 9, 7),   # Independência
        dt.date(2024, 10, 12), # Nossa Sra. Aparecida
        dt.date(2024, 11, 2),  # Finados
        dt.date(2024, 11, 15), # Proclamação da República
        dt.date(2024, 12, 25), # Natal
    }

    def is_business_day(self, date: Date) -> bool:
        return not self.is_holiday_or_weekend(date)

    def is_holiday(self, date: Date) -> bool:
        return date.to_datetime() in self.HOLIDAYS


def main():
    print("Exemplo 2: Manipulação de Datas e Contagem de Dias")
    print("-" * 60)

    # 1. Criação de Datas
    d1 = Date(2024, 5, 1)  # 1 de Maio de 2024
    d2 = Date(2024, 5, 2)  # 2 de Maio de 2024
    
    print(f"Data 1: {d1}")
    print(f"Data 2: {d2}")
    
    # 2. Aritmética de Datas
    d3 = d1 + 30
    print(f"30 dias após {d1}: {d3}")
    
    dias_entre = d3 - d1
    print(f"Dias absolutos entre {d3} e {d1}: {dias_entre}")

    print("\n--- Calendário e Dias Úteis ---")
    cal = BrazilSimpleCalendar()

    # Verificar se é dia útil
    print(f"{d1} (Feriado de 1 de Maio) é dia útil? {cal.is_business_day(d1)}")
    print(f"{d2} é dia útil? {cal.is_business_day(d2)}")
    
    # Adicionar dias úteis
    d_futura = cal.add_business_days(d1, 5)
    print(f"5 dias úteis após {d1}: {d_futura}")

    # Contagem de dias úteis entre duas datas
    d_inicio = Date(2024, 1, 1)
    d_fim = Date(2024, 12, 31)
    
    dias_uteis = cal.business_days_between(d_inicio, d_fim)
    print(f"Dias úteis absolutos entre {d_inicio} e {d_fim}: {dias_uteis}")

    print("\n--- Convenções de Contagem de Dias ---")

    # Convenção Actual/365
    act365 = Actual365()
    frac_ano_act365 = act365.year_fraction(d_inicio, d_fim)
    print(f"Fração de ano contagem Actual/365: {frac_ano_act365:.4f}")

    # Convenção Business/252
    bus252 = Bus252(cal)
    frac_ano_bus252 = bus252.year_fraction(d_inicio, d_fim)
    print(f"Fração de ano contagem Business/252: {frac_ano_bus252:.4f}")

    print("-" * 60)

if __name__ == "__main__":
    main()
