package main

import (
	"fmt"
	"net"
)

func checkIpWhetherInNet(sourceIp string, targetNet string) bool {
	_, targetNt, _ := net.ParseCIDR(targetNet)
	ip := net.ParseIP(sourceIp)
	fmt.Println(targetNet)
	if targetNt.Contains(ip) {
		return true
	} else {
		return false
	}
}

func main() {

	targetNet := "192.168.254.100/24"
	checkIp := "192.168.252.167"
	checkIp2 := "192.168.254.117"
	fmt.Println(checkIpWhetherInNet(checkIp, targetNet))
	fmt.Println(checkIpWhetherInNet(checkIp2, targetNet))

}
