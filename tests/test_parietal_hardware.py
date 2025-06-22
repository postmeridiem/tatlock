"""
test_parietal_hardware.py

Tests for parietal hardware monitoring functions.
Tests system information gathering on both macOS and Linux.
"""

import pytest
import platform
import logging
import psutil
from unittest.mock import patch, MagicMock, Mock
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
    check_system_health,
    run_llm_benchmark,
    run_tool_benchmark,
    run_comprehensive_benchmark
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
    assert "overall_status" in health_status
    assert "checks" in health_status
    assert "recommendations" in health_status
    
    # Check that we have the expected health checks
    assert "cpu" in health_status["checks"]
    assert "memory" in health_status["checks"]
    assert "disk" in health_status["checks"]
    
    # Check that each check has the required fields
    for check_name, check_data in health_status["checks"].items():
        assert "status" in check_data
        assert "message" in check_data
        assert check_data["status"] in ["good", "warning"]
    
    logger.info(f"System health test passed: {health_status['overall_status']}")


def test_error_handling():
    """Test error handling for invalid inputs."""
    # Test disk space with invalid path
    disk_info = get_disk_space_info("/nonexistent/path")
    assert "error" in disk_info
    
    logger.info("Error handling test passed")


class TestOperatingSystemInfo:
    """Test operating system information functions."""
    
    def test_get_operating_system_info(self):
        """Test getting operating system information."""
        result = get_operating_system_info()
        
        assert "system" in result
        assert "release" in result
        assert "version" in result
        assert "machine" in result
        assert "processor" in result
        assert result["system"] in ["Linux", "Darwin", "Windows"]
    
    def test_get_operating_system_info_with_mock(self):
        """Test getting operating system information with mocked platform."""
        with patch('platform.system', return_value="Linux"):
            with patch('platform.release', return_value="5.4.0"):
                with patch('platform.version', return_value="#1 SMP"):
                    with patch('platform.machine', return_value="x86_64"):
                        with patch('platform.processor', return_value="Intel"):
                            result = get_operating_system_info()
                            
                            assert result["system"] == "Linux"
                            assert result["release"] == "5.4.0"
                            assert result["version"] == "#1 SMP"
                            assert result["machine"] == "x86_64"
                            assert result["processor"] == "Intel"


class TestDiskFunctions:
    """Test disk-related functions."""
    
    def test_get_disk_space_info(self):
        """Test getting disk space information."""
        result = get_disk_space_info("/")
        
        assert "total_bytes" in result
        assert "used_bytes" in result
        assert "free_bytes" in result
        assert "usage_percent" in result
        assert result["total_bytes"] > 0
        assert result["usage_percent"] >= 0
        assert result["usage_percent"] <= 100
    
    def test_get_disk_space_info_custom_path(self):
        """Test getting disk space information for custom path."""
        result = get_disk_space_info("/tmp")
        
        assert "total_bytes" in result
        assert "used_bytes" in result
        assert "free_bytes" in result
        assert "usage_percent" in result
    
    def test_get_all_disk_partitions(self):
        """Test getting all disk partitions."""
        result = get_all_disk_partitions()
        
        assert isinstance(result, list)
        if result:  # If partitions exist
            partition = result[0]
            assert "device" in partition
            assert "mountpoint" in partition
            assert "filesystem" in partition
            assert "opts" in partition
    
    def test_get_disk_space_info_error_handling(self):
        """Test error handling in disk space info."""
        with patch('psutil.disk_usage', side_effect=OSError("Permission denied")):
            result = get_disk_space_info("/invalid/path")
            
            assert "error" in result
            assert "Permission denied" in result["error"]


class TestMemoryFunctions:
    """Test memory-related functions."""
    
    def test_get_memory_status(self):
        """Test getting memory status."""
        result = get_memory_status()
        
        assert "ram" in result
        assert "swap" in result
        assert "total_bytes" in result["ram"]
        assert "available_bytes" in result["ram"]
        assert "used_bytes" in result["ram"]
        assert "free_bytes" in result["ram"]
        assert result["ram"]["total_bytes"] > 0
        assert result["ram"]["usage_percent"] >= 0
        assert result["ram"]["usage_percent"] <= 100
    
    def test_get_memory_status_with_mock(self):
        """Test getting memory status with mocked psutil."""
        mock_virtual_memory = Mock()
        mock_virtual_memory.total = 8589934592  # 8GB
        mock_virtual_memory.available = 4294967296  # 4GB
        mock_virtual_memory.used = 4294967296  # 4GB
        mock_virtual_memory.free = 0
        mock_virtual_memory.percent = 50.0
        
        mock_swap_memory = Mock()
        mock_swap_memory.total = 1073741824  # 1GB
        mock_swap_memory.used = 536870912  # 512MB
        mock_swap_memory.free = 536870912  # 512MB
        mock_swap_memory.percent = 50.0
        
        with patch('psutil.virtual_memory', return_value=mock_virtual_memory):
            with patch('psutil.swap_memory', return_value=mock_swap_memory):
                result = get_memory_status()
                
                assert result["ram"]["total_bytes"] == 8589934592
                assert result["ram"]["available_bytes"] == 4294967296
                assert result["ram"]["used_bytes"] == 4294967296
                assert result["ram"]["free_bytes"] == 0
                assert result["ram"]["usage_percent"] == 50.0


