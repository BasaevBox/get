import config
from db import get_wallet_form_bot

post = {
    "callback": {
        "url": "http://example.com/callback",
        "data": {
            "invoice_id": "1234",
            "secret": "7j0ap91o99cxj8k9"
        }
    }
}
ltc = get_wallet_form_bot('wallet_ltc')
btc = get_wallet_form_bot('wallet_btc')
bch = get_wallet_form_bot('wallet_bch')
url = 'https://apirone.com/api/v2/wallets/{}/addresses'.format(ltc[0])

btc_url = 'https://apirone.com/api/v2/wallets/{}/addresses'.format(btc[0])

btc_cash_url = 'https://apirone.com/api/v2/wallets/{}/addresses'.format(bch[0])