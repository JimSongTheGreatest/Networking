from socket import *
import os
import sys
import struct
import time
import select
import binascii
ICMP_ECHO_REQUEST = 8


def check_sum(str_ing):
    str_ing = bytearray(str_ing)
    c_sum = 0
    countTo = (len(str_ing) // 2) * 2
    for count in range(0, countTo, 2):
        thisVal = str_ing[count+1] * 256 + str_ing[count]
        c_sum = c_sum + thisVal
        c_sum = c_sum & 0xffffffff
    if countTo < len(str_ing):
        c_sum = c_sum + str_ing[-1]
        c_sum = c_sum & 0xffffffff
    c_sum = (c_sum >> 16) + (c_sum & 0xffff)
    c_sum = c_sum + (c_sum >> 16)
    answer = ~c_sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receive_One_ping_test(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        icmpType, code, mycheck_sum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader)
        if type != 8 and packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def send_One_ping_test(mySocket, destAddr, ID):
    mycheck_sum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, mycheck_sum, ID, 1)
    data = struct.pack("d", time.time())
    mycheck_sum = check_sum(header + data)
    if sys.platform == 'darwin':
        mycheck_sum = htons(mycheck_sum) & 0xffff
    else:
        mycheck_sum = htons(mycheck_sum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, mycheck_sum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))


def do_One_ping_test(destAddr, timeout):
    icmp = getprotobyname("icmp")
    mySocket = socket(AF_INET, SOCK_DGRAM, icmp)
    myID = os.getpid() & 0xFFFF  # Return the current process i
    send_One_ping_test(mySocket, destAddr, myID)
    delay = receive_One_ping_test(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping_test(host, timeout=1):
    dest = gethostbyname(host)
    print("ping_testing " + dest + " using Python:")
    print("")
    while 1:
        delay = do_One_ping_test(dest, timeout)
        print(delay)
        time.sleep(1)  # one second
    return delay


if __name__ == '__main__':
    ping_test("127.0.0.1")
