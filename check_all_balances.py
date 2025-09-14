import requests

# Combine all your derived addresses from BIP44, BIP49, BIP84, and BIP86
addresses = [
    # === BIP44 Legacy (1...) ===
    "16Kq4g6ErLv87mjBNM1oVGuYkfQrNMdqXV",
    "1HEcL6c435z31DXgMjcb923u8woyPE3prr",
    "18XJuimHQbhrigkYdzzMAWN8mG2xdgW1QM",
    "18xt9cweSZDvN32NbQxMZJZ23yVZ48Dpjw",
    "1Mgw37fcQZqpmeatrQ6Q9hSTuT4frEcVPh",
    "1KE2bKKgRJvsWfnghpjPsydtfW2X15Gyk4",
    "14rYcCXBp8JuifVw86Vm1hxxGSFdsg154K",
    "1LSysyDoDDFi9d9ViqKm3vWT9qYZjVoseD",
    "13DuZGYEzWZCBg4qoPV2Lt8oAdTHtYd7Dj",
    "1PaQStFW1jruFjTgQDtQtb7efZkcyfRWJH",
    "1BMZHXVqTJa7pm8ptQbUQu73gZE4wEiio4",
    "1Hif5XMF7zxKWHyivFSxP1nHjvYs44UHdC",
    "1P9B5e8nrPXtUoCtkNgRmKFTbxmgSayAte",
    "1L9nyftuXJX7AAnDJQdAPygih442WqRxao",
    "1L53bAswkCzmjXDnsHsgket41FXvDLmcAn",
    "1BiXuafpoPapwy2AXa2FP9U4ngWTYxJyoG",
    "12TeA4Ahetb3fptMQN9oitNTUq5TjbDErT",
    "1QUQu6uz7sAogHGwMSeQ82MfSMTLYxjAM",
    "1GTUHWvKAdJnQkpu6FpTgPj6smvVRDAv4p",
    "1j7VmP1EENgyHHX3KRAbPKcCTLPVwiKpA",

    # === BIP49 (3...) ===
    "3BgQqirdqy6CvCHUNtXSwFcLxnE4x7PidN",
    "3KtZeNsvFbeXDZMionqv4JuVKbk3afd8a7",
    "3Njk4Mb2d66FnSLPEwFUNiyLP3VdZZ4n22",
    "3HgEJubN6Q3T7QDbvzrdxmMRuYgrBXq7Av",
    "3HcYYGBeKVmaJE1jDdPJqMyx8Q8yUrZ6m2",
    "3DXXDgck56jbgX3Ef9zFdWvruvKtyKPJm2",
    "31iyfYp1G5Ckrf1vkGPd4p1ZXhTUwNArRT",
    "3PdQhWvSmWvZpDBY7fQEaN7N8E1ELQnmZz",
    "33pygXKMpGP5HLXmFbbebVosJj24R3oPLU",
    "3MGNv71GsNAfAu59qJXSJ9Tmrbj9jNcvEb",
    "3KBd32HqCUbmYMQG9NUWGAsEgpniSvbgEt",
    "3FeBrEBdD26q1YzecpMwowyTCX8hirCMo4",
    "39A7TzLWGFRqFEspaZyWLSCWv5CvqJFQZa",
    "3FQL4ZM8AhzNWR4NMuZSapgyJYCSYdKP55",
    "3CfHnPqbeaGkaPiwoxN8jSCAnrrYwSrKHi",
    "3KckwdkWTqdRw3SH69aUGYe2BU3TVgwCrN",
    "3QwopGVdXZzygERDEMmmhNx3tjxjTPc7NN",
    "3E6n4cck9L9mEHLvhxC2oypUxhZJuPDC6X",
    "3MaGJsSG1nZnJAhJE6qZkE2Xhcr9ByCTbC",
    "3HgZwXjGaX6yg6BMJYZcWHYhxJfMbEXatp",

    # === BIP84 (bc1q...) Native SegWit ===
    "bc1q8f6lxefke2p0h0a3k73faxqxxwkqm8gzg2chly",
    "bc1qg9pfwhslt30ejtuawq4qjk5jjujx27280p7fxa",
    "bc1qexjngclf2mt4kr2rs47ll9sww64naqh2d8wwvg",
    "bc1q6eg3sm5skk8vedy20ph7jhdz40jcnvgyph5nu0",
    "bc1qty3xldra9tdrzflfs7rn9x92c6k9nc9k3mt47w",
    "bc1qr6aarl0wjmpan0v3cszyt0hjc3rh9y8wf4nrcd",
    "bc1q7vmgvhf62xq2ccyql78lj35fea0rcl6k750uxm",
    "bc1qu84s3gjdpajwgv0a0ayg5ru2pnzwaes6k52rs8",
    "bc1qnmv8xeum2d2a65tgc8x5dt29qvml0hjksj0hej",
    "bc1qwl7m06rpk3pw2qv0jxcncptv873wxct796hdvf",
    "bc1qrv4j4tdu6lj559kzz3jw9khj9gqvnspfv0ypqj",
    "bc1q92yux8k4t83gk0jm7972m8rddtfwd7dh28djm5",
    "bc1qt2w25ggjjmte5qshx9zdyhxz539znwqrueu6cs",
    "bc1q83gsm2m6l2avs3ms3p66pydku4e7dymlnxp4n3",
    "bc1qg9rhrvqxr5h7whfzfjuqqryhnvslz3ksa5lu8h",
    "bc1qu7pr4cu9jefm3k6g0aqxlyw2ahhm3yrnytf8a8",
    "bc1qgnyrpegum0a668sgsxh0caw9zfadpd8wmp2dzl",
    "bc1ql4tsdcq07twelpeq44ftvr6wf2ka4l9q9fw2xa",
    "bc1qcnys26d0ra2wzzwk02fhny602a5ak376ehqwjn",
    "bc1qtc57yq3g5vh86ruzh8sufjlgypeg73qqjke47s",

    # === BIP86 (bc1p...) Taproot ===
    "bc1pgsmae23zg64y945zel27stqux5jx5zkdtzcgvzrm0klkmc8lxx5qt0sehq",
    "bc1pnkpwadn7238g9zxhjf4ap72rukj869uu6emucy04ges20j6pwgvqm9w8z9",
    "bc1png50v2hk0sw7nerr8fcl7x83jx4anz2dtsv7j5c6tt4lv9e309zqxuqwj0",
    "bc1phcclvemqkcuenkyrxvgkc23gl7wjq87z7uruxfwyckxwz66n7jsqsp9f6t",
    "bc1pmpmzpsquuxdj0zz6hl3uq5jrjzz5rh4nrsn0gslpejtkwgdtnt9q2pg77m",
    "bc1pwxxtcdwnucdlalt4vjahwehu7d630an99dadevj3hxwu2akym64stqe6j3",
    "bc1pqnpc5u7kvlcszgz3th47usvm8xflfsx2ddxnx3yd7f2cxe4nzejskc8hl9",
    "bc1p3rz9252d3xkj8hz9qju9cderuvv2pmkakmce6pmrrulv4hjl9cpseg00m5",
    "bc1pr0xg5tml0md0mhhyxvezjnv63nhuu03pzh858yv0v7axfd7hzdsqjqzlz6",
    "bc1pewsdunzpnykaswk33jpvn2s9gm0ax476zpyjg944xjxhmcuwtk9s2se7ef",
    "bc1pywymz8ewua9tzq26kclwxy75j7huuezumn492wtjvj09ktevaspquu3xkm",
    "bc1pre8czel007trw4zltfju9wqzp053nhgmjhs5z0df5g7np9qz2hcqadz4t9",
    "bc1ptvwayd3y6geltm03mu77v0u8x8m679j7hzvelzj85j5nkmsx3qkqeh4nt4",
    "bc1ptw2a777dqpty8vka607ny3ym8ck2yghefpuk565p3z8all72g8zqy3xvwa",
    "bc1pr20gzrmvu7cy6f90f4jv0lw7rg9693djmgm3td5yltmvf82qrzssw9qnv0",
    "bc1ptmwhw0yym9z7335w7auqu8mc28mf95ml2qstu2v4shphq8ka8tgqu22rxg",
    "bc1p0rmdm2smj470aqudwqkn7cg3erj2g8kn0j4mwznhsnjxkcaqcpuq0h9us5",
    "bc1pra9l9hg95x7h3dfedaydjz4mlcu6xpmaznm6cggsq6ut5txk7vaq04c6pk",
    "bc1p064y99vnl4xfxgxxn2ghgw7tw4rfqxvatuh4qy89urxyelggpnlqrugtcx",
    "bc1p3djznplgvvzpqge50qsl5r66cl89vksajy2qc8jseh9rvykgsveqpd3j4v",
]

def get_balance(addr):
    url = f"https://blockstream.info/api/address/{addr}"
    r = requests.get(url).json()
    confirmed = r['chain_stats']['funded_txo_sum'] - r['chain_stats']['spent_txo_sum']
    mempool = r['mempool_stats']['funded_txo_sum'] - r['mempool_stats']['spent_txo_sum']
    return confirmed + mempool  # sats

def main():
    for a in addresses:
        bal = get_balance(a)
        print(f"{a}: {bal} sats ({bal/1e8:.8f} BTC)")

if __name__ == "__main__":
    main()
