# Testing Guide

## Test Framework

The project uses **pytest** with async support for comprehensive testing. Tests are organized into categories with specific markers for easy filtering.

## Quick Start

### Install Test Dependencies
```bash
pip install -e .[test]
```

### Run All Tests
```bash
python run_tests.py all
```

### Run Interactive Test Menu
```bash
python run_tests.py
```

## Test Categories

### Basic Functionality (`basic`)
- API connectivity
- Search function
- Get page function
- Error handling

### Canon Validation (`canon`)
- Character information accuracy
- Magic system validation
- Search result validation
- Canon framework testing

### Performance (`performance`)
- Response time validation
- Performance thresholds
- Concurrent request handling

### Integration (`integration`)
- Multi-function workflows
- End-to-end scenarios
- Concurrent operations

## Test Commands

| Command | Description |
|---------|-------------|
| `python run_tests.py all` | Run all tests |
| `python run_tests.py basic` | Run basic functionality tests |
| `python run_tests.py canon` | Run canon validation tests |
| `python run_tests.py performance` | Run performance tests |
| `python run_tests.py integration` | Run integration tests |
| `python run_tests.py quick` | Run quick tests (excludes slow tests) |
| `python run_tests.py coverage` | Run tests with coverage report |

## Direct pytest Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/ -m canon -v
pytest tests/ -m performance -v
pytest tests/ -m integration -v

# Run tests excluding slow ones
pytest tests/ -m "not slow" -v

# Run with coverage
pytest tests/ --cov=src/mediawiki_mcp_server --cov-report=html
```

## Test Markers

- `@pytest.mark.canon` - Canon validation tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (can be excluded)

## Canon Testing

The canon validation system uses fixtures with known Cosmere facts:

```python
@pytest.mark.canon
@pytest.mark.asyncio
async def test_kaladin_canon_accuracy(canon_validator):
    result = await get_page("Kaladin")
    validation = canon_validator.validate_character_info("Kaladin", result)
    assert validation["status"] == "valid"
```

## Adding New Tests

1. Create test functions in `tests/test_mcp_server.py`
2. Use appropriate markers (`@pytest.mark.canon`, etc.)
3. Add new canon facts to `tests/conftest.py` fixtures
4. Follow the naming convention: `test_*`

## Success Metrics

- **Canon Accuracy**: >95% on known facts
- **Response Time**: <2 seconds for typical queries
- **Coverage**: Aim for >90% code coverage
- **Reliability**: <1% error rate

## CI/CD Integration

Tests are configured for easy CI/CD integration:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -e .[test]
    pytest tests/ --cov=src/mediawiki_mcp_server --cov-report=xml
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `pip install -e .[test]` was run
2. **Network timeouts**: Check Coppermind.net connectivity
3. **Canon validation failures**: May indicate wiki content changes

### Debug Mode

```bash
pytest tests/ -v -s --tb=long
```

This enables verbose output, print statements, and detailed tracebacks. 