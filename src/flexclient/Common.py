def ParseRadio(radioString):
    """parse radio info from received packet"""
    desirable_txt = {
        "serial": None,
        "public_ip": None,
        "public_upnp_tls_port": None,
        "public_upnp_udp_port": None,
        "upnp_supported": None,
        "public_tls_port": None,
        "public_udp_port": None,
        "discovery_protocol_version": None,
        "model": None,
        "version": None,
        "nickname": None,
        "callsign": None,
        "ip": None,
        "port": None,
        "status": None,
        "inuse_ip": None,
        "inuse_host": None,
        "max_licensed_version": None,
        "radio_license_id": None,
        "requires_additional_license": None,
        "fpc_mac": None,
        "wan_connected": None,
        "licensed_clients": None,
        "available_clients": None,
        "max_panadapters": None,
        "available_panadapters": None,
        "max_slices": None,
        "available_slices": None,
        "gui_client_ips": None,
        "gui_client_hosts": None,
        "gui_client_programs": None,
        "gui_client_stations": None,
        #"gui_client_handles" (=\x00\x00)
    }
    for ra in radioString.split(" "):
        for txt in desirable_txt.keys():
            if txt in ra:
                desirable_txt[txt] = ra.split("=")[1]

    return desirable_txt

