import asyncio
import random
import sys

from typing import List, Dict, Optional

from questionary import select, Choice
from utils.core import logger, get_accounts_data, Client
from generall_settings import *
from utils.worker import Worker
from utils.core.network import Humanity_Protocol, Sepolia
from data.config import TITLE


class Runner:
    @staticmethod
    async def smart_sleep(up, to, msg: str = None):
        duration = random.randint(up, to)
        if msg is None:
            logger.info(f"💤 Следующий аккаунт запуститься через {duration:.2f} секунд")
        else:
            logger.info(f"💤 {msg} {duration:.2f} секунд")
        await asyncio.sleep(duration)

    @staticmethod
    async def get_proxy_for_account(account_data: Dict) -> Optional[str]:
        try:
            return account_data['proxies']
        except Exception as error:
            logger.info(f"Аккаунт {account_data['account_name']} запускается без прокси: {error}")
            return None

    @classmethod
    def get_selected_accounts(cls) -> List[Dict]:
        accounts = get_accounts_data()

        if ACCOUNTS_TO_WORK == 0:
            return accounts

        if isinstance(ACCOUNTS_TO_WORK, int):
            return [accounts[ACCOUNTS_TO_WORK - 1]]

        if isinstance(ACCOUNTS_TO_WORK, (tuple, list)):
            if len(ACCOUNTS_TO_WORK) == 2:
                start, end = ACCOUNTS_TO_WORK
                return accounts[start-1:end]
            
            return [accounts[i - 1] for i in ACCOUNTS_TO_WORK]

        return []

    async def execute_action(self, account_data: Dict, action: int) -> None:
        account_name = account_data['account_name']
        proxy = await self.get_proxy_for_account(account_data)

        network = Humanity_Protocol

        if action == 3:
            network = Sepolia
        else:
            network = Humanity_Protocol 

        client = Client(
            name=account_name,
            private_key=account_data['private_key'],
            proxy=proxy,
            network=network,
        )

        logger.info(
            f"{account_name} | "
            f"Задание: {action} | Использует прокси: {bool(proxy)}"
        )

        try:
            worker = Worker(client=client)
            action_map = {
                1: worker.claim_daily_reward,
                2: worker.faucet,
                3: worker.swap_sepolia_to_humanity,
                4: worker.swap_humanity_to_sepolia,
            }

            task_func = action_map.get(action)
            if task_func:
                await task_func()
            else:
                logger.warning(f"{account_name} получил неизвестное действие: {action}")

        except Exception as e:
            logger.error(f"Ошибка при выполнении задания {action} для аккаунта {account_name}: {e}")

    async def run_account_modules(
        self, 
        account_data: Dict, 
        proxy: Optional[str], 
        parallel_mode: bool = STREAM, 
        actions_to_perform: Optional[List[int]] = None
    ) -> None:
        
        logger.info(f"Запуск аккаунта: {account_data['account_name']} (параллельный режим: {parallel_mode})")

        actions = actions_to_perform if isinstance(actions_to_perform, list) else [actions_to_perform]

        if SHUFFLE_TASKS:
            random.shuffle(actions)

        for action in actions:
            await self.execute_action(account_data, action)
            if len(actions) > 1:
                await self.smart_sleep(
                    SLEEP_TIME_TASKS[0], SLEEP_TIME_TASKS[1],
                    msg=f'Следующие задание для {account_data["account_name"]} будет выполнено через '
                )
                
    async def run_parallel(self, actions_to_perform: Optional[List[int]] = None) -> None:
        selected_accounts = self.get_selected_accounts()

        if SHUFFLE_ACCOUNTS:
            random.shuffle(selected_accounts)

        tasks = []

        for idx, account_data in enumerate(selected_accounts):
            proxy = await self.get_proxy_for_account(account_data)

            async def account_task():
                await self.run_account_modules(account_data, proxy, actions_to_perform=actions_to_perform)

            if idx > 0:
                if SLEEP_MODE:
                    await self.smart_sleep(SLEEP_TIME_ACCOUNTS[0], SLEEP_TIME_ACCOUNTS[1])

            task = asyncio.create_task(account_task())
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def run_sequential(self, actions_to_perform: Optional[List[int]] = None) -> None:
        selected_accounts = self.get_selected_accounts()

        if SHUFFLE_ACCOUNTS:
            random.shuffle(selected_accounts)

        for account_data in selected_accounts:
            proxy = await self.get_proxy_for_account(account_data)
            await self.run_account_modules(account_data, proxy, actions_to_perform=actions_to_perform)
            if SLEEP_MODE:
                await self.smart_sleep(SLEEP_TIME_ACCOUNTS[0], SLEEP_TIME_ACCOUNTS[1]) 
            await asyncio.sleep(0)            

    async def run(self, actions_to_perform: Optional[List[int]] = None) -> None:
        if STREAM:
            await self.run_parallel(actions_to_perform=actions_to_perform)
        else:
            await self.run_sequential(actions_to_perform=actions_to_perform)


def main():
    print(TITLE)
    print('\033[32m💬 Обновления и поддержка кода ➡️  https://t.me/divinus_xyz  🍀 Подписывайся 🍀 \033[0m')
    print()
    try:
        while True:
            answer = select(
                'Что вы хотите сделать?',
                choices=[
                    Choice("🚀 Выполнить все задания", 'run_all'),
                    Choice("📝 Выбрать задания для выполнения", 'select_actions'),
                    Choice('❌ Выход', 'exit')
                ],
                qmark='🛠️',
                pointer='👉'
            ).ask()

            runner = Runner()
            if answer == 'run_all':
                print()
                actions_to_perform = [1, 2, 3, 4]
                if SHUFFLE_TASKS:
                    random.shuffle(actions_to_perform)
                asyncio.run(runner.run(actions_to_perform=actions_to_perform))
                print()
            elif answer == 'select_actions':
                actions = select(
                    "Выберите задания для выполнения:",
                    choices=[
                        Choice("1️⃣ Daily reward", 1),
                        Choice("2️⃣ Faucet", 2),
                        Choice("3️⃣ Swap Sepolia to Humanity", 3),
                        Choice("4️⃣ Swap Humanity to Sepolia", 4),
                    ],
                    qmark="🤖",
                    pointer="👉",

                ).ask()
                asyncio.run(runner.run(actions_to_perform=actions))
            elif answer == 'exit':
                sys.exit()
            else:
                print("Выбрано неизвестное действие.")
    except KeyboardInterrupt:
        print("\nВыход из программы по сигналу <Ctrl+C>")
        sys.exit()

if __name__ == "__main__":
    asyncio.run(main())