import random
import sys
import time
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
    "arbitrum": "https://arbitrum.drpc.org",
    "Unichain": "https://0xrpc.io/uni",
    "Soneium": "https://soneium.drpc.org",
    "Zora": "https://zora.drpc.org",
    "Blast": "https://blast.drpc.org",
    "Hayperliquid": "https://hyperliquid.drpc.org",
    "Bsc": "https://bsc.therpc.io",
    "Polygon": "https://polygon-rpc.com",
    "Avalanche": "https://avalanche.drpc.org",
}

def ambil_12_kata_acak():
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist
    kata_acak = random.sample(wordlist, 12)
    return " ".join(kata_acak)

def print_inplace(text):
    # Bersihkan baris lalu print text baru (in-place)
    sys.stdout.write('\r' + ' ' * 100)
    sys.stdout.write('\r' + text)
    sys.stdout.flush()

def mnemonic_to_address(mnemonic_phrase):
    try:
        acct = Account.from_mnemonic(mnemonic_phrase)
        return acct.address
    except Exception as e:
        return None

def cek_saldo_wallet(address):
    saldo_total = 0
    saldo_per_chain = {}
    for nama_chain, rpc_url in RPC_ENDPOINTS.items():
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if not web3.is_connected():
                print(Fore.RED + f"  [{nama_chain}] Gagal koneksi ke RPC.")
                saldo_per_chain[nama_chain] = None
                continue
            saldo_wei = web3.eth.get_balance(address)
            saldo_eth = saldo_wei / 10**18  # konversi manual dari Wei ke Ether
            saldo_per_chain[nama_chain] = saldo_eth
            saldo_total += saldo_eth
        except Exception as e:
            print(Fore.RED + f"  [{nama_chain}] Error: {e}")
            saldo_per_chain[nama_chain] = None
    return saldo_total, saldo_per_chain

def simpan_aset(mnemonic, address, saldo_per_chain, filename="aset.txt"):
    with open(filename, "a") as f:
        f.write(f"Mnemonic: {mnemonic}\n")
        f.write(f"Address: {address}\n")
        f.write("Saldo per chain:\n")
        for chain, saldo in saldo_per_chain.items():
            f.write(f"  {chain}: {saldo} ETH\n")
        f.write("="*40 + "\n")

def animasi_loading(duration=3, prefix="Loading"):
    for i in range(duration * 2):
        dots = "." * ((i % 3) + 1)
        sys.stdout.write(f"\r{prefix}{dots}   ")
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write("\r" + " " * (len(prefix) + 3) + "\r")

def main():
    print(Fore.MAGENTA + "Mulai acak 12 kata dan cek saldo... (Tekan Ctrl+C untuk berhenti)")

    while True:
        try:
            mnemonic_12_kata = ambil_12_kata_acak()
            address = mnemonic_to_address(mnemonic_12_kata)
            if address is None:
                # Cetak pesan singkat di in-place sudah dilakukan, lanjut percobaan baru
                continue
            print(Fore.YELLOW + f"Address: {address}")

            animasi_loading(prefix="Mengecek saldo wallet")

            total_saldo, saldo_per_chain = cek_saldo_wallet(address)
            if total_saldo > 0:
                print(Fore.GREEN + f"Saldo ditemukan! Total saldo: {total_saldo} ETH")
                simpan_aset(mnemonic_12_kata, address, saldo_per_chain)
            else:
                print(Fore.RED + "Saldo nol, tidak disimpan.")

            time.sleep(1)

        except KeyboardInterrupt:
            print(Fore.MAGENTA + "\nDihentikan oleh pengguna. Sampai jumpa!")
            break
        except Exception as e:
            print(Fore.RED + f"\nError tak terduga: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()


