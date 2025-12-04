"""Tests for automation.docker.utils module."""

from unittest.mock import patch

from automation.docker.utils import execute_docker_build


def test_execute_docker_build_single_platform():
    """Test that single platform builds use regular docker build."""
    with patch("automation.docker.utils.subprocess.call") as mock_call:
        mock_call.return_value = 0

        execute_docker_build(
            image="test-image:latest",
            docker_args={"ARG1": "value1"},
            platform="linux/amd64",
        )

        # Verify it uses regular docker build (not buildx)
        args = mock_call.call_args[0][0]
        assert args[0:3] == ["docker", "build", "."]
        assert "--platform" in args
        assert "linux/amd64" in args
        assert "--build-arg" in args
        assert "ARG1=value1" in args


def test_execute_docker_build_multi_platform():
    """Test that multi-platform builds use docker buildx."""
    with patch("automation.docker.utils.subprocess.call") as mock_call:
        mock_call.return_value = 0

        execute_docker_build(
            image="test-image:latest",
            docker_args={"ARG1": "value1"},
            platform="linux/amd64,linux/arm64",
            push=True,
        )

        # Verify it uses buildx
        args = mock_call.call_args[0][0]
        assert args[0:4] == ["docker", "buildx", "build", "."]
        assert "--platform" in args
        assert "linux/amd64,linux/arm64" in args
        assert "--push" in args


def test_execute_docker_build_no_platform():
    """Test that builds without platform use regular docker build."""
    with patch("automation.docker.utils.subprocess.call") as mock_call:
        mock_call.return_value = 0

        execute_docker_build(
            image="test-image:latest",
            docker_args={"ARG1": "value1"},
        )

        # Verify it uses regular docker build (not buildx)
        args = mock_call.call_args[0][0]
        assert args[0:3] == ["docker", "build", "."]
        assert "--platform" not in args
