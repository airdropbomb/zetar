import os
import time
import random
from datetime import datetime
import pytz
from colorama import Fore, Style, init
import requests
from typing import Optional, Dict, List
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import warnings

# Initialize Colorama
init(autoreset=True)

# Ignore warnings
warnings.filterwarnings('ignore')
import sys
if not sys.warnoptions:
    os.environ["PYTHONWARNINGS"] = "ignore"

os.system('clear' if os.name == 'posix' else 'cls')

# --- ASCII Logo ---
def display_logo():
    print(
        f"""
{Fore.GREEN + Style.BRIGHT}        █████╗ ██████╗ ██████╗      ███╗   ██╗ ██████╗ ██████╗ ███████╗
{Fore.GREEN + Style.BRIGHT}       ██╔══██╗██╔══██╗██╔══██╗     ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
{Fore.GREEN + Style.BRIGHT}       ███████║██║  ██║██████╔╝     ██╔██╗ ██║██║   ██║██║  ██║█████╗  
{Fore.GREEN + Style.BRIGHT}       ██╔══██║██║  ██║██╔══██╗     ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
{Fore.GREEN + Style.BRIGHT}       ██║  ██║██████╔╝██████╔╝     ██║ ╚████║╚██████╔╝██████╔╝███████╗
{Fore.GREEN + Style.BRIGHT}       ╚═╝  ╚═╝╚═════╝ ╚═════╝      ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
{Fore.YELLOW + Style.BRIGHT}                Modified by ADB NODE
        """
    )

RPC_URL = "https://data-seed-prebsc-1-s1.binance.org:8545"
TOKEN_ADDRESS = "0x2186fc0e8404eCF9F63cCBf1C75d5fAF6B843786"
MARKET_CONTRACT_ADDRESS = "0x852a5C778034e0776181955536528347Aa901d24"
FAUCET_CONTRACT_ADDRESS = "0xc9e16209Ed6B2A4f41b751788FE74F5c0B7F8E1c"

