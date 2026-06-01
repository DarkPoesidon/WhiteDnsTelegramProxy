package main

import (
	"strings"
	"testing"
)

func TestMergeCfproxyDomainsAcceptsWhitespaceSeparatedList(t *testing.T) {
	var parsed []string
	for _, field := range strings.Fields("virkgj.com vmmzovy.com\nmkuosckvso.com") {
		parsed = append(parsed, field)
	}

	domains := mergeCfproxyDomains(parsed)
	if len(domains) != 3 {
		t.Fatalf("expected 3 domains, got %d: %v", len(domains), domains)
	}
}

func TestChooseFreshCfproxyDomainExcludesPreviousActive(t *testing.T) {
	cfproxyMu.Lock()
	previousDomains := cfproxyDomains
	previousUserDomain := cfproxyUserDomain
	previousActive := activeCfDomain
	cfproxyDomains = defaultCfproxyDomains()
	cfproxyUserDomain = ""
	activeCfDomain = cfproxyDomains[0]
	excluded := activeCfDomain
	chosen := chooseFreshCfproxyDomainLocked(excluded)
	cfproxyDomains = previousDomains
	cfproxyUserDomain = previousUserDomain
	activeCfDomain = previousActive
	cfproxyMu.Unlock()

	if chosen == "" {
		t.Fatal("expected a fresh domain")
	}
	if chosen == excluded {
		t.Fatalf("expected rotation away from %s", excluded)
	}
}

func TestFailureCooldownSuppressesImmediateRetry(t *testing.T) {
	clearCfproxyFailureCooldowns()
	domain := defaultCfproxyDomains()[0]
	markCfproxyFailureCooldown(domain)
	if remaining := cfproxyFailureCooldownRemaining(domain); remaining <= 0 {
		t.Fatal("expected active failure cooldown")
	}
	clearCfproxyFailureCooldown(domain)
	if remaining := cfproxyFailureCooldownRemaining(domain); remaining != 0 {
		t.Fatalf("expected cleared failure cooldown, got %s", remaining)
	}
}
