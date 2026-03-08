import logging
from scapy.all import rdpcap, TCP, ARP


logger = logging.getLogger(__name__)


def analyze_pcap(file_path: str) -> str:
    """
    Простейший анализ pcap-файла.
    Проверяем несколько базовых признаков сетевых атак.
    """

    try:
        packets = rdpcap(file_path)
    except Exception as err:
        logger.error("Cannot read pcap file %s: %s", file_path, err)
        return "❌ Ошибка чтения файла трафика"

    tcp_syn_count = 0
    arp_count = 0
    total_packets = 0

    # иногда scapy возвращает странные пакеты,
    # поэтому лучше аккуратно проверять каждый
    for pkt in packets:

        total_packets += 1

        try:
            if pkt.haslayer(TCP):

                flags = pkt[TCP].flags

                # SYN флаг = 2
                if flags == 2:
                    tcp_syn_count += 1

            elif pkt.haslayer(ARP):

                arp_count += 1

        except Exception as parse_err:
            logger.debug("packet parse error: %s", parse_err)
            continue

    report_lines = []
    recommendations = []

    # SYN Flood
    if tcp_syn_count > 100:
        report_lines.append("⚠️ Возможная SYN Flood (DoS) атака")
        recommendations.append(
            "🔐 Проверьте firewall и ограничьте количество входящих соединений"
        )

    # ARP spoofing
    if arp_count > 50:
        report_lines.append("⚠️ Возможная ARP Spoofing атака")
        recommendations.append(
            "🔐 Используйте ARP inspection или защищённую сеть"
        )

    # если ничего подозрительного
    if len(report_lines) == 0:
        report_lines.append("✅ Подозрительной активности не обнаружено")
        recommendations.append("ℹ️ Трафик выглядит нормальным")

    text = "📊 Результаты анализа трафика\n\n"

    for line in report_lines:
        text += line + "\n"

    text += "\n📌 Рекомендации\n"

    for rec in recommendations:
        text += rec + "\n"

    text += f"\n📦 Всего пакетов проанализировано: {total_packets}"

    return text