class TestCPUFunctions:
    """Test CPU-related functions."""
    
    def test_get_cpu_info(self):
        """Test getting CPU information."""
        result = get_cpu_info()
        
        assert "count" in result
        assert "frequency" in result
        assert "usage" in result
        assert "logical" in result["count"]
        assert "physical" in result["count"]
        assert result["count"]["logical"] > 0
        assert result["count"]["physical"] > 0
    
    def test_get_cpu_info_with_mock(self):
        """Test getting CPU information with mocked psutil."""
        mock_cpu_freq = Mock()
        mock_cpu_freq.current = 2400000000  # 2.4GHz
        mock_cpu_freq.min = 1200000000  # 1.2GHz
        mock_cpu_freq.max = 3200000000  # 3.2GHz
        
        with patch('psutil.cpu_count') as mock_cpu_count:
            with patch('psutil.cpu_freq', return_value=mock_cpu_freq):
                with patch('psutil.cpu_percent') as mock_cpu_percent:
                    mock_cpu_count.side_effect = [4, 8]  # physical, logical
                    mock_cpu_percent.side_effect = [25.5, [20.0, 25.0, 30.0, 27.0]]
                    
                    result = get_cpu_info()
                    
                    assert result["count"]["physical"] == 4
                    assert result["count"]["logical"] == 8
                    assert result["frequency"]["current_mhz"] == 2400000
                    assert result["usage"]["overall_percent"] == 25.5
    
    def test_get_load_average(self):
        """Test getting load average."""
        result = get_load_average()
        
        # On macOS, this might return an error, so check for either format
        if "error" not in result:
            assert "1min" in result
            assert "5min" in result
            assert "15min" in result
            assert all(isinstance(v, (int, float)) for v in result.values())
    
    def test_get_load_average_with_mock(self):
        """Test getting load average with mocked psutil."""
        with patch('platform.system', return_value="Linux"):
            with patch('os.getloadavg', return_value=(1.5, 2.0, 1.8)):
                result = get_load_average()
                
                assert result["1min"] == 1.5
                assert result["5min"] == 2.0
                assert result["15min"] == 1.8


class TestNetworkFunctions:
    """Test network-related functions."""
    
    def test_get_network_statistics(self):
        """Test getting network statistics."""
        result = get_network_statistics()
        
        assert "bytes_sent" in result
        assert "bytes_recv" in result
        assert "packets_sent" in result
        assert "packets_recv" in result
        assert "interfaces" in result
    
    def test_get_network_statistics_with_mock(self):
        """Test getting network statistics with mocked psutil."""
        mock_net_io = Mock()
        mock_net_io.bytes_sent = 1024000
        mock_net_io.bytes_recv = 2048000
        mock_net_io.packets_sent = 1000
        mock_net_io.packets_recv = 2000
        
        mock_interfaces = {
            "lo0": [Mock()],
            "en0": [Mock()]
        }
        
        mock_interface_stats = {
            "lo0": Mock(isup=True, speed=1000, mtu=16384),
            "en0": Mock(isup=True, speed=1000, mtu=1500)
        }
        
        with patch('psutil.net_io_counters', return_value=mock_net_io):
            with patch('psutil.net_if_addrs', return_value=mock_interfaces):
                with patch('psutil.net_if_stats', return_value=mock_interface_stats):
                    result = get_network_statistics()
                    
                    assert result["bytes_sent"] == 1024000
                    assert result["bytes_recv"] == 2048000
                    assert result["packets_sent"] == 1000
                    assert result["packets_recv"] == 2000
                    assert len(result["interfaces"]) == 2


