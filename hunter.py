import random
import sys
import time
import threading
from datetime import datetime
from mnemonic import Mnemonic
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

# Inisialisasi colorama untuk warna output
init(autoreset=True)

# Aktifkan fitur mnemonic pada eth_account
Account.enable_unaudited_hdwallet_features()

RPC_ENDPOINTS = {
    "Ethereum": "https://eth.merkle.io",
    "Base": "https://base.drpc.org",
    "Optimism": "https://optimism.drpc.org",
    "Arbitrum": "https://arbitrum.drpc.org",
    "Unichain": "https://0xrpc.io/uni",
    "Soneium": "https://soneium.drpc.org",
    "Zora": "https://zora.drpc.org",
    "Blast": "https://blast.drpc.org",
    "Hyperliquid": "https://hyperliquid.drpc.org",
    "BSC": "https://bsc.therpc.io",
    "Polygon": "https://polygon-rpc.com",
    "Avalanche": "https://avalanche.drpc.org",
}

# Variabel global untuk statistik
stats = {
    "total_checked": 0,
    "wallets_with_balance": 0,
    "total_balance_found": 0,
    "start_time": None
}

def banner():
    """Menampilkan banner keren"""
    print(Fore.CYAN + Style.BRIGHT + """
╔═══════════════════════════════════════════════════════════════╗
║                   🔍 CRYPTO WALLET HUNTER 🔍                   ║
║                     Advanced Balance Checker                   ║
╚═══════════════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)

def ambil_12_kata_acak():
    """Generate 12 kata mnemonic acak"""
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    kata_acak = random.sample(wordlist, 12)
    return " ".join(kata_acak)

def mnemonic_to_address(mnemonic_phrase):
    """Konversi mnemonic ke address wallet"""
    try:
        acct = Account.from_mnemonic(mnemonic_phrase)
        return acct.address
    except Exception as e:
        return None

def format_time_elapsed():
    """Format waktu yang telah berlalu"""
    if stats["start_time"]:
        elapsed = time.time() - stats["start_time"]
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return "00:00:00"

def create_status_line(address, status, chain_info=""):
    """Membuat status line yang bergulir"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    elapsed = format_time_elapsed()
    
    # Truncate address untuk tampilan yang lebih kompak
    short_addr = f"{address[:6]}...{address[-4:]}" if address else "N/A"
    
    status_line = (
        f"⏰ {timestamp} | "
        f"🕒 {elapsed} | "
        f"📊 Checked: {stats['total_checked']:,} | "
        f"💰 Found: {stats['wallets_with_balance']} | "
        f"🏦 Total: {stats['total_balance_found']:.6f} ETH | "
        f"🎯 Current: {short_addr} | "
        f"📡 {status}"
    )
    
    if chain_info:
        status_line += f" | {chain_info}"
    
    return status_line

def print_scrolling_status(address, status, chain_info=""):
    """Print status dengan efek bergulir"""
    status_line = create_status_line(address, status, chain_info)
    
    # Bersihkan baris dan print status baru
    sys.stdout.write('\r' + ' ' * 150)  # Clear line
    sys.stdout.write('\r')
    
    # Warna berdasarkan status
    if "✅" in status:
        color = Fore.GREEN
    elif "❌" in status or "⚠️" in status:
        color = Fore.RED
    elif "🔍" in status:
        color = Fore.YELLOW
    else:
        color = Fore.CYAN
    
    sys.stdout.write(color + status_line)
    sys.stdout.flush()

def animate_checking_chains():
    """Animasi untuk pengecekan chains"""
    chains = list(RPC_ENDPOINTS.keys())
    for i, chain in enumerate(chains):
        progress = f"[{i+1}/{len(chains)}]"
        return f"🔍 Checking {chain} {progress}"

def cek_saldo_wallet(address):
    """Cek saldo wallet di semua chain"""
    saldo_total = 0
    saldo_per_chain = {}
    
    for i, (nama_chain, rpc_url) in enumerate(RPC_ENDPOINTS.items()):
        try:
            # Update status untuk chain yang sedang dicek
            progress = f"[{i+1}/{len(RPC_ENDPOINTS)}]"
            chain_status = f"🔍 Checking {nama_chain} {progress}"
            print_scrolling_status(address, chain_status)
            
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if not web3.is_connected():
                saldo_per_chain[nama_chain] = None
                continue
                
            saldo_wei = web3.eth.get_balance(address)
            saldo_eth = saldo_wei / 10**18
            saldo_per_chain[nama_chain] = saldo_eth
            saldo_total += saldo_eth
            
            # Jika ada balance, update status
            if saldo_eth > 0:
                balance_status = f"💰 FOUND {saldo_eth:.6f} ETH on {nama_chain}!"
                print_scrolling_status(address, balance_status)
                time.sleep(1)  # Pause sebentar untuk highlight
            
        except Exception as e:
            saldo_per_chain[nama_chain] = None
    
    return saldo_total, saldo_per_chain

def simpan_aset(mnemonic, address, saldo_per_chain, filename="crypto_assets.txt"):
    """Simpan aset yang ditemukan"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"🎯 WALLET FOUND! - {timestamp}\n")
        f.write(f"{'='*60}\n")
        f.write(f"Mnemonic: {mnemonic}\n")
        f.write(f"Address: {address}\n")
        f.write(f"Balances:\n")
        for chain, saldo in saldo_per_chain.items():
            if saldo and saldo > 0:
                f.write(f"  💰 {chain}: {saldo:.8f} ETH\n")
        f.write(f"{'='*60}\n")

def show_final_stats():
    """Tampilkan statistik akhir"""
    elapsed = format_time_elapsed()
    print(f"\n\n" + "="*70)
    print(Fore.MAGENTA + Style.BRIGHT + "📊 FINAL STATISTICS")
    print("="*70)
    print(f"⏰ Runtime: {elapsed}")
    print(f"📊 Total Wallets Checked: {stats['total_checked']:,}")
    print(f"💰 Wallets with Balance: {stats['wallets_with_balance']:,}")
    print(f"🏦 Total ETH Found: {stats['total_balance_found']:.8f}")
    if stats['total_checked'] > 0:
        success_rate = (stats['wallets_with_balance'] / stats['total_checked']) * 100
        print(f"📈 Success Rate: {success_rate:.8f}%")
    print("="*70)

def main():
    banner()
    print(Fore.YELLOW + "🚀 Starting Crypto Wallet Hunter...")
    print(Fore.CYAN + "💡 Press Ctrl+C to stop\n")
    
    stats["start_time"] = time.time()
    
    try:
        while True:
            # Generate mnemonic dan address
            mnemonic_12_kata = ambil_12_kata_acak()
            address = mnemonic_to_address(mnemonic_12_kata)
            
            if address is None:
                print_scrolling_status("", "⚠️ Invalid mnemonic generated")
                continue
            
            stats["total_checked"] += 1
            
            # Update status awal
            print_scrolling_status(address, "🎯 Generated new wallet")
            time.sleep(0.1)
            
            # Cek saldo
            total_saldo, saldo_per_chain = cek_saldo_wallet(address)
            
            if total_saldo > 0:
                stats["wallets_with_balance"] += 1
                stats["total_balance_found"] += total_saldo
                
                # Tampilkan hasil dengan highlight
                success_msg = f"🎉 JACKPOT! Found {total_saldo:.6f} ETH!"
                print_scrolling_status(address, success_msg)
                
                # Simpan hasil
                simpan_aset(mnemonic_12_kata, address, saldo_per_chain)
                
                # Tampilkan detail di baris baru
                print(f"\n{Fore.GREEN}{'='*70}")
                print(f"🎯 ADDRESS: {address}")
                print(f"🔑 MNEMONIC: {mnemonic_12_kata}")
                for chain, saldo in saldo_per_chain.items():
                    if saldo and saldo > 0:
                        print(f"💰 {chain}: {saldo:.8f} ETH")
                print(f"{'='*70}{Style.RESET_ALL}")
                
                time.sleep(2)  # Pause untuk apresiasi
            else:
                # Status kosong
                print_scrolling_status(address, "❌ No balance found")
            
            time.sleep(0.05)  # Small delay untuk smooth scrolling
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}🛑 Stopping Crypto Wallet Hunter...")
        show_final_stats()
        print(f"{Fore.MAGENTA}👋 Thanks for using Crypto Wallet Hunter!")
        
    except Exception as e:
        print(f"\n{Fore.RED}💥 Unexpected error: {e}")
        show_final_stats()

if __name__ == "__main__":
    main()
