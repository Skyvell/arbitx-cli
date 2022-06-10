from asyncio import wait_for
from multiprocessing.connection import wait
from typing import List

import settings

from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import CallTransactionBuilder
from iconsdk.signed_transaction import SignedTransaction


icon_service = IconService(HTTPProvider(settings.ENDPOINT))
wallet = KeyWallet.load(settings.KEYSTORE_PATH, settings.KEYSTORE_PASSWORD)

def contract_call(to: str, method: str, params: dict):
    call = CallBuilder(wallet.get_address(), to, method, params).build()
    result = icon_service.call(call)
    return result

def contract_tx(to: str, method: str, params: dict = None, wait_for_result: bool = False):
    transaction = CallTransactionBuilder(
        from_ = wallet.get_address(), 
        to = to,
        value = 0,
        step_limit = settings.STEP_LIMIT,
        nid = settings.NID, 
        method = method, 
        params = params
    )
    transaction = transaction.build()
    signed_transaction = SignedTransaction(transaction, wallet)

    if wait_for_result:
        return icon_service.send_transaction_and_wait(signed_transaction)
    else:
        return icon_service.send_transaction(signed_transaction)
  
    
def arbitrage(pairName: str, wait_for_result: bool = False):
    tx = CallTransactionBuilder(
        from_ = wallet.get_address(), 
        to = settings.ARBITRAGE_SCORE,
        value = 0,
        step_limit = settings.STEP_LIMIT,
        nid = settings.NID,
        nonce=100,
        method = "arbitrage",
        params = {'pairName': pairName}
    )
    tx = tx.build()
    signed_tx = SignedTransaction(tx, wallet)

    if wait_for_result:
        return icon_service.send_transaction_and_wait(signed_tx)
    else:
        return icon_service.send_transaction(signed_tx)
