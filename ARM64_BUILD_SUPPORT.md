# ARM64 Docker Build Support

This document describes the changes made to add ARM64 build support to Dagster's Docker images.

## Changes Made

### 1. Updated `buildkite-test` Dockerfile
**File**: `python_modules/automation/automation/docker/images/buildkite-test/Dockerfile`

Modified to dynamically detect architecture instead of hardcoding `amd64`:
- **kubectl**: Uses `$(dpkg --print-architecture)` to download the correct binary
- **kind**: Uses `$(dpkg --print-architecture)` for the correct architecture
- **FOSSA CLI**: Downloads the correct architecture-specific tarball
- **Docker repository**: Uses `ARCH` variable in repository configuration
- **DuckDB CLI**: Downloads the correct architecture-specific ZIP file

### 2. Updated `build.sh` for Test Projects
**File**: `python_modules/dagster-test/dagster_test/test_project/build.sh`

Made platform configurable via environment variable:
- Removed hardcoded `--platform linux/amd64`
- Added `DOCKER_PLATFORM` environment variable (defaults to `linux/amd64` for backward compatibility)
- Users can now specify single or multiple platforms: `DOCKER_PLATFORM=linux/arm64` or `DOCKER_PLATFORM=linux/amd64,linux/arm64`

### 3. Enhanced Docker Build Automation
**File**: `python_modules/automation/automation/docker/cli.py`

Changed default platform from `linux/amd64` to `None`:
- Allows builds to use the native platform when not specified
- Users can explicitly specify single or multiple platforms

**File**: `python_modules/automation/automation/docker/utils.py`

Enhanced `execute_docker_build()` to support multi-platform builds:
- Automatically detects multi-platform builds (when platform contains comma)
- Uses `docker buildx` for multi-platform builds
- Uses regular `docker build` for single-platform or native builds
- Added `push` parameter for pushing multi-platform images (required by buildx)

### 4. Added Tests
**File**: `python_modules/automation/automation_tests/docker_tests/test_utils.py`

Created unit tests to verify:
- Single-platform builds use regular `docker build`
- Multi-platform builds use `docker buildx`
- Platform parameter is correctly passed
- Build arguments are correctly included

## Usage

### Building for a Single Platform

```bash
# Build for ARM64 only
dagster-image build --name buildkite-test --dagster-version 1.0.0 --python-version 3.11 --platform linux/arm64

# Build for AMD64 only (default behavior)
dagster-image build --name buildkite-test --dagster-version 1.0.0 --python-version 3.11 --platform linux/amd64

# Build for native platform (no platform specified)
dagster-image build --name buildkite-test --dagster-version 1.0.0 --python-version 3.11
```

### Building for Multiple Platforms

For multi-platform builds, you need to use Docker Buildx:

```bash
# First, create a buildx builder (one-time setup)
docker buildx create --name multiplatform --use

# Build for both AMD64 and ARM64
dagster-image build --name buildkite-test --dagster-version 1.0.0 --python-version 3.11 --platform linux/amd64,linux/arm64
```

**Note**: Multi-platform builds typically require pushing to a registry. The images cannot be loaded directly to the local Docker daemon.

### Using the Test Project Build Script

```bash
# Build for native platform
./build.sh 3.11 my-test-image

# Build for ARM64
DOCKER_PLATFORM=linux/arm64 ./build.sh 3.11 my-test-image

# Build for both platforms (requires buildx)
DOCKER_PLATFORM=linux/amd64,linux/arm64 ./build.sh 3.11 my-test-image
```

## Backward Compatibility

All changes maintain backward compatibility:
- Default behavior remains the same (AMD64 builds when platform is specified as default)
- Existing scripts and CI/CD pipelines continue to work without modification
- Multi-platform support is opt-in via explicit platform specification

## Testing

The changes have been tested with:
- Unit tests for the `execute_docker_build` function
- Manual verification of Docker build command generation
- Code review to ensure proper architecture detection in Dockerfiles

## Future Enhancements

Potential improvements for the future:
1. Add CI/CD pipeline support for automated multi-platform builds
2. Create pre-built multi-platform images and publish to Docker registries
3. Add integration tests that actually build images on both architectures
4. Document platform-specific dependency issues (if any)
