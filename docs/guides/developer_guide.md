# Developer Guide

## Architecture Overview
EpochCore RAS uses a modular architecture with recursive improvement capabilities.

## Adding New Engines
1. Inherit from RecursiveEngine base class
2. Implement required methods
3. Register with orchestrator
4. Add tests

## Configuration Management
All configuration is stored in YAML files in the `config/` directory.

## Testing
Run tests with:
```bash
python -m unittest discover tests/
pytest --cov=.
```

## Debugging
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python integration.py status
```

## Performance Optimization
- Monitor resource usage
- Profile code execution
- Optimize recursive algorithms
- Use caching where appropriate
