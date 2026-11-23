from wifisec.core.scanner import (
    _detect_encryption,
    _parse_netsh_output,
    analyze_signal,
    filter_networks,
)


def test_parse_netsh_output_extracts_network_details():
    output = """
    SSID 1 : Test Network
        Authentication : WPA2-Personal
        Encryption : CCMP
        BSSID 1 : 00:11:22:33:44:55
            Signal : 75%
            Channel : 6
    """

    networks = _parse_netsh_output(output)

    assert networks == [{
        "ESSID": "Test Network",
        "BSSID": "00:11:22:33:44:55",
        "Channel": "6",
        "Authentication": "WPA2-Personal",
        "Encryption": "WPA2",
        "Signal": "75%",
        "Quality(%)": 75,
    }]


def test_encryption_detection_prioritizes_stronger_protocols():
    assert _detect_encryption("WPA3-SAE WPA2") == "WPA3"
    assert _detect_encryption("WPA2-Personal") == "WPA2"
    assert _detect_encryption("ESS encryption key:on") == "WEP"
    assert _detect_encryption("") == "OPEN"


def test_analyze_signal_clamps_percent_and_converts_dbm():
    networks = [
        {"Signal": "120%"},
        {"Signal": "-60 dBm"},
        {"Signal": "not-a-signal"},
    ]

    result = analyze_signal(networks)

    assert [network["Quality(%)"] for network in result] == [100, 80, 0]


def test_filter_networks_applies_security_ssid_and_quality():
    networks = [
        {"ESSID": "Home", "Encryption": "WPA2", "Quality(%)": 80},
        {"ESSID": "Guest", "Encryption": "OPEN", "Quality(%)": 90},
        {"ESSID": "Home-5G", "Encryption": "WPA2", "Quality(%)": 20},
    ]

    result = filter_networks(
        networks,
        security="WPA2",
        ssid="home",
        min_quality=50,
    )

    assert result == [networks[0]]
