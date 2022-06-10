from multiprocessing.connection import wait
import typer
import time
import rpc
import settings
import constants
import pandas as pd
from concurrent import futures

app = typer.Typer()


@app.command()
def start_arbitrage_bot():
    pairs_with_arbitrage = rpc.contract_call(settings.ARBITRAGE_SCORE, "checkForArbitrage", {})

    if not pairs_with_arbitrage:
        return

    # Execute arbitrages and save txids.
    tx_ids = []
    for pair in pairs_with_arbitrage:
        txid = rpc.arbitrage(pair, wait_for_result=False)
        tx_ids.append(txid)
    
    # Sleep and get transaction results.
    time.sleep(4)
    for tx_id in tx_ids:
        result = rpc.icon_service.get_transaction_result(tx_id)
        arbitrage_report = get_eventlog(result, settings.ARBITRAGE_SCORE, 'ArbitrageReport(Address,int,int)')
    print(result)
    print(arbitrage_report)


    #while True:
    #    pairs_with_arbitrage = rpc.contract_call(settings.ARBITRAGE_SCORE, "checkForArbitrage")
    #    if pairs_with_arbitrage:
    #        for pair in pairs_with_arbitrage:
    #            txid = rpc.contract_tx(settings.ARBITRAGE_SCORE, "arbitrage", {'pairName': pair})
    #            print(txid)
    #    time.sleep(1.8)

@app.command()
def check_for_arbitrage():
    result = rpc.contract_call(settings.ARBITRAGE_SCORE, "checkForArbitrage", {})
    print(result)

@app.command()
def get_detailed_arbitrage_evaluation():
    evaluations = rpc.contract_call(settings.ARBITRAGE_SCORE, "getDetailedArbitrageEvaluation", {})
    
    # Create dataframe and rename columns.
    df = pd.DataFrame(evaluations)
    rename_colums = {
        "d": "pair",
        "e": "convexusPrice",
        "f": "balancedPrice",
        "g": "basisPointDifference",
        "h": "arbitrage",
        "i": "buyExchange",
        "j": "sellExchange"
    }
    df = df.rename(columns=rename_colums)

    # Make values more readable.
    df['convexusPrice'] = df['convexusPrice'].apply(lambda x: int(x, 16) / constants.EXA)
    df['balancedPrice'] = df['balancedPrice'].apply(lambda x: int(x, 16) / constants.EXA)
    df['basisPointDifference'] = df['basisPointDifference'].apply(lambda x: int(x, 16))
    df['arbitrage'] = df['arbitrage'].apply(lambda x: bool(int(x, 16)))
    print(df)

@app.command()
def get_arbitrage_pairs():
    pairs = rpc.contract_call(settings.ARBITRAGE_SCORE, "getPairs", {})
    df = pd.DataFrame(pairs, columns=["name", "tokenA", "tokenB", "convexusFee", "arbitrageThreshold", "tokensPerIteration"])
    df['arbitrageThreshold'] = df['arbitrageThreshold'].apply(lambda x: int(x, 16))
    df['convexusFee'] = df['convexusFee'].apply(lambda x: int(x, 16))
    df['tokensPerIteration'] = df['tokensPerIteration'].apply(lambda x: int(x, 16) / constants.EXA)
    print(df)

@app.command()
def contract_balances():
    # Retrieve contract balances.
    balances = rpc.contract_call(settings.TRADEEXECUTOR_SCORE, "getContractTokenBalances", {})

    # Make table and print out.
    df = pd.DataFrame(balances, columns=["address", "name", "balance"])
    df['balance'] = df['balance'].apply(lambda x: int(x, 16) / constants.EXA)
    print(df)

##def execute_arbitrage(pairs: list):
##    workers = min(len(pairs, constants.MAX_WORKERS))
##    with futures.ThreadPoolExecutor(workers) as executor:
##        result = executor.map(rpc.arbitrage, pairs)


def get_eventlog(tx_result: dict, score_address: str, name: str, indexed: bool = True):
    eventlogs = tx_result['eventLogs']

    for eventlog in eventlogs:
        if eventlog['scoreAddress'] == score_address and eventlog['indexed'][0] == name:
            target_eventlog = eventlog['indexed']
            break

    return target_eventlog

def get_arbitrage_report(tx_result: str):
    get_eventlog(tx_result)

    




    arbitrage_report_eventlog = eventlogs


if __name__ == "__main__":
    app()