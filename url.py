class Node:
    """Node for doubly linked list used in LRU Cache"""
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    """Custom LRU Cache implementation using doubly linked list and dictionary"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # Hash map for O(1) lookups
        self.head = Node()  # Dummy head
        self.tail = Node()  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head
        
    def _remove(self, node):
        """Remove node from linked list"""
        node.prev.next = node.next
        node.next.prev = node.prev
        
    def _add(self, node):
        """Add node right after head"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        
    def get(self, key):
        """Get value from cache and move to front"""
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add(node)
            return node.value
        return None
        
    def put(self, key, value):
        """Put value in cache"""
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self._add(node)
        self.cache[key] = node
        if len(self.cache) > self.capacity:
            # Remove from tail
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]

class URLDatabase:
    """In-memory database implementation"""
    def __init__(self):
        self.url_to_code = {}  # Long URL to short code mapping
        self.code_to_url = {}  # Short code to URL mapping
        self.stats = {}        # Statistics for each URL
        self.counter = 0       # Counter for generating unique codes
        
    def store(self, short_code, long_url, expiry=None):
        """Store URL mapping"""
        self.url_to_code[long_url] = short_code
        self.code_to_url[short_code] = long_url
        self.stats[short_code] = {
            'created_at': self._current_timestamp(),
            'expires_at': expiry,
            'visit_count': 0
        }
        
    def get_url(self, short_code):
        """Get long URL from short code"""
        return self.code_to_url.get(short_code)
        
    def get_code(self, long_url):
        """Get short code from long URL"""
        return self.url_to_code.get(long_url)
        
    def increment_visits(self, short_code):
        """Increment visit count for URL"""
        if short_code in self.stats:
            self.stats[short_code]['visit_count'] += 1
            
    def get_stats(self, short_code):
        """Get statistics for URL"""
        return self.stats.get(short_code)
        
    def _current_timestamp(self):
        """Get current timestamp in seconds"""
        import time
        return int(time.time())

class URLShortener:
    """Main URL shortener implementation"""
    def __init__(self, cache_size=1000):
        self.db = URLDatabase()
        self.cache = LRUCache(cache_size)
        self.charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
    def create_short_url(self, long_url, custom_code=None, expiry_days=None):
        """Create short URL from long URL"""
        # Validate URL
        if not self._is_valid_url(long_url):
            return False, "Invalid URL format"
            
        # Check if URL already exists
        existing_code = self.db.get_code(long_url)
        if existing_code:
            return True, existing_code
            
        # Generate or validate short code
        if custom_code:
            if not self._is_valid_code(custom_code):
                return False, "Invalid custom code"
            if self.db.get_url(custom_code):
                return False, "Custom code already in use"
            short_code = custom_code
        else:
            short_code = self._generate_code()
            
        # Calculate expiry time
        expiry = None
        if expiry_days:
            import time
            expiry = int(time.time()) + (expiry_days * 24 * 60 * 60)
            
        # Store URL
        self.db.store(short_code, long_url, expiry)
        self.cache.put(short_code, long_url)
        
        return True, short_code
        
    def get_long_url(self, short_code):
        """Get original URL from short code"""
        # Check cache first
        cached_url = self.cache.get(short_code)
        if cached_url:
            self.db.increment_visits(short_code)
            return True, cached_url
            
        # Check database
        long_url = self.db.get_url(short_code)
        if not long_url:
            return False, "URL not found"
            
        # Check expiration
        stats = self.db.get_stats(short_code)
        if stats['expires_at'] and stats['expires_at'] < self._current_timestamp():
            return False, "URL has expired"
            
        # Update statistics and cache
        self.db.increment_visits(short_code)
        self.cache.put(short_code, long_url)
        
        return True, long_url
        
    def get_url_stats(self, short_code):
        """Get statistics for URL"""
        stats = self.db.get_stats(short_code)
        if not stats:
            return False, "URL not found"
        return True, stats
        
    def _generate_code(self, length=7):
        """Generate unique short code"""
        import random
        while True:
            self.db.counter += 1
            num = self.db.counter
            code = self._encode_base62(num).rjust(length, '0')
            if not self.db.get_url(code):
                return code
                
    def _encode_base62(self, num):
        """Encode number to base62 string"""
        if num == 0:
            return self.charset[0]
            
        result = []
        base = len(self.charset)
        while num:
            num, rem = divmod(num, base)
            result.append(self.charset[rem])
        return ''.join(reversed(result))
        
    def _is_valid_url(self, url):
        """Validate URL format"""
        # Basic URL validation
        if len(url) > 2048:
            return False
            
        # Check for scheme and netloc
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Basic domain validation
        parts = url.split('/')
        if len(parts) < 3:
            return False
            
        domain = parts[2]
        if not '.' in domain:
            return False
            
        return True
        
    def _is_valid_code(self, code):
        """Validate custom short code"""
        if len(code) != 7:
            return False
            
        return all(c in self.charset for c in code)
        
    def _current_timestamp(self):
        """Get current timestamp"""
        import time
        return int(time.time())

# Example usage
def main():
    # Create URL shortener instance
    shortener = URLShortener(cache_size=1000)
    
    # Test 1: Create short URL
    print("Test 1: Creating short URL")
    long_url = "https://example.com/very/long/path"
    success, result = shortener.create_short_url(long_url)
    print(f"Success: {success}, Result: {result}")
    
    # Test 2.1: Create custom URL
    print("\nTest 2.1: Creating custom URL")
    success, result = shortener.create_short_url(
        "https://example.com/custom",
        custom_code="CUSTOM1"
    )
    print(f"Success: {success}, Result: {result}")
    # Test 2.2: Create custom URL
    print("\nTest 2.2: Creating custom URL")
    success, result = shortener.create_short_url(
        "https://example.com/custom3",
        custom_code="CUSTOM1"
    )
    print(f"Success: {success}, Result: {result}")
    # Test 3: Create temporary URL
    print("\nTest 3: Creating temporary URL")
    success, result = shortener.create_short_url(
        "https://example.com/temporary",
        expiry_days=7
    )
    print(f"Success: {success}, Result: {result}")
    
    # Test 4: Retrieve URL
    print("\nTest 4: Retrieving URL")
    success, long_url = shortener.get_long_url("0000002")
    print(f"Success: {success}, URL: {long_url}")
    
    # Test 4: Retrieve URL
    print("\nTest 5: Retrieving URL")
    success, long_url = shortener.get_long_url("00020002")
    print(f"Success: {success}, URL: {long_url}")
    
    # Test 5: Get statistics
    print("\nTest 6: Getting statistics")
    success, stats = shortener.get_url_stats(result)
    print(f"Success: {success}")
    print("Statistics:", stats)

if __name__ == "__main__":
    main()
