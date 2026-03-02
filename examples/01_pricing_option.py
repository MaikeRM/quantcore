import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quantcore.instruments.derivatives.options.european import EuropeanOption
from quantcore.core.base.types.enums import OptionType
from quantcore.pricing.engines import PricingEngineFactory, EngineType

def main():
    print("Exemplo 1: Precificação de Opção Europeia usando Black-Scholes")
    print("-" * 60)

    # Criação de uma opção de compra (Call) europeia
    call_option = EuropeanOption(
        underlying_price=100.0,
        strike_price=100.0,
        time_to_maturity=1.0,  # 1 ano
        risk_free_rate=0.05,   # 5%
        volatility=0.2,        # 20%
        dividend_yield=0.0,
        option_type=OptionType.CALL
    )

    print(f"Detalhes da Opção:")
    print(f"Tipo: {call_option.option_type.name}")
    print(f"Preço do Ativo Objeto (S): {call_option.underlying_price}")
    print(f"Preço de Exercício (K): {call_option.strike_price}")
    print(f"Tempo até Maturidade (T): {call_option.time_to_maturity} anos")
    print(f"Taxa Livre de Risco (r): {call_option.risk_free_rate}")
    print(f"Volatilidade (σ): {call_option.volatility}")

    # Inicializa a fábrica de engines para obter a engine apropriada para a opção
    factory = PricingEngineFactory()
    
    # Obtém a engine analítica (neste caso, Black-Scholes) para a opção europeia
    bs_engine = factory.create_engine(call_option, EngineType.ANALYTIC)
    
    # Executa a precificação
    call_price = bs_engine.calculate(call_option)
    
    print("-" * 60)
    print(f"Preço Calculado da Call: {call_price:.4f}")

    # Criação de uma opção de venda (Put) correspondente (paridade Put-Call)
    put_option = EuropeanOption(
        underlying_price=100.0,
        strike_price=100.0,
        time_to_maturity=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        dividend_yield=0.0,
        option_type=OptionType.PUT
    )

    put_price = bs_engine.calculate(put_option)
    
    print(f"Preço Calculado da Put  : {put_price:.4f}")
    print("-" * 60)

if __name__ == "__main__":
    main()
