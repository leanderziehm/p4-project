import pytest
from scapy.all import sniff, IP
import subprocess
import time


def extract_mri_count(pkt):
    """
    Extract MRI count from IP options if present.
    Returns count or None.
    """
    if IP not in pkt:
        return None

    ip = pkt[IP]

    if not hasattr(ip, "options"):
        return None

    for opt in ip.options:
        # MRI option type is 31
        if hasattr(opt, "option") and opt.option == 31:
            if hasattr(opt, "count"):
                return opt.count

    return None


@pytest.fixture(scope="module")
def generate_traffic():
    """
    Starts traffic in Mininet.
    """

    # low-rate traffic
    h1 = subprocess.Popen([
        "bash", "-c",
        "./send.py 10.0.2.2 'P4 is cool' 5"
    ])

    # high-rate traffic
    h11 = subprocess.Popen([
        "bash", "-c",
        "iperf -c 10.0.2.22 -t 5 -u"
    ])

    time.sleep(6)

    yield

    h1.terminate()
    h11.terminate()


def test_mri_count_is_nonzero(generate_traffic):
    """
    Sniff packets at h2 and verify MRI count > 0.
    """

    results = []

    def handler(pkt):
        count = extract_mri_count(pkt)
        if count is not None:
            results.append(count)

    # sniff packets on h2 interface
    sniff(
        iface="h2-eth0",
        prn=handler,
        timeout=8
    )

    print("Captured MRI counts:", results)

    assert len(results) > 0, "No MRI packets detected"
    assert any(c > 0 for c in results), f"All MRI counts invalid: {results}"