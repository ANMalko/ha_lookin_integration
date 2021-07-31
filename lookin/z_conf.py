from zeroconf import ServiceBrowser, ServiceListener, Zeroconf


class MyListener(ServiceListener):

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print(f"Service {name} added, service info: {info}")


zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_lookin._tcp.local.", listener)

try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()

# TYPE = '_lookin._tcp.local.'
# NAME = 'LOOKin_98F33011'
#
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.DEBUG)
#     if len(sys.argv) > 1:
#         assert sys.argv[1:] == ['--debug']
#         logging.getLogger('zeroconf').setLevel(logging.DEBUG)
#
#     zeroconf = Zeroconf()
#
#     try:
#         print(zeroconf.get_service_info(TYPE, NAME + '.' + TYPE))
#     finally:
#         zeroconf.close()