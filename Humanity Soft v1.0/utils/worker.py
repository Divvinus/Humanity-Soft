import random

from better_proxy import Proxy
from undetected_playwright.async_api import Page, async_playwright
from web3 import AsyncWeb3

from data.config import BRIDGE_ABI, REWARDS_ABI
from utils.core import*


class Worker(ElementHandler):
    def __init__(self, client: Client):
        self.client: Client = client
        self.user_data_dir = f"./browser_data/{self.client.address}"

    async def claim_daily_reward(self):
        logger.info(
            f"{self.client.name} | Выполняем Daily Claim Reward (Check-in) | Адрес: {self.client.address}"
        )
        implementation_contract_address = AsyncWeb3.to_checksum_address(
            '0xa18f6FCB2Fd4884436d10610E69DB7BFa1bFe8C7'
        )
        contract = self.client.w3.eth.contract(
            address=implementation_contract_address, abi=REWARDS_ABI
        )
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.claimReward().build_transaction(tx_params)
            tx_result = await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            if "execution reverted: Rewards: no rewards available" in str(error):
                logger.warning(
                    f"{self.client.name} | Daily Claim Reward уже был выполнен | "
                    f"Адрес: {self.client.address}"
                )
            else:
                logger.error(
                    f"{self.client.name} | Произошла ошибка при Daily Claim Reward (Check-in) | "
                    f"Адрес: {self.client.address} | Error: {error}"
                )
            return

    async def faucet(self):
        logger.info(f"{self.client.name} | Запрашиваем токены из крана | Адрес: {self.client.address}")

        async with async_playwright() as p:
            args = [
                "--disable-blink-features=AutomationControlled"
            ]
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=True,
                proxy=Proxy.from_str(self.client.proxy_init).as_playwright_proxy,
                args=args,
                locale="en-US",
            )
            page: Page = await context.new_page()
            await page.goto('https://faucet.testnet.humanity.org/', timeout=60000)

            await page.locator(
                'input.input.is-rounded[placeholder="Enter your address or ENS name"]'
            ).fill(self.client.address)

            while True:
                await self.handle_element(page.locator('button:has-text("Request")'))
                if await page.locator(
                    'div.notification.is-success:has-text("Txhash")'
                ).is_visible(timeout=2000):
                    break

            logger.success(f"{self.client.name} | Успешно запросили тестовые токены | Адрес: {self.client.address}")

            await context.close()

    async def swap_sepolia_to_humanity(self):
        balance = await self.client.get_token_balance(check_native=True)
    
        if balance/10**18 < 0.001:
            logger.warning(f"{self.client.name} | Недостаточно {self.client.network.token} для свопа в сети Sepolia | Адрес: {self.client.address}")
            return
        value = int(balance * random.uniform(0.01, 0.1))
        logger.info(f"{self.client.name} | Свапаем {value/10**18} {self.client.network.token} из Sepolia в  Humanity | Адрес: {self.client.address}")

        implementation_contract_address = AsyncWeb3.to_checksum_address(
            '0x5F7CaE7D1eFC8cC05da97D988cFFC253ce3273eF'
        )
        contract = self.client.w3.eth.contract(
            address=implementation_contract_address, abi=BRIDGE_ABI
        )

        destination_network = 1
        destination_address = self.client.address
        amount = value
        token = AsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000')
        force_update_global_exit_root = True
        permit_data = b''

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.bridgeAsset(
                destination_network,
                destination_address,
                amount,
                token,
                force_update_global_exit_root,
                permit_data
            ).build_transaction(tx_params)
            tx_result = await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            logger.error(
                f"{self.client.name} | Произошла ошибка при Daily Claim Reward (Check-in) | "
                f"Адрес: {self.client.address} | Error: {error}"
            )
            return

    async def swap_humanity_to_sepolia(self):
        balance = await self.client.get_token_balance(check_native=True)
    
        if balance/10**18 < 0.001:
            logger.warning(f"{self.client.name} | Недостаточно {self.client.network.token} для свопа  | Адрес: {self.client.address}")
            return
        value = int(balance * random.uniform(0.01, 0.1))
        logger.info(f"{self.client.name} | Свапаем {value/10**18} {self.client.network.token} из Humanity в  Sepolia | Адрес: {self.client.address}")

        implementation_contract_address = AsyncWeb3.to_checksum_address(
            '0x5F7CaE7D1eFC8cC05da97D988cFFC253ce3273eF'
        )
        contract = self.client.w3.eth.contract(
            address=implementation_contract_address, abi=BRIDGE_ABI
        )
        value = int(balance * random.uniform(0.1, 0.3))

        destination_network = 0 
        destination_address = self.client.address
        amount = value
        token = AsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000')
        force_update_global_exit_root = True
        permit_data = b''

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.bridgeAsset(
                destination_network,
                destination_address,
                amount,
                token,
                force_update_global_exit_root,
                permit_data
            ).build_transaction(tx_params)
            tx_result = await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            logger.error(
                f"{self.client.name} | Произошла ошибка при Daily Claim Reward (Check-in) | "
                f"Адрес: {self.client.address} | Error: {error}"
            )
            return

    
