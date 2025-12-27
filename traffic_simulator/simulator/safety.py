"""
Safety Guard Module - Prevents abuse and ensures internal-only usage
"""
import ipaddress
import os
import socket
from typing import List, Optional, Tuple
from urllib.parse import urlparse


class SafetyGuard:
    """
    Safety guard untuk mencegah abuse dan memastikan hanya digunakan
    untuk internal testing (localhost, staging, internal network)
    """
    
    # Internal/private IP ranges yang diizinkan
    ALLOWED_IP_RANGES = [
        ipaddress.ip_network('127.0.0.0/8'),      # localhost
        ipaddress.ip_network('10.0.0.0/8'),       # private class A
        ipaddress.ip_network('172.16.0.0/12'),    # private class B
        ipaddress.ip_network('192.168.0.0/16'),   # private class C
        ipaddress.ip_network('169.254.0.0/16'),   # link-local
        ipaddress.ip_network('::1/128'),          # IPv6 localhost
        ipaddress.ip_network('fc00::/7'),         # IPv6 private
        ipaddress.ip_network('fe80::/10'),        # IPv6 link-local
    ]
    
    # Domain allowlist (internal dan staging)
    ALLOWED_DOMAINS = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        'staging.domainmu.com',
        'beraffiliate.com',
        'adilsempoamandiri.com',
    ]
    
    # Maximum RPS hard limit (safety limit)
    MAX_RPS_LIMIT = 1000  # requests per second
    
    # Maximum concurrent connections
    MAX_CONCURRENT_CONNECTIONS = 500
    
    # Allowed environments
    ALLOWED_ENVIRONMENTS = ['development', 'staging', 'test', 'local']
    
    def __init__(self, max_rps: int = MAX_RPS_LIMIT, 
                 max_concurrent: int = MAX_CONCURRENT_CONNECTIONS,
                 allowed_domains: Optional[List[str]] = None):
        """
        Initialize safety guard
        
        Args:
            max_rps: Maximum RPS limit (default: 1000)
            max_concurrent: Maximum concurrent connections (default: 500)
            allowed_domains: Additional allowed domains
        """
        self.max_rps = min(max_rps, self.MAX_RPS_LIMIT)
        self.max_concurrent = min(max_concurrent, self.MAX_CONCURRENT_CONNECTIONS)
        
        if allowed_domains:
            self.allowed_domains = self.ALLOWED_DOMAINS + allowed_domains
        else:
            self.allowed_domains = self.ALLOWED_DOMAINS.copy()
    
    def check_environment(self) -> Tuple[bool, str]:
        """
        Check jika environment sesuai (dev/staging)
        
        Returns:
            (is_allowed, error_message)
        """
        env = os.getenv('ENVIRONMENT', '').lower()
        node_env = os.getenv('NODE_ENV', '').lower()
        app_env = os.getenv('APP_ENV', '').lower()
        
        current_env = env or node_env or app_env or 'development'
        
        if current_env not in self.ALLOWED_ENVIRONMENTS and current_env != '':
            return False, f"Environment '{current_env}' not allowed. Allowed: {self.ALLOWED_ENVIRONMENTS}"
        
        return True, ""
    
    def resolve_hostname(self, hostname: str) -> List[str]:
        """
        Resolve hostname ke IP addresses
        
        Args:
            hostname: Hostname to resolve
            
        Returns:
            List of IP addresses
        """
        try:
            # Try IPv4 first
            ipv4_addrs = socket.gethostbyname_ex(hostname)[2]
            return ipv4_addrs
        except socket.gaierror:
            try:
                # Try IPv6
                ipv6_addrs = socket.getaddrinfo(hostname, None, socket.AF_INET6)
                return [addr[4][0] for addr in ipv6_addrs]
            except:
                return []
    
    def is_private_ip(self, ip_str: str) -> bool:
        """
        Check jika IP adalah private/internal
        
        Args:
            ip_str: IP address string
            
        Returns:
            True jika private/internal
        """
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # Check jika IP dalam allowed ranges
            for network in self.ALLOWED_IP_RANGES:
                if ip in network:
                    return True
            
            return False
        except ValueError:
            return False
    
    def is_allowed_domain(self, hostname: str) -> bool:
        """
        Check jika domain dalam allowlist
        
        Args:
            hostname: Hostname to check
            
        Returns:
            True jika domain diizinkan
        """
        # Direct match
        if hostname in self.allowed_domains:
            return True
        
        # Subdomain match (staging.domainmu.com matches domainmu.com)
        for allowed in self.allowed_domains:
            if hostname.endswith('.' + allowed) or hostname == allowed:
                return True
        
        return False
    
    def validate_target(self, url: str) -> Tuple[bool, str]:
        """
        Validate target URL - hanya izinkan internal/staging
        
        Args:
            url: Target URL
            
        Returns:
            (is_valid, error_message)
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            
            if not hostname:
                return False, "Invalid URL: no hostname"
            
            # Check jika hostname dalam allowlist
            if self.is_allowed_domain(hostname):
                return True, ""
            
            # Resolve hostname ke IP
            ip_addrs = self.resolve_hostname(hostname)
            
            if not ip_addrs:
                return False, f"Could not resolve hostname: {hostname}"
            
            # Check setiap resolved IP
            for ip in ip_addrs:
                if self.is_private_ip(ip):
                    return True, ""
            
            # Jika semua IP adalah public IP, block
            return False, f"Target '{hostname}' resolves to public IP(s): {', '.join(ip_addrs)}. Only internal/staging targets allowed."
        
        except Exception as e:
            return False, f"Error validating target: {str(e)}"
    
    def validate_rps(self, target_rps: float) -> Tuple[bool, str]:
        """
        Validate target RPS tidak melebihi limit
        
        Args:
            target_rps: Target requests per second
            
        Returns:
            (is_valid, error_message)
        """
        if target_rps > self.max_rps:
            return False, f"Target RPS {target_rps:.0f} exceeds maximum limit {self.max_rps} req/s"
        return True, ""
    
    def validate_concurrency(self, target_concurrent: int) -> Tuple[bool, str]:
        """
        Validate target concurrency tidak melebihi limit
        
        Args:
            target_concurrent: Target concurrent connections
            
        Returns:
            (is_valid, error_message)
        """
        if target_concurrent > self.max_concurrent:
            return False, f"Target concurrency {target_concurrent} exceeds maximum limit {self.max_concurrent}"
        return True, ""
    
    def validate_all(self, url: str, target_rps: Optional[float] = None,
                     target_concurrent: Optional[int] = None) -> Tuple[bool, str]:
        """
        Validate semua safety checks
        
        Args:
            url: Target URL
            target_rps: Target RPS (optional)
            target_concurrent: Target concurrency (optional)
            
        Returns:
            (is_valid, error_message)
        """
        # Check environment
        env_ok, env_msg = self.check_environment()
        if not env_ok:
            return False, env_msg
        
        # Check target URL
        url_ok, url_msg = self.validate_target(url)
        if not url_ok:
            return False, url_msg
        
        # Check RPS limit
        if target_rps is not None:
            rps_ok, rps_msg = self.validate_rps(target_rps)
            if not rps_ok:
                return False, rps_msg
        
        # Check concurrency limit
        if target_concurrent is not None:
            concurrent_ok, concurrent_msg = self.validate_concurrency(target_concurrent)
            if not concurrent_ok:
                return False, concurrent_msg
        
        return True, ""