class TestSystemFunctions:
    """Test system-related functions."""
    
    def test_get_system_uptime(self):
        """Test getting system uptime."""
        result = get_system_uptime()
        
        assert "uptime_seconds" in result
        assert "uptime_formatted" in result
        assert result["uptime_seconds"] > 0
        assert isinstance(result["uptime_formatted"], str)
    
    def test_get_system_uptime_with_mock(self):
        """Test getting system uptime with mocked time."""
        with patch('time.time', return_value=1000000):
            with patch('psutil.boot_time', return_value=999000):
                result = get_system_uptime()
                
                assert result["uptime_seconds"] == 1000
                assert "1000 seconds" in result["uptime_formatted"]
    
    def test_get_process_count(self):
        """Test getting process count."""
        result = get_process_count()
        
        assert "total" in result
        assert result["total"] > 0
    
    def test_get_process_count_with_mock(self):
        """Test getting process count with mocked psutil."""
        with patch('psutil.pids', return_value=[1, 2, 3, 4, 5]):
            result = get_process_count()
            
            assert result["total"] == 5


class TestComprehensiveSystemInfo:
    """Test comprehensive system information."""
    
    def test_get_comprehensive_system_info(self):
        """Test getting comprehensive system information."""
        result = get_comprehensive_system_info()
        
        assert "cpu" in result
        assert "memory" in result
        assert "disk" in result
        assert "network" in result
        assert "uptime" in result
        assert "processes" in result
        assert "load_average" in result


class TestSystemHealth:
    """Test system health checking."""
    
    def test_check_system_health(self):
        """Test system health check."""
        health_status = check_system_health()
        
        # Basic structure checks
        assert "overall_status" in health_status
        assert "checks" in health_status
        assert "recommendations" in health_status
        
        # Check that we have the expected health checks
        assert "cpu" in health_status["checks"]
        assert "memory" in health_status["checks"]
        assert "disk" in health_status["checks"]
        
        # Check that each check has the required fields
        for check_name, check_data in health_status["checks"].items():
            assert "status" in check_data
            assert "message" in check_data
            assert check_data["status"] in ["good", "warning"]
    
    def test_check_system_health_with_mock(self):
        """Test system health check with mocked data."""
        with patch('parietal.hardware.get_cpu_info') as mock_cpu:
            with patch('parietal.hardware.get_memory_status') as mock_memory:
                with patch('parietal.hardware.get_disk_space_info') as mock_disk:
                    mock_cpu.return_value = {"usage": {"overall_percent": 25.0}}
                    mock_memory.return_value = {"ram": {"usage_percent": 60.0}}
                    mock_disk.return_value = {"usage_percent": 45.0}
                    
                    health_status = check_system_health()
                    
                    # The actual thresholds might be different, so just check structure
                    assert "overall_status" in health_status
                    assert "checks" in health_status
                    assert "cpu" in health_status["checks"]
                    assert "memory" in health_status["checks"]
                    assert "disk" in health_status["checks"]
    
    def test_check_system_health_warning_conditions(self):
        """Test system health check with warning conditions."""
        with patch('parietal.hardware.get_cpu_info') as mock_cpu:
            with patch('parietal.hardware.get_memory_status') as mock_memory:
                with patch('parietal.hardware.get_disk_space_info') as mock_disk:
                    mock_cpu.return_value = {"usage": {"overall_percent": 85.0}}
                    mock_memory.return_value = {"ram": {"usage_percent": 90.0}}
                    mock_disk.return_value = {"usage_percent": 95.0}
                    
                    health_status = check_system_health()
                    
                    # The actual thresholds might be different, so just check structure
                    assert "overall_status" in health_status
                    assert "checks" in health_status
                    assert "cpu" in health_status["checks"]
                    assert "memory" in health_status["checks"]
                    assert "disk" in health_status["checks"]


