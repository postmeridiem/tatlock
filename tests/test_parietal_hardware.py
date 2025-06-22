"""
test_parietal_hardware.py

Tests for parietal hardware monitoring functions.
Tests system information gathering on both macOS and Linux.
"""

import pytest
import platform
import logging
from parietal.hardware import (
    get_operating_system_info,
    get_disk_space_info,
    get_all_disk_partitions,
    get_memory_status,
    get_cpu_info,
    get_load_average,
    get_network_statistics,
    get_system_uptime,
    get_process_count,
    get_comprehensive_system_info,
    check_system_health
)

# Set up logging for this module
logger = logging.getLogger(__name__)


def test_get_operating_system_info():
    """Test operating system information retrieval."""
    os_info = get_operating_system_info()
    
    # Basic checks
    assert "system" in os_info
    assert "release" in os_info
    assert "version" in os_info
    assert "machine" in os_info
    assert "architecture" in os_info
    assert "python_version" in os_info
    
    # OS-specific checks
    if platform.system() == "Darwin":  # macOS
        assert os_info["os_type"] == "macOS"
        assert "macos_version" in os_info
        assert "macos_product" in os_info
    elif platform.system() == "Linux":
        assert os_info["os_type"] == "Linux"
        # Linux distribution info may or may not be available
        if "linux_distribution" in os_info:
            assert isinstance(os_info["linux_distribution"], str)
    
    logger.info(f"OS info test passed: {os_info['os_type']}")


def test_get_disk_space_info():
    """Test disk space information retrieval."""
    disk_info = get_disk_space_info("/")
    
    # Basic checks
    assert "path" in disk_info
    assert "total_bytes" in disk_info
    assert "used_bytes" in disk_info
    assert "free_bytes" in disk_info
    assert "total_gb" in disk_info
    assert "used_gb" in disk_info
    assert "free_gb" in disk_info
    assert "usage_percent" in disk_info
    
    # Value checks
    assert disk_info["path"] == "/"
    assert disk_info["total_bytes"] > 0
    assert disk_info["used_bytes"] >= 0
    assert disk_info["free_bytes"] >= 0
    assert 0 <= disk_info["usage_percent"] <= 100
    assert disk_info["total_gb"] > 0
    
    logger.info(f"Disk space test passed: {disk_info['usage_percent']}% used")


def test_get_all_disk_partitions():
    """Test disk partition information retrieval."""
    partitions = get_all_disk_partitions()
    
    # Should return a list
    assert isinstance(partitions, list)
    
    # Each partition should have basic info
    for partition in partitions:
        assert "device" in partition
        assert "mountpoint" in partition
        assert "filesystem" in partition
        
        # If partition is mounted, should have usage info
        if partition.get("total_gb") is not None:
            assert "used_gb" in partition
            assert "free_gb" in partition
            assert "usage_percent" in partition
    
    logger.info(f"Disk partitions test passed: {len(partitions)} partitions found")


def test_get_memory_status():
    """Test memory status retrieval."""
    memory_info = get_memory_status()
    
    # Basic structure checks
    assert "ram" in memory_info
    assert "swap" in memory_info
    
    # RAM checks
    ram = memory_info["ram"]
    assert "total_bytes" in ram
    assert "available_bytes" in ram
    assert "used_bytes" in ram
    assert "free_bytes" in ram
    assert "total_gb" in ram
    assert "usage_percent" in ram
    
    # Value checks
    assert ram["total_bytes"] > 0
    assert ram["available_bytes"] >= 0
    assert ram["used_bytes"] >= 0
    assert ram["free_bytes"] >= 0
    assert 0 <= ram["usage_percent"] <= 100
    assert ram["total_gb"] > 0
    
    # Swap checks
    swap = memory_info["swap"]
    assert "total_bytes" in swap
    assert "used_bytes" in swap
    assert "free_bytes" in swap
    assert "usage_percent" in swap
    
    logger.info(f"Memory test passed: RAM {ram['usage_percent']}% used")


def test_get_cpu_info():
    """Test CPU information retrieval."""
    cpu_info = get_cpu_info()
    
    # Basic structure checks
    assert "count" in cpu_info
    assert "usage" in cpu_info
    assert "load_average" in cpu_info
    
    # CPU count checks
    count = cpu_info["count"]
    assert "physical" in count
    assert "logical" in count
    assert count["physical"] > 0
    assert count["logical"] >= count["physical"]
    
    # CPU usage checks
    usage = cpu_info["usage"]
    assert "overall_percent" in usage
    assert "per_core_percent" in usage
    assert 0 <= usage["overall_percent"] <= 100
    assert len(usage["per_core_percent"]) == count["logical"]
    
    # Load average checks
    load_avg = cpu_info["load_average"]
    if "error" not in load_avg:
        assert "1min" in load_avg
        assert "5min" in load_avg
        assert "15min" in load_avg
    
    logger.info(f"CPU test passed: {count['logical']} cores, {usage['overall_percent']}% usage")


