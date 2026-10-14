"""Standalone diagnostic of the working MLB Scoreboard Configurator Wi-Fi workflow.

Run: python3 -m universal_led.wifi_reference
This module never changes network profiles or disconnects Wi-Fi.
"""
import json
import subprocess

def command(args,timeout=20):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=timeout,check=False)
        return {'command':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {'command':args,'returncode':-1,'stdout':'','stderr':str(exc)}

def diagnose(interface='wlan0'):
    """Use the same two nmcli commands as mlb_scoreboard_configurator.network.scan."""
    rescan=command(['nmcli','device','wifi','rescan','ifname',interface],15)
    listing=command(['nmcli','-t','-f','SSID,SIGNAL,SECURITY,IN-USE',
                     'device','wifi','list','ifname',interface])
    return {'interface':interface,'rescan':rescan,'listing':listing,
            'note':'Read-only; no connection changes performed'}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interface',default='wlan0')
    args=parser.parse_args()
    print(json.dumps(diagnose(args.interface),indent=2))