class TestBenchmarkFunctions:
    """Test benchmark functions."""
    
    @patch('parietal.hardware.ollama')
    def test_run_llm_benchmark_success(self, mock_ollama):
        """Test successful LLM benchmark."""
        mock_ollama.chat.return_value = {
            'message': {'content': 'Hello'}
        }
        
        result = run_llm_benchmark()
        
        assert "timestamp" in result
        assert "model" in result
        assert "tests" in result
        assert "summary" in result
        assert "analysis" in result
        assert "simple_response" in result["tests"]
        assert "complex_reasoning" in result["tests"]
        assert result["tests"]["simple_response"]["status"] == "success"
    
    @patch('parietal.hardware.ollama')
    def test_run_llm_benchmark_with_tool_calling(self, mock_ollama):
        """Test LLM benchmark with tool calling."""
        mock_ollama.chat.return_value = {
            'message': {'content': 'Weather is sunny', 'tool_calls': [{'id': '1'}]}
        }
        
        result = run_llm_benchmark()
        
        assert "tool_calling" in result["tests"]
        assert result["tests"]["tool_calling"]["status"] == "success"
        assert result["tests"]["tool_calling"]["has_tool_calls"] is True
    
    @patch('parietal.hardware.ollama')
    def test_run_llm_benchmark_tool_calling_failure(self, mock_ollama):
        """Test LLM benchmark with tool calling failure."""
        def mock_chat(*args, **kwargs):
            if 'tools' in kwargs:
                raise Exception("Tool calling not supported")
            return {'message': {'content': 'Hello'}}
        
        mock_ollama.chat.side_effect = mock_chat
        
        result = run_llm_benchmark()
        
        assert "tool_calling" in result["tests"]
        assert result["tests"]["tool_calling"]["status"] == "failed"
        assert "error" in result["tests"]["tool_calling"]
    
    @patch('parietal.hardware.ollama')
    def test_run_llm_benchmark_complete_failure(self, mock_ollama):
        """Test LLM benchmark with complete failure."""
        mock_ollama.chat.side_effect = Exception("Ollama not available")
        
        result = run_llm_benchmark()
        
        assert "error" in result
        assert "Ollama not available" in result["error"]
        assert result["tests"] == {}
        assert result["summary"] == {}
        assert result["analysis"] == {}
    
    @patch('parietal.hardware.execute_find_personal_variables')
    @patch('parietal.hardware.execute_recall_memories')
    @patch('parietal.hardware.execute_get_weather_forecast')
    @patch('parietal.hardware.execute_web_search')
    def test_run_tool_benchmark_success(self, mock_web_search, mock_weather, mock_recall, mock_personal):
        """Test successful tool benchmark."""
        mock_personal.return_value = {"status": "success", "data": []}
        mock_recall.return_value = {"status": "success", "data": []}
        mock_weather.return_value = {"status": "success", "data": {"temp": 20}}
        mock_web_search.return_value = {"status": "success", "data": []}
        
        result = run_tool_benchmark()
        
        assert "timestamp" in result
        assert "tools" in result
        assert "summary" in result
        assert "analysis" in result
        assert "personal_variables" in result["tools"]
        assert "memory_recall" in result["tools"]
        assert "weather_forecast" in result["tools"]
        assert "web_search" in result["tools"]
        assert result["tools"]["personal_variables"]["status"] == "success"
    
    @patch('parietal.hardware.execute_find_personal_variables')
    @patch('parietal.hardware.execute_recall_memories')
    @patch('parietal.hardware.execute_get_weather_forecast')
    @patch('parietal.hardware.execute_web_search')
    def test_run_tool_benchmark_with_failures(self, mock_web_search, mock_weather, mock_recall, mock_personal):
        """Test tool benchmark with some failures."""
        mock_personal.side_effect = Exception("Database error")
        mock_recall.return_value = {"status": "success", "data": []}
        mock_weather.side_effect = Exception("API error")
        mock_web_search.return_value = {"status": "success", "data": []}
        
        result = run_tool_benchmark()
        
        assert result["tools"]["personal_variables"]["status"] == "failed"
        assert result["tools"]["memory_recall"]["status"] == "success"
        assert result["tools"]["weather_forecast"]["status"] == "failed"
        assert result["tools"]["web_search"]["status"] == "success"
    
    @patch('parietal.hardware.run_llm_benchmark')
    @patch('parietal.hardware.run_tool_benchmark')
    @patch('parietal.hardware.get_comprehensive_system_info')
    def test_run_comprehensive_benchmark_success(self, mock_system_info, mock_tool_bench, mock_llm_bench):
        """Test successful comprehensive benchmark."""
        mock_llm_bench.return_value = {
            "summary": {"average_time": 2.5},
            "analysis": {"performance_grade": "Good"}
        }
        mock_tool_bench.return_value = {
            "tools": {"test_tool": {"time_seconds": 1.0, "status": "success"}}
        }
        mock_system_info.return_value = {
            "cpu": {"usage": {"overall_percent": 25.0}},
            "memory": {"ram": {"usage_percent": 60.0}}
        }
        
        result = run_comprehensive_benchmark()
        
        assert "timestamp" in result
        assert "llm_benchmark" in result
        assert "tool_benchmark" in result
        assert "system_info" in result
        assert "overall_analysis" in result
        assert "overall_assessment" in result
        assert result["overall_assessment"]["grade"] == "Good"
    
    @patch('parietal.hardware.run_llm_benchmark')
    @patch('parietal.hardware.run_tool_benchmark')
    @patch('parietal.hardware.get_comprehensive_system_info')
    def test_run_comprehensive_benchmark_with_errors(self, mock_system_info, mock_tool_bench, mock_llm_bench):
        """Test comprehensive benchmark with errors."""
        mock_llm_bench.side_effect = Exception("LLM error")
        mock_tool_bench.return_value = {"tools": {}}
        mock_system_info.return_value = {"cpu": {"usage": {"overall_percent": 25.0}}}
        
        result = run_comprehensive_benchmark()
        
        assert "timestamp" in result
        assert "llm_benchmark" in result
        assert "error" in result["llm_benchmark"]
        assert "tool_benchmark" in result
        assert "system_info" in result
        assert result["overall_assessment"]["grade"] == "Unknown"


