from scapy.all import sniff, IP
import time
import sys

# Store whether we saw MRI with count > 0
passed = False

def check_packet(pkt):
    global passed

    if IP in pkt:
        ip = pkt[IP]

        # MRI is carried in IP options
        if hasattr(ip, "options"):
            for opt in ip.options:
                # MRI option type is 31
                if opt.copy_flag == 0 and opt.option == 31:
                    try:
                        # opt.fields should contain MRI parsed fields
                        if hasattr(opt, "count"):
                            print(f"[DEBUG] MRI count = {opt.count}")
                            if opt.count != 0:
                                passed = True
                    except Exception as e:
                        print("Parse error:", e)

print("Sniffing for MRI packets... (10 seconds)")

sniff(
    iface="h2-eth0",
    prn=check_packet,
    timeout=10
)

if passed:
    print("TEST PASS: MRI count != 0 detected")
    sys.exit(0)
else:
    print("TEST FAIL: No MRI count > 0 detected")
    sys.exit(1)