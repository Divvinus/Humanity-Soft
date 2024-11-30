class Network:
    def __init__(
            self,
            name: str,
            rpc: list,
            chain_id: int,
            eip1559_support: bool,
            token: str,
            explorer: str,
            decimals: int = 18
    ):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.eip1559_support = eip1559_support
        self.token = token
        self.explorer = explorer
        self.decimals = decimals

    def __repr__(self):
        return f'{self.name}'


Humanity_Protocol = Network(
    name='Humanity Protocol Testnet',
    rpc=[
        'https://rpc.testnet.humanity.org/'
    ],
    chain_id=1942999413,
    eip1559_support=False,
    token='tHP',
    explorer='https://explorer.testnet.humanity.org/',
)

Sepolia = Network(
    name='Sepolia Testnet',
    rpc=[
        'wss://sepolia.drpc.org',
        'wss://ethereum-sepolia-rpc.publicnode.com',
        'wss://sepolia.gateway.tenderly.co',
        'https://eth-sepolia.public.blastapi.io',
        'https://ethereum-sepolia.blockpi.network/v1/rpc/public',
        'https://sepolia.gateway.tenderly.co',
        'https://endpoints.omniatech.io/v1/eth/sepolia/public',
        'https://ethereum-sepolia-rpc.publicnode.com',
        'https://gateway.tenderly.co/public/sepolia',
        'https://1rpc.io/sepolia'
    ],
    chain_id=11155111 ,
    eip1559_support=False,
    token='ETH',
    explorer='https://sepolia.etherscan.io/',
)
