from scapy.all import rdpcap, TCP, ARP
import pandas as pd

def analyze_pcap(file_path: str) -> str:
    packets = rdpcap(file_path)

    data = []
    for pkt in packets:
        if pkt.haslayer(TCP):
            data.append({
                "type": "TCP",
                "flags": pkt[TCP].flags
            })
        elif pkt.haslayer(ARP):
            data.append({
                "type": "ARP"
            })

    df = pd.DataFrame(data)

    report = []
    recommendations = []

    if "TCP" in df["type"].values:
        syn_packets = df[df["flags"] == 2]
        if len(syn_packets) > 100:
            report.append("⚠️ Возможная SYN Flood (DoS) атака")
            recommendations.append("🔐 Ограничить входящие соединения, использовать firewall")

    arp_count = len(df[df["type"] == "ARP"])
    if arp_count > 50:
        report.append("⚠️ Возможная ARP Spoofing атака")
        recommendations.append("🔐 Использовать ARP inspection, защищённый Wi-Fi")

    if not report:
        report.append("✅ Признаков атак не обнаружено")
        recommendations.append("ℹ️ Сеть работает в нормальном режиме")

    response = (
        "📊 Результаты анализа трафика:\n\n"
        + "\n".join(report)
        + "\n\n📌 Рекомендации:\n"
        + "\n".join(recommendations)
    )

    return response