def test_get_load_average():
    """Test load average retrieval."""
    load_avg = get_load_average()
    
    if "error" not in load_avg:
        assert "1min" in load_avg
        assert "5min" in load_avg
        assert "15min" in load_avg
        assert load_avg["1min"] >= 0
        assert load_avg["5min"] >= 0
        assert load_avg["15min"] >= 0
    
    logger.info(f"Load average test passed: {load_avg}")


def test_get_network_statistics():
    """Test network statistics retrieval."""
    network_info = get_network_statistics()
    
    # Basic checks
    assert "bytes_sent" in network_info
    assert "bytes_recv" in network_info
    assert "packets_sent" in network_info
    assert "packets_recv" in network_info
    assert "interfaces" in network_info
    
    # Value checks
    assert network_info["bytes_sent"] >= 0
    assert network_info["bytes_recv"] >= 0
    assert network_info["packets_sent"] >= 0
    assert network_info["packets_recv"] >= 0
    assert isinstance(network_info["interfaces"], list)
    
    # Interface checks
    for interface in network_info["interfaces"]:
        assert "name" in interface
        assert "addresses" in interface
        assert isinstance(interface["addresses"], list)
    
    logger.info(f"Network test passed: {len(network_info['interfaces'])} interfaces")


def test_get_system_uptime():
    """Test system uptime retrieval."""
    uptime_info = get_system_uptime()
    
    # Basic checks
    assert "boot_time" in uptime_info
    assert "uptime_seconds" in uptime_info
    assert "uptime_formatted" in uptime_info
    assert "days" in uptime_info
    assert "hours" in uptime_info
    assert "minutes" in uptime_info
    assert "seconds" in uptime_info
    
    # Value checks
    assert uptime_info["uptime_seconds"] > 0
    assert uptime_info["days"] >= 0
    assert uptime_info["hours"] >= 0
    assert uptime_info["minutes"] >= 0
    assert uptime_info["seconds"] >= 0
    
    logger.info(f"Uptime test passed: {uptime_info['uptime_formatted']}")


def test_get_process_count():
    """Test process count retrieval."""
    process_info = get_process_count()
    
    # Basic checks
    assert "total" in process_info
    assert "running" in process_info
    assert "sleeping" in process_info
    assert "stopped" in process_info
    assert "zombie" in process_info
    
    # Value checks
    assert process_info["total"] > 0
    assert process_info["running"] >= 0
    assert process_info["sleeping"] >= 0
    assert process_info["stopped"] >= 0
    assert process_info["zombie"] >= 0
    
    # Sum of known states should not exceed total
    total_calculated = (process_info["running"] + process_info["sleeping"] + 
                       process_info["stopped"] + process_info["zombie"])
    assert total_calculated <= process_info["total"]
    logger.info(f"Process count test passed: {process_info['total']} total processes, {total_calculated} in known states, {process_info['total']-total_calculated} in other states")


def test_get_comprehensive_system_info():
    """Test comprehensive system information retrieval."""
    system_info = get_comprehensive_system_info()
    
    # Basic structure checks
    assert "timestamp" in system_info
    assert "operating_system" in system_info
    assert "cpu" in system_info
    assert "memory" in system_info
    assert "disk" in system_info
    assert "network" in system_info
    assert "uptime" in system_info
    assert "processes" in system_info
    
    # Disk structure checks
    disk = system_info["disk"]
    assert "root_partition" in disk
    assert "all_partitions" in disk
    
    logger.info("Comprehensive system info test passed")


def test_check_system_health():
    """Test system health check."""
    health_status = check_system_health()
    
    # Basic structure checks
    assert "timestamp" in health_status
    assert "overall_status" in health_status
    assert "warnings" in health_status
    assert "recommendations" in health_status
    
    # Status should be one of the expected values
    assert health_status["overall_status"] in ["healthy", "warning", "critical"]
    
    # Lists should be lists
    assert isinstance(health_status["warnings"], list)
    assert isinstance(health_status["recommendations"], list)
    
    logger.info(f"System health test passed: {health_status['overall_status']}")


def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test disk space with invalid path
    disk_info = get_disk_space_info("/nonexistent/path")
    assert "error" in disk_info
    
    logger.info("Error handling test passed")


if __name__ == "__main__":
    # Run basic tests
    print("Running hardware monitoring tests...")
    
    try:
        test_get_operating_system_info()
        test_get_disk_space_info()
        test_get_memory_status()
        test_get_cpu_info()
        test_get_network_statistics()
        test_get_system_uptime()
        test_get_process_count()
        test_check_system_health()
        print("All basic tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc() 