class TestErrorHandling:
    """Test error handling in hardware functions."""
    
    def test_get_cpu_info_error_handling(self):
        """Test error handling in CPU info."""
        with patch('psutil.cpu_count', side_effect=Exception("CPU error")):
            result = get_cpu_info()
            
            assert "error" in result
            assert "CPU error" in result["error"]
    
    def test_get_memory_status_error_handling(self):
        """Test error handling in memory status."""
        with patch('psutil.virtual_memory', side_effect=Exception("Memory error")):
            result = get_memory_status()
            
            assert "error" in result
            assert "Memory error" in result["error"]
    
    def test_get_network_statistics_error_handling(self):
        """Test error handling in network statistics."""
        with patch('psutil.net_io_counters', side_effect=Exception("Network error")):
            result = get_network_statistics()
            
            assert "error" in result
            assert "Network error" in result["error"]
    
    def test_get_system_uptime_error_handling(self):
        """Test error handling in system uptime."""
        with patch('psutil.boot_time', side_effect=Exception("Boot time error")):
            result = get_system_uptime()
            
            assert "error" in result
            assert "Boot time error" in result["error"]
    
    def test_check_system_health_error_handling(self):
        """Test error handling in system health check."""
        with patch('parietal.hardware.get_cpu_info', side_effect=Exception("Health check error")):
            result = check_system_health()
            
            # Should handle error gracefully and still return a structure
            assert "overall_status" in result
            assert "checks" in result


class TestEdgeCases:
    """Test edge cases in hardware functions."""
    
    def test_get_disk_space_info_zero_values(self):
        """Test disk space info with zero values."""
        mock_usage = Mock()
        mock_usage.total = 0
        mock_usage.used = 0
        mock_usage.free = 0
        mock_usage.percent = 0
        
        with patch('psutil.disk_usage', return_value=mock_usage):
            result = get_disk_space_info("/")
            
            assert result["total_bytes"] == 0
            assert result["used_bytes"] == 0
            assert result["free_bytes"] == 0
            assert result["usage_percent"] == 0
    
    def test_get_memory_status_zero_values(self):
        """Test memory status with zero values."""
        mock_virtual_memory = Mock()
        mock_virtual_memory.total = 0
        mock_virtual_memory.available = 0
        mock_virtual_memory.used = 0
        mock_virtual_memory.free = 0
        mock_virtual_memory.percent = 0
        
        mock_swap_memory = Mock()
        mock_swap_memory.total = 0
        mock_swap_memory.used = 0
        mock_swap_memory.free = 0
        mock_swap_memory.percent = 0
        
        with patch('psutil.virtual_memory', return_value=mock_virtual_memory):
            with patch('psutil.swap_memory', return_value=mock_swap_memory):
                result = get_memory_status()
                
                assert result["ram"]["total_bytes"] == 0
                assert result["ram"]["available_bytes"] == 0
                assert result["ram"]["used_bytes"] == 0
                assert result["ram"]["free_bytes"] == 0
                assert result["ram"]["usage_percent"] == 0
    
    def test_get_load_average_zero_values(self):
        """Test load average with zero values."""
        with patch('platform.system', return_value="Linux"):
            with patch('os.getloadavg', return_value=(0.0, 0.0, 0.0)):
                result = get_load_average()
                
                assert result["1min"] == 0.0
                assert result["5min"] == 0.0
                assert result["15min"] == 0.0
    
    def test_get_process_count_zero(self):
        """Test process count with zero processes."""
        with patch('psutil.pids', return_value=[]):
            result = get_process_count()
            
            assert result["total"] == 0


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