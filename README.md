# Custom URL Shortener Implementation

A pure Python implementation of a URL shortening service with no external dependencies. This implementation provides URL shortening, custom aliases, expiration, and analytics capabilities.

## Table of Contents
1. [Features](#features)
2. [System Design](#system-design)
3. [Data Structures](#data-structures)
4. [Installation](#installation)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Implementation Details](#implementation-details)
8. [Performance](#performance)
9. [Examples](#examples)
10. [Testing](#testing)

## Features

### Core Features
- Generate short URLs from long URLs
- Custom short code support
- URL expiration
- Visit tracking and analytics
- In-memory caching
- URL validation
- Collision handling

### Technical Features
- Pure Python implementation
- No external dependencies
- Thread-safe operations
- O(1) lookup time complexity
- Efficient Base62 encoding
- LRU caching

## System Design

### Components
1. **URLShortener**: Main class handling URL operations
2. **LRUCache**: Custom cache implementation
3. **URLDatabase**: In-memory database
4. **Node**: Doubly linked list node for LRU cache

### Design Decisions
- Base62 encoding for short codes (a-z, A-Z, 0-9)
- 7-character short codes (62^7 ≈ 3.5 trillion combinations)
- In-memory storage with LRU caching
- Custom URL validation

## Data Structures

### LRU Cache
```python
class LRUCache:
    - Dictionary for O(1) lookups
    - Doubly linked list for LRU tracking
    - Capacity limit for memory management
```

### URL Database
```python
class URLDatabase:
    - url_to_code: Dict[str, str]  # Long URL to short code
    - code_to_url: Dict[str, str]  # Short code to long URL
    - stats: Dict[str, Dict]       # URL statistics
```

## Installation

1. Copy the code into your project
2. No additional dependencies required
3. Minimum Python version: 3.6+

```python
# Import the main class
from url_shortener import URLShortener

# Create an instance
shortener = URLShortener(cache_size=1000)
```

## Usage

### Basic Usage
```python
# Create a shortener instance
shortener = URLShortener()

# Create a short URL
success, short_code = shortener.create_short_url("https://example.com/long/path")
if success:
    print(f"Short code: {short_code}")
else:
    print(f"Error: {short_code}")

# Retrieve original URL
success, long_url = shortener.get_long_url(short_code)
if success:
    print(f"Original URL: {long_url}")
```

### Custom Short Codes
```python
# Create URL with custom code
success, code = shortener.create_short_url(
    "https://example.com/path",
    custom_code="CUSTOM1"
)
```

### URL with Expiration
```python
# Create temporary URL (7 days)
success, code = shortener.create_short_url(
    "https://example.com/temporary",
    expiry_days=7
)
```

### Get URL Statistics
```python
success, stats = shortener.get_url_stats(short_code)
if success:
    print(f"Visit count: {stats['visit_count']}")
    print(f"Created at: {stats['created_at']}")
    print(f"Expires at: {stats['expires_at']}")
```

## API Reference

### URLShortener Class

#### Methods

1. `create_short_url(long_url, custom_code=None, expiry_days=None)`
   - Parameters:
     - `long_url`: Original URL to shorten
     - `custom_code`: Optional custom short code
     - `expiry_days`: Optional expiration in days
   - Returns: `Tuple[bool, str]`
     - Success status and short code/error message

2. `get_long_url(short_code)`
   - Parameters:
     - `short_code`: Short code to lookup
   - Returns: `Tuple[bool, str]`
     - Success status and long URL/error message

3. `get_url_stats(short_code)`
   - Parameters:
     - `short_code`: Short code to get stats for
   - Returns: `Tuple[bool, dict]`
     - Success status and statistics dictionary

## Implementation Details

### Short Code Generation
- Base62 encoding for numbers-to-letters conversion
- 7-character codes allowing 62^7 unique combinations
- Collision handling with counter-based generation

### Caching System
- LRU (Least Recently Used) cache
- Configurable cache size
- O(1) operations for get/put
- Automatic eviction of least used URLs

### URL Validation
```python
def _is_valid_url(self, url):
    # Length check
    if len(url) > 2048:
        return False
        
    # Protocol check
    if not url.startswith(('http://', 'https://')):
        return False
        
    # Domain validation
    parts = url.split('/')
    return len(parts) >= 3 and '.' in parts[2]
```

## Performance

### Time Complexity
- URL Creation: O(1)
- URL Lookup: O(1)
- Statistics Lookup: O(1)
- Cache Operations: O(1)

### Space Complexity
- URL Storage: O(n) where n is number of URLs
- Cache Storage: O(k) where k is cache size
- Statistics Storage: O(n)

## Examples

### Complete Usage Example
```python
def main():
    # Initialize shortener
    shortener = URLShortener(cache_size=1000)
    
    # Create short URL
    success, code = shortener.create_short_url(
        "https://example.com/very/long/path/that/needs/shortening"
    )
    print(f"Short code: {code}")
    
    # Create custom URL
    success, custom_code = shortener.create_short_url(
        "https://example.com/custom",
        custom_code="CUSTOM1"
    )
    print(f"Custom code: {custom_code}")
    
    # Create temporary URL
    success, temp_code = shortener.create_short_url(
        "https://example.com/temporary",
        expiry_days=7
    )
    print(f"Temporary code: {temp_code}")
    
    # Get URL stats
    success, stats = shortener.get_url_stats(code)
    print(f"URL Statistics: {stats}")

if __name__ == "__main__":
    main()
```

## Testing

### Manual Testing
```python
def test_shortener():
    shortener = URLShortener()
    
    # Test basic shortening
    success, code = shortener.create_short_url("https://example.com/test")
    assert success
    assert len(code) == 7
    
    # Test retrieval
    success, url = shortener.get_long_url(code)
    assert success
    assert url == "https://example.com/test"
    
    # Test custom code
    success, custom = shortener.create_short_url(
        "https://example.com/custom",
        custom_code="CUSTOM1"
    )
    assert success
    assert custom == "CUSTOM1"
```

### Edge Cases to Test
1. Invalid URLs
2. Expired URLs
3. Non-existent short codes
4. Custom code collisions
5. Cache eviction
6. URL length limits

## Recommendations
1. Add persistence layer for production use
2. Implement rate limiting for public access
3. Add URL sanitization
4. Implement backup/recovery mechanisms
5. Add monitoring and logging

## Limitations
1. In-memory storage (data lost on restart)
2. No built-in rate limiting
3. Single-instance only
4. No URL normalization

## Future Improvements
1. Add database persistence
2. Implement distributed architecture
3. Add rate limiting
4. Add URL normalization
5. Add API interface
6. Add monitoring and metrics
