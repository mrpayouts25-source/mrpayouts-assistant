from urllib.parse import urlparse, parse_qs


def parse_ctrader_link(link):

    params = parse_qs(
        urlparse(link).query
    )

    return {

        "symbol": params.get("s", [""])[0].upper(),

        "direction": params.get("d", [""])[0].upper(),

        "sl": float(params.get("sl", [0])[0]),

        "tp": float(params.get("tp", [0])[0])

    }