def binance_keys(sub_account=None):
    if sub_account == 1:
        # AGPL Main
        key = ""
        secret = ""
    elif sub_account == 2:
        # Trading account 2
        key = ''
        secret = ''
    elif sub_account == 3:
        #AGPLsub2
        key = ''
        secret = ''
    elif sub_account == 4:
        # AGPLsub3
        key = ''
        secret = ''
    elif sub_account == 5:
        # AGPLsub4
        key = ''
        secret = ''
    else:
        #AGPL Main
        key = ""
        secret = ""
    return key, secret

def kucoin_keys(sub_account=None):
    if sub_account == 1:
        #AGPL Main
        key = ""
        secret = ""
        passphrase = ""
    elif sub_account == 2:
        #AGPL sub1
        key = ""
        secret = ""
        passphrase = ""
    elif sub_account == 3:
        #AGPL HB rewards
        key = ""
        secret = ""
        passphrase = ""
    elif sub_account == 4:
        # AGPL sub3
        key = ""
        secret = ""
        passphrase = ""
    else:
        # AGPL Main
        key = ""
        secret = ""
        passphrase = ""


    return key, secret, passphrase

def gate_keys():
    key = ""
    secret = ""
    return key, secret