class ZetariumBot:
    def __init__(self):
        self.base_url = "https://airdrop-data.zetarium.world"
        self.api_url = "https://api.zetarium.world"
        self.prediction_url = "https://prediction-market-api.zetarium.world"
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.trade_count_per_account = 1
        
        self.token_abi = [
            {"constant":False,"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},
            {"constant":True,"inputs":[{"name":"account","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},
            {"constant":True,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"}
        ]
        
        self.market_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "marketId", "type": "uint256"},
                    {"name": "outcome", "type": "uint8"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "makePrediction",
                "outputs": [],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

        self.faucet_abi = [
            {
                "constant": False,
                "inputs": [],
                "name": "claim",
                "outputs": [],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    def get_wib_time(self):
        wib = pytz.timezone('Asia/Jakarta')
        return datetime.now(wib).strftime('%H:%M:%S')
    
    def print_banner(self):
        # စာသားဟောင်းကို ဖြုတ်ပြီး Logo အသစ်တစ်ခုတည်းပဲ ပြပါမယ်
        display_logo()
    
    def log(self, message, level="INFO"):
        time_str = self.get_wib_time()
        
        if level == "INFO": color = Fore.CYAN; symbol = "[INFO]"
        elif level == "SUCCESS": color = Fore.GREEN; symbol = "[SUCCESS]"
        elif level == "ERROR": color = Fore.RED; symbol = "[ERROR]"
        elif level == "WARNING": color = Fore.YELLOW; symbol = "[WARNING]"
        elif level == "CYCLE": color = Fore.MAGENTA; symbol = "[CYCLE]"
        elif level == "BET": color = Fore.MAGENTA; symbol = "[BET]"
        else: color = Fore.WHITE; symbol = "[LOG]"
        
        print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")
    
    def random_delay(self, min_sec=2, max_sec=5):
        time.sleep(random.randint(min_sec, max_sec))
    
    def show_proxy_menu(self):
        print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. Run with proxy")
        print(f"2. Run without proxy{Style.RESET_ALL}")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        while True:
            try:
                choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
                if choice in ['1', '2']: return choice == '1'
                else: print(f"{Fore.RED}Invalid choice! Please enter 1 or 2.{Style.RESET_ALL}")
            except KeyboardInterrupt: exit(0)

    def show_action_menu(self):
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. Run Daily Checkin")
        print(f"2. Run Faucet + Trades")
        print(f"3. Run All{Style.RESET_ALL}")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        while True:
            try:
                choice = input(f"{Fore.GREEN}Enter your choice (1/2/3): {Style.RESET_ALL}").strip()
                if choice in ['1', '2', '3']:
                    if choice in ['2', '3']:
                        try:
                            count = int(input(f"{Fore.GREEN}How many times do you want to trade : {Style.RESET_ALL}"))
                            self.trade_count_per_account = count
                        except ValueError: self.trade_count_per_account = 1
                    return choice
                else: print(f"{Fore.RED}Invalid choice! Please enter 1, 2 or 3.{Style.RESET_ALL}")
            except KeyboardInterrupt: exit(0)
    
    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            hours = i // 3600
            minutes = (i % 3600) // 60
            secs = i % 60
            print(f"\r{Fore.CYAN}[COUNTDOWN]{Style.RESET_ALL} Next cycle in: {hours:02d}:{minutes:02d}:{secs:02d} ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)

    def check_balance(self, private_key):
        try:
            account = self.w3.eth.account.from_key(private_key)
            token_contract = self.w3.eth.contract(address=Web3.to_checksum_address(TOKEN_ADDRESS), abi=self.token_abi)
            balance = token_contract.functions.balanceOf(account.address).call()
            return float(self.w3.from_wei(balance, 'ether'))
        except Exception as e:
            self.log(f"Balance check failed: {e}", "ERROR")
            return 0

    def check_and_approve(self, private_key, amount_wei):
        try:
            account = self.w3.eth.account.from_key(private_key)
            token_contract = self.w3.eth.contract(address=Web3.to_checksum_address(TOKEN_ADDRESS), abi=self.token_abi)
            spender = Web3.to_checksum_address(MARKET_CONTRACT_ADDRESS)
            allowance = token_contract.functions.allowance(account.address, spender).call()
            
            if allowance < amount_wei:
                self.log("Approving USDC...", "INFO")
                max_amount = 2**256 - 1
                tx = token_contract.functions.approve(spender, max_amount).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 100000,
                    'gasPrice': self.w3.eth.gas_price
                })
                signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                self.w3.eth.wait_for_transaction_receipt(tx_hash)
                self.log(f"USDC Approved! Hash: {tx_hash.hex()[:10]}...", "SUCCESS")
                time.sleep(3)
            return True
        except Exception as e:
            self.log(f"Approve Failed: {e}", "ERROR")
            return False

    def claim_faucet(self, private_key):
        try:
            account = self.w3.eth.account.from_key(private_key)
            contract = self.w3.eth.contract(address=Web3.to_checksum_address(FAUCET_CONTRACT_ADDRESS), abi=self.faucet_abi)
            contract_func = contract.functions.claim()
            try:
                gas_estimate = contract_func.estimate_gas({'from': account.address})
                gas_limit = int(gas_estimate * 1.2)
            except:
                self.log("Faucet Already Claimed", "WARNING")
                return False

            tx = contract_func.build_transaction({
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price
            })
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.log(f"Faucet Tx Sent: {tx_hash.hex()[:10]}...", "INFO")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            if receipt.status == 1:
                self.log("Faucet Claimed Successfully!", "SUCCESS")
                return True
            return False
        except Exception as e:
            self.log(f"Faucet Error: {str(e)}", "ERROR")
            return False

    def buy_prediction(self, private_key, market_id, outcome, token_amount):
        try:
            account = self.w3.eth.account.from_key(private_key)
            amount_wei = self.w3.to_wei(token_amount, 'ether')
            if not self.check_and_approve(private_key, amount_wei): return False

            market_contract = self.w3.eth.contract(address=Web3.to_checksum_address(MARKET_CONTRACT_ADDRESS), abi=self.market_abi)
            outcome_str = "YES" if outcome == 1 else "NO"
            self.log(f"Placing Bet... ID: {market_id} | Pick: {outcome_str} | Amt: {token_amount} USDC", "BET")
            
            contract_func = market_contract.functions.makePrediction(int(market_id), int(outcome), amount_wei)
            gas_limit = int(contract_func.estimate_gas({'from': account.address}) * 1.2)
            
            tx = contract_func.build_transaction({
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address, 'pending'),
                'gas': gas_limit, 
                'gasPrice': self.w3.eth.gas_price
            })
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                self.log("Bet Placed Successfully!", "SUCCESS")
                return True
            return False
        except Exception as e:
            self.log(f"Buy Error: {str(e)}", "ERROR")
            return False

    def get_prediction_markets(self, proxy=None):
        headers = {"accept": "*/*", "user-agent": "Mozilla/5.0", "origin": "https://prediction.zetarium.world"}
        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            response = requests.get(f"{self.prediction_url}/markets?limit=200", headers=headers, proxies=proxies, timeout=30)
            return response.json() if response.status_code == 200 else None
        except: return None

    def get_user_info(self, token, proxy=None):
        headers = {"authorization": f"Bearer {token}", "user-agent": "Mozilla/5.0"}
        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            res = requests.get(f"{self.base_url}/auth/me", headers=headers, proxies=proxies, timeout=30)
            return res.json() if res.status_code == 200 else None
        except: return None

    def sign_message(self, private_key, message):
        try:
            account = Account.from_key(private_key)
            message_hash = encode_defunct(text=message)
            signed = account.sign_message(message_hash)
            return "0x" + signed.signature.hex()
        except: return None

    def get_wallet_address(self, private_key):
        try: return Account.from_key(private_key).address
        except: return None

    def claim_daily_gm(self, token, private_key, wallet, proxy=None):
        headers = {"authorization": f"Bearer {token}", "content-type": "application/json", "user-agent": "Mozilla/5.0"}
        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            msg = f"GM! Claim daily points - {wallet.lower()}"
            sig = self.sign_message(private_key, msg)
            if not sig: return {"success": False}
            res = requests.post(f"{self.api_url}/api/profile/{wallet}/gm", json={"message": msg, "signature": sig}, headers=headers, proxies=proxies)
            if res.status_code == 200: return res.json()
            elif res.status_code == 400: return {"success": False, "already_claimed": True}
            return {"success": False}
        except: return {"success": False}

    def load_accounts(self, filename="accounts.txt"):
        try:
            accounts = []
            with open(filename, 'r') as f:
                content = f.read().split('\n\n')
            for block in content:
                lines = block.strip().split('\n')
                acc = {}
                for line in lines:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        acc[k.strip().lower()] = v.strip()
                if 'token' in acc: accounts.append(acc)
            return accounts
        except: return []

    def load_proxies(self, filename="proxy.txt"):
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except: return []

    def process_account(self, idx, total, account, proxy, mode):
        token = account.get('token')
        pk = account.get('private_key')
        self.log(f"Account #{idx}/{total} | Proxy: {proxy[:20] if proxy else 'No Proxy'}...", "INFO")

        user = self.get_user_info(token, proxy)
        if not user:
            self.log("Login Failed / Token Expired", "ERROR")
            return
        
        username = user['user'].get('username', 'N/A')
        points = user['user'].get('points', 0)
        self.log(f"Login successful! {username} | Points: {points}", "SUCCESS")
        
        if pk:
            wallet_address = self.get_wallet_address(pk)
            current_balance = self.check_balance(pk)
            self.log(f"Wallet: {wallet_address[:6]}... | Balance: {current_balance:.2f} USDC", "INFO")
            
            res = self.claim_daily_gm(token, pk, wallet_address, proxy)
            if res.get('success'): self.log("GM Claimed Successfully!", "SUCCESS")
            elif res.get('already_claimed'): self.log("GM Already Claimed Today", "SUCCESS")
            
            if mode in ['2', '3']:
                self.claim_faucet(pk)
                markets = self.get_prediction_markets(proxy)
                if markets and "markets" in markets:
                    active_markets = [m for m in markets['markets'] if m.get('status') == 0]
                    random.shuffle(active_markets)
                    
                    successful = 0
                    for t in range(self.trade_count_per_account):
                        if not active_markets: break
                        target = active_markets.pop(0)
                        outcome = 1 if int(target.get('yesPool', 0)) >= int(target.get('noPool', 0)) else 2
                        if self.buy_prediction(pk, target['id'], outcome, random.randint(50, 100)):
                            successful += 1
                        time.sleep(random.randint(5, 10))
                    self.log(f"Trades Complete: {successful}/{self.trade_count_per_account}", "INFO")

    def run(self):
        self.print_banner()
        use_proxy = self.show_proxy_menu()
        mode = self.show_action_menu()
        accounts = self.load_accounts()
        proxies = self.load_proxies() if use_proxy else []

        cycle = 1
        while True:
            self.log(f"Cycle #{cycle} Started", "CYCLE")
            for i, acc in enumerate(accounts):
                proxy = proxies[i % len(proxies)] if proxies else None
                self.process_account(i+1, len(accounts), acc, proxy, mode)
                print("-" * 60)
            
            self.log(f"Cycle #{cycle} Complete", "CYCLE")
            cycle += 1
            self.countdown(86400)

if __name__ == "__main__":
    ZetariumBot().run()
